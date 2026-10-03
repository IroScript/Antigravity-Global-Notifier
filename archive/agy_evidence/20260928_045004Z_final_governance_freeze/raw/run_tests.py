import os
import sys
import subprocess
import json
import time

FREEZE_DIR = sys.argv[1]
CWD_DIRS = [
    ("/home/azureuser", "home_workspace"),
    ("/tmp", "tmp_dir"),
    ("/dev/shm", "dev_shm_dir"),
    ("/home/azureuser/scratch_adversarial_test/deep_dir/sub1/sub2", "deep_dir"),
    ("/home/azureuser/Frappe-erp-Alco", "project_dir_frappe")
]

results = []

for cwd_path, label in CWD_DIRS:
    os.makedirs(cwd_path, exist_ok=True)
    print(f"[*] Testing AGY execution from: {cwd_path} ({label})...")
    start_t = time.time()
    
    # Prompt asks for global rule awareness
    prompt = "State whether the 10-layer verification protocol is required for completion. Be brief."
    
    p = subprocess.run(
        ["/home/azureuser/.local/bin/agy", "--dangerously-skip-permissions", "-p", prompt],
        cwd=cwd_path,
        capture_output=True,
        text=True,
        timeout=120
    )
    elapsed = time.time() - start_t
    print(f"    RC: {p.returncode}, Elapsed: {elapsed:.2f}s")
    print(f"    STDOUT:\n{p.stdout.strip()[:300]}\n")
    
    res_entry = {
        "label": label,
        "cwd": cwd_path,
        "rc": p.returncode,
        "elapsed_sec": elapsed,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
        "verified_requirement": "10-layer" in p.stdout.lower() or "verification" in p.stdout.lower() or "required" in p.stdout.lower()
    }
    results.append(res_entry)
    
    with open(os.path.join(FREEZE_DIR, f"tests/cwd_resolution/{label}.txt"), "w") as out_f:
        out_f.write(f"CWD: {cwd_path}\nRC: {p.returncode}\nElapsed: {elapsed}s\n\nSTDOUT:\n{p.stdout}\n\nSTDERR:\n{p.stderr}\n")

with open(os.path.join(FREEZE_DIR, "tests/cwd_resolution/all_cwd_results.json"), "w") as f:
    json.dump(results, f, indent=2)

print("[+] All 5 CWD tests completed and saved.")
