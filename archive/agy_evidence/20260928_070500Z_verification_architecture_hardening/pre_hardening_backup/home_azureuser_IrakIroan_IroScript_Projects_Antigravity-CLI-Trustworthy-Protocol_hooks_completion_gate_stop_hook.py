#!/usr/bin/env python3
"""
Hardened Native AGY Completion Gate Stop Hook (v2.0)
Enforces:
1. Cryptographic HMAC-SHA256 signature verification on state
2. Timestamp freshness (<= 3600 seconds)
3. Workspace and target binding
4. Disk-level re-reading and SHA-256 integrity check of all target files
5. 10-level vector check (V1..V9 == PASS, V10 == VERIFIED_SUCCESS)
6. Fail-closed return on any controllable error condition
"""

import sys
import os
import json
import time
import hashlib
import hmac

STATE_FILE = os.environ.get("STATE_FILE_OVERRIDE", "/home/azureuser/.agents/verification_state.json")
KEY_FILE = os.environ.get("KEY_FILE_OVERRIDE", "/home/azureuser/.agents/.verification_secret.key")
INCIDENT_LOG = "/home/azureuser/.agents/completion_gate_attempts.jsonl"

def log_gate_event(decision, reason, details):
    try:
        os.makedirs(os.path.dirname(INCIDENT_LOG), exist_ok=True)
        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "decision": decision,
            "reason": reason,
            "details": details
        }
        with open(INCIDENT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass

def compute_state_hmac(key: bytes, state_dict: dict) -> str:
    clean = dict(state_dict)
    clean.pop("hmac_signature", None)
    canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def fail_closed(reason, details=None):
    log_gate_event("continue", reason, details or {})
    print(json.dumps({
        "decision": "continue",
        "reason": f"🛑 [STOP GATE FAIL-CLOSED]: {reason}"
    }))

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            # If nothing was provided on stdin, allow termination for standard no-op
            print(json.dumps({"decision": "allow"}))
            return
        payload = json.loads(raw)
    except Exception as e:
        fail_closed(f"Failed to parse Stop hook payload: {e}")
        return

    final_output = payload.get("finalModelOutput", "") or payload.get("error", "")

    # Look for explicit claims of completion or success
    completion_markers = [
        "VERIFIED_SUCCESS",
        "TASK COMPLETED",
        "IMPLEMENTED_AND_VERIFIED",
        "ALL TESTS PASSED",
        "10/10 PASS",
        "TASK IS DONE",
        "ALL 10 TESTS PASSED"
    ]
    
    claims_completion = any(marker.lower() in final_output.lower() for marker in completion_markers)

    if not claims_completion:
        # Conversational / informative turns not claiming completion are permitted
        print(json.dumps({"decision": "allow"}))
        return

    # 1. State file presence
    if not os.path.exists(STATE_FILE):
        fail_closed(
            f"You claimed completion, but NO machine verification record ({STATE_FILE}) exists. "
            "You MUST execute verify_10_fold.py to produce signed empirical evidence.",
            {"claimed_completion": True, "state_exists": False}
        )
        return

    # 2. Key file presence
    if not os.path.exists(KEY_FILE):
        fail_closed(
            f"HMAC secret key file ({KEY_FILE}) is missing. State authenticity cannot be verified.",
            {"claimed_completion": True, "key_exists": False}
        )
        return

    try:
        with open(KEY_FILE, "r", encoding="utf-8") as kf:
            key_bytes = kf.read().strip().encode("utf-8")
        if not key_bytes:
            fail_closed("HMAC secret key is empty.", {"key_empty": True})
            return
    except Exception as e:
        fail_closed(f"Failed to read HMAC key: {e}", {"error": str(e)})
        return

    # 3. Read and parse state JSON
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            v_state = json.load(f)
    except Exception as e:
        fail_closed(f"Verification state is unreadable or malformed JSON: {e}", {"error": str(e)})
        return

    # 4. Cryptographic HMAC signature check
    sig = v_state.get("hmac_signature", "")
    if not sig:
        fail_closed("Verification state has NO cryptographic HMAC signature (untrusted/forged).", {"hmac_present": False})
        return

    try:
        expected_sig = compute_state_hmac(key_bytes, v_state)
        if not hmac.compare_digest(sig, expected_sig):
            fail_closed(
                "HMAC signature verification FAILED. State has been tampered with post-verification.",
                {"sig_mismatch": True}
            )
            return
    except Exception as e:
        fail_closed(f"HMAC verification computation error: {e}", {"error": str(e)})
        return

    # 4b. Workspace binding validation
    ws_root = v_state.get("workspace_root", "")
    if not ws_root or not os.path.isdir(ws_root):
        fail_closed(f"Workspace root '{ws_root}' recorded in verification state does not exist or is invalid.", {"workspace_root": ws_root})
        return

    # 5. Timestamp freshness check (<= 3600 seconds)
    ts = v_state.get("timestamp", 0)
    current_time = time.time()
    if not isinstance(ts, (int, float)) or ts <= 0:
        fail_closed("Verification state has an invalid timestamp.", {"ts": ts})
        return

    if current_time - ts > 3600:
        fail_closed(
            f"Verification record is STALE ({int(current_time - ts)}s old > 3600s limit). Re-run verification.",
            {"age_seconds": current_time - ts}
        )
        return

    # 6. Target file integrity: re-read disk and recompute SHA-256 hashes
    file_hashes = v_state.get("file_hashes", {})
    if not isinstance(file_hashes, dict):
        fail_closed("Invalid file_hashes structure in state record.", {"file_hashes_type": str(type(file_hashes))})
        return

    for target_path, expected_hash in file_hashes.items():
        if not os.path.exists(target_path):
            fail_closed(f"Target file '{target_path}' recorded in state no longer exists on disk.", {"missing_file": target_path})
            return
        try:
            actual_disk_hash = sha256_file(target_path)
            if actual_disk_hash != expected_hash:
                fail_closed(
                    f"Target file '{target_path}' was TAMPERED on disk post-verification! "
                    f"Expected SHA: {expected_hash[:12]}..., Actual Disk SHA: {actual_disk_hash[:12]}...",
                    {"path": target_path, "expected": expected_hash, "actual": actual_disk_hash}
                )
                return
        except Exception as e:
            fail_closed(f"Failed to re-read target file '{target_path}' from disk: {e}", {"path": target_path, "error": str(e)})
            return

    # 7. Vector and V10 completeness
    v10 = v_state.get("V10", "")
    if v10 != "VERIFIED_SUCCESS":
        failed_vecs = v_state.get("failed_vectors", [])
        fail_closed(
            f"Machine verification is NOT satisfied (V10 = '{v10}', failed: {failed_vecs}). "
            "All 10 verification vectors must evaluate to PASS.",
            {"v10": v10, "failed_vectors": failed_vecs}
        )
        return

    vectors = v_state.get("vectors", {})
    for i in range(1, 10):
        vec_key = f"V{i}"
        if vectors.get(vec_key) != "PASS":
            fail_closed(f"Vector {vec_key} is not marked PASS (found: '{vectors.get(vec_key)}').", {"vector": vec_key})
            return

    # 8. All checks passed
    log_gate_event("allow", "Hardened cryptographic verification confirmed", {
        "v10": v10,
        "timestamp": ts,
        "hmac_verified": True,
        "disk_hashes_verified": len(file_hashes)
    })
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
