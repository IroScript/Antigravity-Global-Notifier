import os
import sys
import subprocess
import json
import time

FREEZE_DIR = sys.argv[1]
HOOK = "/home/azureuser/.agents/hooks/completion_gate_stop_hook.py"
VERIFIER = "/home/azureuser/.agents/verify_10_fold.py"
STATE_FILE = "/home/azureuser/.agents/verification_state.json"

print("="*60)
print("PART 7: FINAL REAL END-TO-END AGY VERIFICATION CHAIN")
print("="*60)

# -------------------------------------------------------------
# 1. CONTROLLED NEGATIVE TEST: Unverified Claim Cannot Receive VERIFIED_SUCCESS
# -------------------------------------------------------------
print("\n--- 1. CONTROLLED NEGATIVE TEST (Unverified Completion Claim) ---")
# Ensure state is invalid or failing
failing_state = {
    "task_name": "negative_test_unverified",
    "timestamp": time.time(),
    "V10": "FAILED",
    "failed_vectors": ["V4"],
    "vectors": {"V1": "PASS", "V2": "PASS", "V3": "PASS", "V4": "FAIL", "V5": "PASS", "V6": "PASS", "V7": "PASS", "V8": "PASS", "V9": "PASS"}
}
with open(STATE_FILE, "w") as f:
    json.dump(failing_state, f)

# Simulate model claiming completion without valid proof
neg_payload = {"terminationReason": "model_stop", "finalModelOutput": "Task is finished. VERIFIED_SUCCESS."}
p_neg = subprocess.run([sys.executable, HOOK], input=json.dumps(neg_payload), capture_output=True, text=True)
print("Negative test Stop hook exit code:", p_neg.returncode)
print("Negative test Stop hook decision output:\n", p_neg.stdout.strip())

neg_blocked = "continue" in p_neg.stdout
print(f"[*] Controlled Negative Test Verdict: {'PASSED (Unverified completion blocked)' if neg_blocked else 'FAILED'}")

with open(os.path.join(FREEZE_DIR, "tests/final_e2e_chain/negative_test.log"), "w") as f:
    f.write(f"RC: {p_neg.returncode}\nSTDOUT:\n{p_neg.stdout}\nSTDERR:\n{p_neg.stderr}\n")

# -------------------------------------------------------------
# 2. LEGITIMATE SUCCESSFUL TEST: Real Work -> Real Verification -> VERIFIED_SUCCESS
# -------------------------------------------------------------
print("\n--- 2. LEGITIMATE SUCCESSFUL TEST (Real Work & Full Chain) ---")
# A. Perform actual work: create production-quality file
target_path = os.path.join(FREEZE_DIR, "tests/final_e2e_chain/final_target.txt")
with open(target_path, "w") as f:
    f.write("Machine-verified permanent governance freeze target.\nTimestamp: " + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")

print(f"[+] Step A: Produced actual file on disk: {target_path}")

# B. Execute verification engine
v_cmd = f"python3 {VERIFIER} --files {target_path} --task-name final_freeze_e2e_task"
p_v = subprocess.run(v_cmd, shell=True, capture_output=True, text=True)
print("Verifier exit code:", p_v.returncode)
print("Verifier stdout:\n", p_v.stdout.strip())

with open(os.path.join(FREEZE_DIR, "tests/final_e2e_chain/verifier_run.log"), "w") as f:
    f.write(f"RC: {p_v.returncode}\nSTDOUT:\n{p_v.stdout}\nSTDERR:\n{p_v.stderr}\n")

# C. Read signed state
with open(STATE_FILE) as f:
    signed_state = json.load(f)

print(f"[+] Step C: State generated. V10={signed_state.get('V10')}, HMAC={signed_state.get('hmac_signature')[:16]}...")

# D. Evaluate Stop Hook
pos_payload = {"terminationReason": "model_stop", "finalModelOutput": "Task completed with VERIFIED_SUCCESS."}
p_pos = subprocess.run([sys.executable, HOOK], input=json.dumps(pos_payload), capture_output=True, text=True)
print("Positive test Stop hook exit code:", p_pos.returncode)
print("Positive test Stop hook decision output:\n", p_pos.stdout.strip())

pos_allowed = "allow" in p_pos.stdout
print(f"[*] Legitimate Successful Test Verdict: {'PASSED (Verified completion allowed)' if pos_allowed else 'FAILED'}")

with open(os.path.join(FREEZE_DIR, "tests/final_e2e_chain/positive_test.log"), "w") as f:
    f.write(f"RC: {p_pos.returncode}\nSTDOUT:\n{p_pos.stdout}\nSTDERR:\n{p_pos.stderr}\n")

print("\n" + "="*60)
print(f"E2E CHAIN COMPLETE: Negative Blocked={neg_blocked}, Positive Allowed={pos_allowed}")
print("="*60)
