#!/usr/bin/env python3
"""
Hardened Native AGY Completion Gate Stop Hook (v2.1.0)
Enforces:
1. Cryptographic HMAC-SHA256 signature verification on state
2. Strict timestamp freshness (<= 120 seconds anti-stale limit)
3. Session & Conversation ID binding against incoming hook payload
4. Single-use nonce replay protection (consumed nonces registry)
5. Disk-level re-reading and SHA-256 integrity check of all target files
6. 10-level vector check (V1..V9 == PASS, V10 == VERIFIED_SUCCESS)
7. Expanded completion marker heuristics (multilingual EN/BN)
8. Fail-closed return on any controllable error condition
"""

import sys
import subprocess
import os
import json
import time
import hashlib
import hmac

STATE_FILE = os.environ.get("STATE_FILE_OVERRIDE", "/home/azureuser/.agents/verification_state.json")
KEY_FILE = os.environ.get("KEY_FILE_OVERRIDE", "/home/azureuser/.agents/.verification_secret.key")
CONSUMED_NONCES_FILE = os.environ.get("CONSUMED_NONCES_OVERRIDE", "/home/azureuser/.agents/consumed_nonces.jsonl")
INCIDENT_LOG = "/home/azureuser/.agents/completion_gate_attempts.jsonl"
MAX_STATE_AGE_SECONDS = 120

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

def get_transcript_metric(t_path: str) -> int:
    if t_path and os.path.isfile(t_path):
        try:
            with open(t_path, "rb") as tf:
                return sum(1 for _ in tf)
        except Exception:
            pass
    return 0

