#!/usr/bin/env python3
"""
Machine-Authoritative 10-Level Verification Protocol Engine for AGY (v2.0.0 - Hardened)
Features:
1. Rejects dummy test commands (true, :, echo, exit 0, sleep, etc.) in V4
2. Rejects dummy negative commands (false, exit 1, return 1, etc.) in V5
3. Enforces non-empty, existing, non-zero-byte target files in V1/V2
4. Generates single-use cryptographic nonce
5. Binds conversation ID and workspace root
6. Cryptographically signs state using HMAC-SHA256
Writes state to /home/azureuser/.agents/verification_state.json.
"""

import sys
import os
import re
import json
import time
import hashlib
import hmac
import secrets
import subprocess
import argparse

STATE_FILE = "/home/azureuser/.agents/verification_state.json"
KEY_FILE = "/home/azureuser/.agents/.verification_secret.key"
PROTOCOL_VERSION = "2.1"
VERIFIER_VERSION = "2.0.0"

DUMMY_TEST_PATTERNS = [
    r'^\s*true\s*$',
    r'^\s*:\s*$',
    r'^\s*echo(\s+.*)?$',
    r'^\s*exit\s+0\s*$',
    r'^\s*return\s+0\s*$',
    r'^\s*cat\s+/dev/null\s*$',
    r'^\s*sleep\s+.*$',
    r'^\s*nop\s*$'
]

DUMMY_NEG_PATTERNS = [
    r'^\s*false\s*$',
    r'^\s*exit\s+[1-9][0-9]*\s*$',
    r'^\s*return\s+[1-9][0-9]*\s*$',
    r'^\s*\(exit\s+[1-9][0-9]*\)\s*$'
]

def get_or_create_hmac_key():
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                k = f.read().strip()
                if k:
                    return k.encode("utf-8")
        except Exception:
            pass
    new_k = secrets.token_hex(32)
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    with open(KEY_FILE, "w", encoding="utf-8") as f:
        f.write(new_k + "\n")
    os.chmod(KEY_FILE, 0o600)
    return new_k.encode("utf-8")

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

def run_test(cmd):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {
            "cmd": cmd,
            "rc": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip()
        }
    except Exception as e:
        return {"cmd": cmd, "rc": -1, "stdout": "", "stderr": str(e)}

def is_dummy_command(cmd, patterns):
    if not cmd or not cmd.strip():
        return True, "EMPTY_COMMAND"
    cleaned = cmd.strip()
    for pat in patterns:
        if re.match(pat, cleaned, re.IGNORECASE):
            return True, f"MATCHED_DUMMY_PATTERN: {pat}"
    return False, ""

