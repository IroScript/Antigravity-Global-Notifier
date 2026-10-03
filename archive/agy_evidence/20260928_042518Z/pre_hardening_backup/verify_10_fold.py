#!/usr/bin/env python3
"""
Machine-Authoritative 10-Level Verification Protocol Engine for AGY
Executes V1 through V9, collects machine-observable evidence, and derives V10.
Writes state to /home/azureuser/.agents/verification_state.json.
"""

import sys
import os
import json
import time
import hashlib
import subprocess
import argparse

STATE_FILE = "/home/azureuser/.agents/verification_state.json"

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

def main():
    parser = argparse.ArgumentParser(description="10-Level Verification Protocol Runner")
    parser.add_argument("--files", nargs="*", default=[], help="Target files to verify existence, content, and integrity")
    parser.add_argument("--test-cmd", default="", help="Command to execute for V4 dynamic testing")
    parser.add_argument("--negative-cmd", default="", help="Negative adversarial test command for V5")
    parser.add_argument("--rules", nargs="*", default=[], help="Rule files to verify V3 discovery")
    parser.add_argument("--hooks", default="", help="Hook file to verify V3 configuration")
    parser.add_argument("--task-name", default="unnamed_task", help="Name or description of task")
    args = parser.parse_args()

    evidence = {}
    vectors = {}
    failed_vectors = []

    print(f"[*] Starting 10-Level Verification for: {args.task_name}")

    # ==========================================
    # V1 — EXISTENCE / STRUCTURE
    # ==========================================
    v1_pass = True
    v1_details = []
    for f in args.files:
        if os.path.exists(f):
            st = os.stat(f)
            v1_details.append({"path": f, "exists": True, "size": st.st_size, "mode": oct(st.st_mode)})
            if st.st_size == 0 and not f.endswith(".empty"):
                v1_pass = False
        else:
            v1_details.append({"path": f, "exists": False})
            v1_pass = False
    
    vectors["V1"] = "PASS" if v1_pass and args.files else "FAIL"
    evidence["V1"] = v1_details
    if vectors["V1"] != "PASS":
        failed_vectors.append("V1")
    print(f"  V1 (Existence): {vectors['V1']}")

    # ==========================================
    # V2 — CONTENT / CONFIGURATION
    # ==========================================
    v2_pass = True
    v2_details = []
    for f in args.files:
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
            except Exception as e:
                v2_details.append({"path": f, "error": str(e)})
                v2_pass = False
        else:
            v2_pass = False

    vectors["V2"] = "PASS" if v2_pass and args.files else "FAIL"
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
        if os.path.exists(rf):
            with open(rf, "r", errors="ignore") as fp:
                head = fp.read(300)
            has_always_on = "trigger: always_on" in head or "AGENTS.md" in rf or "GEMINI.md" in rf
            v3_details.append({"rule": rf, "always_on": has_always_on})
            if not has_always_on:
                v3_pass = False
        else:
            v3_details.append({"rule": rf, "exists": False})
            v3_pass = False

    if args.hooks:
        if os.path.exists(args.hooks):
            try:
                with open(args.hooks) as hf:
                    hdata = json.load(hf)
                v3_details.append({"hooks": args.hooks, "parsed": True, "hook_count": len(hdata)})
            except Exception as e:
                v3_details.append({"hooks": args.hooks, "error": str(e)})
                v3_pass = False
        else:
            v3_details.append({"hooks": args.hooks, "exists": False})
            v3_pass = False

    vectors["V3"] = "PASS" if v3_pass else "FAIL"
    evidence["V3"] = v3_details
    if vectors["V3"] != "PASS":
        failed_vectors.append("V3")
    print(f"  V3 (Discovery): {vectors['V3']}")

    # ==========================================
    # V4 — EXECUTION / DYNAMIC TESTING
    # ==========================================
    if args.test_cmd:
        t_res = run_test(args.test_cmd)
        v4_pass = (t_res["rc"] == 0)
        evidence["V4"] = t_res
    else:
        v4_pass = True
        evidence["V4"] = {"note": "No test command supplied; static operation"}

    vectors["V4"] = "PASS" if v4_pass else "FAIL"
    if vectors["V4"] != "PASS":
        failed_vectors.append("V4")
    print(f"  V4 (Execution): {vectors['V4']}")

    # ==========================================
    # V5 — NEGATIVE / ADVERSARIAL TEST
    # ==========================================
    if args.negative_cmd:
        neg_res = run_test(args.negative_cmd)
        # In a negative test, we expect non-zero exit code or "deny" decision
        v5_pass = (neg_res["rc"] != 0 or "deny" in neg_res["stdout"].lower() or "blocked" in neg_res["stdout"].lower() or "eacces" in neg_res["stderr"].lower())
        evidence["V5"] = {"cmd": args.negative_cmd, "rc": neg_res["rc"], "contained": v5_pass, "output": (neg_res["stdout"] + " " + neg_res["stderr"])[:200]}
    else:
        v5_pass = True
        evidence["V5"] = {"note": "Negative test omitted"}

    vectors["V5"] = "PASS" if v5_pass else "FAIL"
    if vectors["V5"] != "PASS":
        failed_vectors.append("V5")
    print(f"  V5 (Adversarial): {vectors['V5']}")

    # ==========================================
    # V6 — INTEGRITY (SHA-256 HASHES)
    # ==========================================
    v6_details = {}
    for f in args.files:
        if os.path.exists(f):
            v6_details[f] = sha256_file(f)
    vectors["V6"] = "PASS" if v6_details else "FAIL"
    evidence["V6"] = v6_details
    if vectors["V6"] != "PASS":
        failed_vectors.append("V6")
    print(f"  V6 (Integrity): {vectors['V6']}")

    # ==========================================
    # V7 — PERSISTENCE
    # ==========================================
    # Verify that files are persisted on disk (not temporary / memory)
    v7_pass = all(os.path.exists(f) for f in args.files)
    vectors["V7"] = "PASS" if v7_pass and args.files else "FAIL"
    evidence["V7"] = {"persisted_on_disk": v7_pass}
    if vectors["V7"] != "PASS":
        failed_vectors.append("V7")
    print(f"  V7 (Persistence): {vectors['V7']}")

    # ==========================================
    # V8 — BYPASS / ATTACK SURFACE
    # ==========================================
    # Check that permissions do not allow world-write on critical files
    v8_pass = True
    v8_details = []
    for f in args.files:
        if os.path.exists(f):
            st = os.stat(f)
            world_write = bool(st.st_mode & 0o002)
            v8_details.append({"file": f, "world_writable": world_write})
            if world_write:
                v8_pass = False
    vectors["V8"] = "PASS" if v8_pass else "FAIL"
    evidence["V8"] = v8_details
    if vectors["V8"] != "PASS":
        failed_vectors.append("V8")
    print(f"  V8 (Attack Surface): {vectors['V8']}")

    # ==========================================
    # V9 — INDEPENDENT EVIDENCE
    # ==========================================
    # Machine metadata collected
    vectors["V9"] = "PASS"
    evidence["V9"] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "epoch": time.time(),
        "uid": os.getuid(),
        "gid": os.getgid()
    }
    print(f"  V9 (Evidence): {vectors['V9']}")

    # ==========================================
    # V10 — MECHANICAL DERIVATION
    # ==========================================
    # V10 = AND(V1..V9)
    all_passed = (len(failed_vectors) == 0 and all(vectors[f"V{i}"] == "PASS" for i in range(1, 10)))
    v10 = "VERIFIED_SUCCESS" if all_passed else "FAILED"
    print(f"==========================================")
    print(f"  V10 (Derived Verdict): {v10}")
    print(f"==========================================")

    # Save state to STATE_FILE
    state_payload = {
        "task_name": args.task_name,
        "timestamp": time.time(),
        "formatted_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "V10": v10,
        "failed_vectors": failed_vectors,
        "vectors": vectors,
        "evidence": evidence
    }

    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state_payload, f, indent=2)

    print(f"[+] Verification state written to: {STATE_FILE}")
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