def is_nonce_consumed(nonce: str, current_conv_id: str = "", t_lines: int = 0, exec_num: int = 0) -> bool:
    if not os.path.exists(CONSUMED_NONCES_FILE):
        return False
    now = time.time()
    try:
        with open(CONSUMED_NONCES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("nonce") == nonce:
                    rec_conv = rec.get("conversation_id", "")
                    rec_lines = rec.get("transcript_lines", -1)
                    rec_exec = rec.get("execution_num", -1)
                    rec_ts = rec.get("timestamp", 0)
                    # Sibling hook within the exact same Stop event: same conversation, exact same transcript line count, same executionNum
                    if (current_conv_id and rec_conv == current_conv_id 
                        and t_lines > 0 and rec_lines == t_lines 
                        and exec_num > 0 and rec_exec == exec_num
                        and (now - rec_ts) < 10.0):
                        continue
                    return True
    except Exception:
        pass
    return False

def mark_nonce_consumed(nonce: str, task_name: str, conv_id: str, t_lines: int = 0, exec_num: int = 0):
    try:
        os.makedirs(os.path.dirname(CONSUMED_NONCES_FILE), exist_ok=True)
        rec = {
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "nonce": nonce,
            "task_name": task_name,
            "conversation_id": conv_id,
            "transcript_lines": t_lines,
            "execution_num": exec_num
        }
        with open(CONSUMED_NONCES_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + chr(10))
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to persist consumed nonce: {e}\n")

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({"decision": "allow"}))
            return
        payload = json.loads(raw)
    except Exception as e:
        fail_closed(f"Failed to parse Stop hook payload: {e}")
        return

    def get_agent_last_response(p):
        if p.get("finalModelOutput"):
            return str(p["finalModelOutput"])
        t_path = p.get("transcriptPath", "")
        if t_path and os.path.isfile(t_path):
            try:
                last_text = ""
                with open(t_path, "r", encoding="utf-8", errors="ignore") as tf:
                    for line in tf:
                        line = line.strip()
                        if not line: continue
                        try:
                            item = json.loads(line)
                            if item.get("source") == "MODEL" and item.get("type") in ("PLANNER_RESPONSE", "MODEL_RESPONSE", "GENERIC"):
                                c = item.get("content", "")
                                if c and isinstance(c, str):
                                    last_text = c
                        except Exception:
                            continue
                return last_text
            except Exception:
                pass
        return ""

    final_output = get_agent_last_response(payload) or payload.get("finalModelOutput", "") or payload.get("error", "")
    current_conv_id = payload.get("conversationId", "") or os.environ.get("CONVERSATION_ID", "")

    # Anti-Lying Check 1: Forbidden Promotional / False Verdict Labels (SETTING_67 & SETTING_68)
    forbidden_verdict_labels = [
        "সফলভাবে",
        "sofol vabe",
        "কাজটি সফলভাবে সম্পন্ন",
        "সব টেস্ট পাস",
        "all tests passed",
        "all tests verified",
        "10/10 pass",
        "10/10 verified"
    ]
    has_forbidden_label = any(lbl.lower() in final_output.lower() for lbl in forbidden_verdict_labels)

    completion_markers = [
        "verified_success",
        "task completed",
        "implemented_and_verified",
        "all tests passed",
        "10/10 pass",
        "task is done",
        "all 10 tests passed",
        "কাজ সম্পন্ন",
        "কাজ শেষ",
        "টেস্ট পাস",
        "সফলভাবে সম্পন্ন",
        "fix complete",
        "fixed",
        "done",
        "complete",
        "completed",
        "verified",
        "100% verified"
    ]
    
    claims_completion = any(marker.lower() in final_output.lower() for marker in completion_markers)

    if not claims_completion and not has_forbidden_label:
        print(json.dumps({"decision": "allow"}))
        return

    # If forbidden verdict label is present without signed verification, block immediately
    if has_forbidden_label and not os.path.exists(STATE_FILE):
        fail_closed(
            "🛑 [TRUTH HOOK HARD STOP - SETTING_67/68]: Forbidden promotional verdict label ('সফলভাবে', 'all tests passed') "
            "detected in response without empirical machine verification proof. Under SETTING_67 and SETTING_68, "
            "you are strictly prohibited from using promotional labels or self-praise. State ONLY factual actions and literal outputs.",
            {"has_forbidden_label": True}
        )
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

    # 5. Conversation / Session Binding Check
    state_conv_id = v_state.get("conversation_id", "")
    if current_conv_id and state_conv_id and current_conv_id != state_conv_id:
        fail_closed(
            f"Replay attack detected: verification state conversation ID '{state_conv_id}' "
            f"does not match current active conversation ID '{current_conv_id}'.",
            {"state_conv_id": state_conv_id, "current_conv_id": current_conv_id}
        )
        return

    # 6. Single-use Nonce Replay Check
    nonce = v_state.get("nonce", "")
    if not nonce:
        fail_closed("Verification state lacks required cryptographic nonce.", {"nonce": nonce})
        return

    t_lines = get_transcript_metric(payload.get("transcriptPath", ""))
    exec_num = payload.get("executionNum", 0)
    if is_nonce_consumed(nonce, current_conv_id, t_lines, exec_num):
        fail_closed(
            f"Replay attack detected: nonce '{nonce}' has already been consumed in a prior turn. "
            "Fresh verification is mandatory.",
            {"nonce": nonce, "replayed": True}
        )
        return

    # 7. Workspace binding validation
    ws_root = v_state.get("workspace_root", "")
    if not ws_root or not os.path.isdir(ws_root):
        fail_closed(f"Workspace root '{ws_root}' recorded in verification state does not exist or is invalid.", {"workspace_root": ws_root})
        return

    # 8. Strict Timestamp freshness check (<= 120 seconds)
    ts = v_state.get("timestamp", 0)
    current_time = time.time()
    if not isinstance(ts, (int, float)) or ts <= 0:
        fail_closed("Verification state has an invalid timestamp.", {"ts": ts})
        return

    age_seconds = current_time - ts
    if age_seconds > MAX_STATE_AGE_SECONDS:
        fail_closed(
            f"Verification record is STALE ({int(age_seconds)}s old > {MAX_STATE_AGE_SECONDS}s limit). Re-run verification.",
            {"age_seconds": age_seconds, "limit": MAX_STATE_AGE_SECONDS}
        )
        return

    # 9. Target file integrity: re-read disk and recompute SHA-256 hashes
    file_hashes = v_state.get("file_hashes", {})
    if not isinstance(file_hashes, dict) or not file_hashes:
        fail_closed("Invalid or empty file_hashes in state record (zero verified targets).", {"file_hashes": file_hashes})
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

    # 10. Vector and V10 completeness
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

    # 11. Mandatory Live Execution of Unified 72-Check Regression & Architecture Suite (Fail-Closed on Missing Runner)
    reg_runner = "/home/azureuser/.agents/run_regression_suite.py"
    if not os.path.isfile(reg_runner):
        fail_closed(
            f"Mandatory unified regression runner is MISSING from disk: '{reg_runner}'. "
            "Completion is strictly prohibited without the authoritative 72-check suite.",
            {"reg_runner": reg_runner, "exists": False}
        )
        return

    if os.environ.get("AGY_IN_REGRESSION_RUN") != "1":
        try:
            sub_env = dict(os.environ)
            sub_env["AGY_IN_REGRESSION_RUN"] = "1"
            p_reg = subprocess.run([sys.executable, reg_runner], env=sub_env, capture_output=True, text=True, timeout=15)
            if p_reg.returncode != 0:
                fail_closed(
                    "Unified 72-Check Regression & Architecture Suite FAILED at Stop Gate! "
                    "You cannot claim completion until all 72 assertions pass (Frappe v16 + Adversarial + Alco Architecture).",
                    {"returncode": p_reg.returncode, "stdout_tail": p_reg.stdout[-300:], "stderr_tail": p_reg.stderr[-300:]}
                )
                return
        except Exception as e:
            fail_closed(f"Failed to execute Unified Regression Runner at Stop Gate: {e}", {"error": str(e)})
            return

    # Mark nonce as consumed so it cannot be replayed
    mark_nonce_consumed(nonce, v_state.get("task_name", "unnamed"), state_conv_id)

    # 11. All checks passed
    log_gate_event("allow", "Hardened cryptographic verification confirmed", {
        "v10": v10,
        "timestamp": ts,
        "nonce": nonce,
        "conversation_id": state_conv_id,
        "hmac_verified": True,
        "disk_hashes_verified": len(file_hashes)
    })
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