def main():
    parser = argparse.ArgumentParser(description="Hardened 10-Level Verification Protocol Runner")
    parser.add_argument("--files", nargs="*", default=[], help="Target files to verify existence, content, and integrity")
    parser.add_argument("--test-cmd", default="", help="Substantive command to execute for V4 dynamic testing")
    parser.add_argument("--negative-cmd", default="", help="Negative adversarial test command for V5")
    parser.add_argument("--rules", nargs="*", default=[], help="Rule files to verify V3 discovery")
    parser.add_argument("--hooks", default="", help="Hook file to verify V3 configuration")
    parser.add_argument("--task-name", default="unnamed_task", help="Name or description of task")
    parser.add_argument("--conversation-id", default="", help="Conversation ID to bind to")
    parser.add_argument("--session-id", default="", help="Session ID to bind to")
    parser.add_argument("--workspace", default="", help="Workspace root directory")
    args = parser.parse_args()

    conv_id = args.conversation_id or os.environ.get("CONVERSATION_ID", "447a4135-224e-49a7-93cd-e9130c02d41c")
    session_id = args.session_id or os.environ.get("AGY_SESSION_ID", "default_session")
    workspace_root = os.path.abspath(args.workspace or os.getcwd())

    evidence = {}
    vectors = {}
    failed_vectors = []

    print(f"[*] Starting Hardened 10-Level Verification (v{VERIFIER_VERSION}) for task: {args.task_name}")
    print(f"    Workspace: {workspace_root} | Conversation: {conv_id} | Session: {session_id}")

    abs_files = [os.path.abspath(f) for f in args.files]

    # ==========================================
    # V1 — EXISTENCE / STRUCTURE (Anti-Dummy Check)
    # ==========================================
    v1_pass = True
    v1_details = []
    if not abs_files:
        v1_pass = False
        v1_details.append({"error": "Target files list is EMPTY. Verification requires at least 1 real file target."})
    else:
        for f in abs_files:
            if f in ['/dev/null', '/dev/zero', '/dev/random', '/dev/urandom']:
                v1_details.append({"path": f, "error": "Dummy system device rejected as target file"})
                v1_pass = False
                continue
            if os.path.exists(f):
                st = os.stat(f)
                v1_details.append({"path": f, "exists": True, "size": st.st_size, "mode": oct(st.st_mode)})
                if st.st_size == 0 and not f.endswith(".empty"):
                    v1_pass = False
            else:
                v1_details.append({"path": f, "exists": False})
                v1_pass = False
    
    vectors["V1"] = "PASS" if v1_pass else "FAIL"
    evidence["V1"] = v1_details
    if vectors["V1"] != "PASS":
        failed_vectors.append("V1")
    print(f"  V1 (Existence): {vectors['V1']}")

    # ==========================================
    # V2 — CONTENT / CONFIGURATION
    # ==========================================
    v2_pass = True
    v2_details = []
    if not abs_files:
        v2_pass = False
        v2_details.append({"error": "Target files list is EMPTY."})
    else:
        for f in abs_files:
            if os.path.exists(f):
                try:
                    if f.endswith(".json"):
                        with open(f) as jf:
                            json.load(jf)
                        v2_details.append({"path": f, "valid_json": True})
                    else:
                        with open(f, "r", errors="ignore") as tf:
                            lines = len(tf.readlines())
                        v2_details.append({"path": f, "line_count": lines, "readable": True})
                        if lines == 0:
                            v2_pass = False
                except Exception as e:
                    v2_details.append({"path": f, "error": str(e)})
                    v2_pass = False
            else:
                v2_pass = False

    vectors["V2"] = "PASS" if v2_pass else "FAIL"
    evidence["V2"] = v2_details
    if vectors["V2"] != "PASS":
        failed_vectors.append("V2")
    print(f"  V2 (Content/Config): {vectors['V2']}")

    # ==========================================
    # V3 — LOADING / DISCOVERY
    # ==========================================
    v3_pass = True
    v3_details = []
    for rf in args.rules:
        r_abs = os.path.abspath(rf)
        if os.path.exists(r_abs):
            with open(r_abs, "r", errors="ignore") as fp:
                head = fp.read(300)
            has_always_on = "trigger: always_on" in head or "AGENTS.md" in r_abs or "GEMINI.md" in r_abs or "rules/" in r_abs
            v3_details.append({"rule": r_abs, "always_on": has_always_on})
            if not has_always_on:
                v3_pass = False
        else:
            v3_details.append({"rule": r_abs, "exists": False})
            v3_pass = False

    if args.hooks:
        h_abs = os.path.abspath(args.hooks)
        if os.path.exists(h_abs):
            try:
                with open(h_abs) as hf:
                    hdata = json.load(hf)
                v3_details.append({"hooks": h_abs, "parsed": True, "hook_count": len(hdata)})
            except Exception as e:
                v3_details.append({"hooks": h_abs, "error": str(e)})
                v3_pass = False
        else:
            v3_details.append({"hooks": h_abs, "exists": False})
            v3_pass = False

    vectors["V3"] = "PASS" if v3_pass else "FAIL"
    evidence["V3"] = v3_details
    if vectors["V3"] != "PASS":
        failed_vectors.append("V3")
    print(f"  V3 (Discovery): {vectors['V3']}")

    # ==========================================
    # V4 — EXECUTION / DYNAMIC TESTING (Anti-Dummy Gate)
    # ==========================================
    v4_pass = False
    v4_details = {}
    if not args.test_cmd or not args.test_cmd.strip():
        v4_details = {"error": "Dynamic test command (--test-cmd) is REQUIRED and cannot be empty."}
    else:
        is_dummy, reason = is_dummy_command(args.test_cmd, DUMMY_TEST_PATTERNS)
        if is_dummy:
            v4_details = {"cmd": args.test_cmd, "rejected_as_dummy": True, "reason": reason}
            v4_pass = False
        else:
            t_res = run_test(args.test_cmd)
            v4_pass = (t_res["rc"] == 0)
            v4_details = t_res

    vectors["V4"] = "PASS" if v4_pass else "FAIL"
    evidence["V4"] = v4_details
    if vectors["V4"] != "PASS":
        failed_vectors.append("V4")
    print(f"  V4 (Execution): {vectors['V4']}")

    # ==========================================
    # V5 — NEGATIVE / ADVERSARIAL TEST (Anti-Dummy Negative Gate)
    # ==========================================
    v5_pass = False
    v5_details = {}
    if not args.negative_cmd or not args.negative_cmd.strip():
        v5_details = {"error": "Negative adversarial test command (--negative-cmd) is REQUIRED and cannot be empty."}
    else:
        is_dummy_neg, reason = is_dummy_command(args.negative_cmd, DUMMY_NEG_PATTERNS)
        if is_dummy_neg:
            v5_details = {"cmd": args.negative_cmd, "rejected_as_dummy_negative": True, "reason": reason}
            v5_pass = False
        else:
            neg_res = run_test(args.negative_cmd)
            v5_pass = (neg_res["rc"] != 0 or any(k in neg_res["stdout"].lower() for k in ["deny", "denied", "blocked", "prohibited"]))
            v5_details = {"cmd": args.negative_cmd, "rc": neg_res["rc"], "blocked": v5_pass, "output": (neg_res["stdout"] + " " + neg_res["stderr"])[:200]}

    vectors["V5"] = "PASS" if v5_pass else "FAIL"
    evidence["V5"] = v5_details
    if vectors["V5"] != "PASS":
        failed_vectors.append("V5")
    print(f"  V5 (Adversarial): {vectors['V5']}")

    # ==========================================
    # V6 — INTEGRITY (SHA-256 HASHES)
    # ==========================================
    file_hashes = {}
    for f in abs_files:
        if os.path.exists(f):
            file_hashes[f] = sha256_file(f)
    vectors["V6"] = "PASS" if (file_hashes and abs_files) else "FAIL"
    evidence["V6"] = file_hashes
    if vectors["V6"] != "PASS":
        failed_vectors.append("V6")
    print(f"  V6 (Integrity): {vectors['V6']}")

    # ==========================================
    # V7 — PERSISTENCE
    # ==========================================
    v7_pass = all(os.path.exists(f) for f in abs_files) if abs_files else False
    vectors["V7"] = "PASS" if v7_pass else "FAIL"
    evidence["V7"] = {"persisted_on_disk": v7_pass}
    if vectors["V7"] != "PASS":
        failed_vectors.append("V7")
    print(f"  V7 (Persistence): {vectors['V7']}")

    # ==========================================
    # V8 — ATTACK SURFACE
    # ==========================================
    v8_pass = True
    v8_details = []
    for f in abs_files:
        if os.path.exists(f):
            st = os.stat(f)
            world_write = bool(st.st_mode & 0o002)
            v8_details.append({"file": f, "world_writable": world_write})
            if world_write:
                v8_pass = False
    vectors["V8"] = "PASS" if (v8_pass and abs_files) else "FAIL"
    evidence["V8"] = v8_details
    if vectors["V8"] != "PASS":
        failed_vectors.append("V8")
    print(f"  V8 (Attack Surface): {vectors['V8']}")

    # ==========================================
    # V9 — INDEPENDENT MACHINE EVIDENCE
    # ==========================================
    nonce = secrets.token_hex(16)
    epoch_now = time.time()
    vectors["V9"] = "PASS"
    evidence["V9"] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch_now)),
        "epoch": epoch_now,
        "nonce": nonce,
        "uid": os.getuid(),
        "gid": os.getgid(),
        "host": "FatehAli"
    }
    print(f"  V9 (Evidence): {vectors['V9']}")

    # ==========================================
    # V10 — MECHANICAL DERIVATION
    # ==========================================
    all_passed = (len(failed_vectors) == 0 and all(vectors[f"V{i}"] == "PASS" for i in range(1, 10)))
    v10 = "VERIFIED_SUCCESS" if all_passed else "FAILED"
    print(f"==========================================")
    print(f"  V10 (Derived Verdict): {v10}")
    print(f"==========================================")

    key_bytes = get_or_create_hmac_key()

    state_payload = {
        "protocol_version": PROTOCOL_VERSION,
        "verifier_version": VERIFIER_VERSION,
        "task_name": args.task_name,
        "conversation_id": conv_id,
        "session_id": session_id,
        "workspace_root": workspace_root,
        "nonce": nonce,
        "target_files": abs_files,
        "file_hashes": file_hashes,
        "timestamp": epoch_now,
        "formatted_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch_now)),
        "V10": v10,
        "failed_vectors": failed_vectors,
        "vectors": vectors,
        "evidence": evidence
    }

    sig = compute_state_hmac(key_bytes, state_payload)
    state_payload["hmac_signature"] = sig

    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state_payload, f, indent=2)

    print(f"[+] Cryptographically signed state written to: {STATE_FILE}")
    print(f"[+] Conversation ID bound: {conv_id}")
    print(f"[+] Nonce: {nonce}")
    print(f"[+] HMAC-SHA256 signature: {sig[:16]}...{sig[-8:]}")
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
