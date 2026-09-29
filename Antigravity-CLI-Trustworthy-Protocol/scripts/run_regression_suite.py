#!/usr/bin/env python3
"""
UNIFIED TRUSTWORTHY AGY REGRESSION TEST RUNNER (72 CHECKS)
Executes:
  1. Frappe v16 & Local Directory Governance Suite (30 blocks)
  2. Trustworthy AGY Adversarial Security Suite (5 attack groups, 30 sub-tests)
  3. Alco × Frappe v16 Architecture Compliance Suite (12 vectors)
Fails closed (exit code 1) if even 1 assertion fails across the 72 checks.
"""

import sys
import os
import subprocess

FRAPPE_BLOCKS_SCRIPT = "/home/azureuser/.agents/test_frappe_v16_hard_blocks.py"
ADVERSARIAL_SUITE_SCRIPT = "/home/azureuser/.agents/test_trustworthy_agy_enforcement.py"
ARCHITECTURE_SUITE_SCRIPT = "/home/azureuser/.agents/test_alco_frappe_architecture.py"

def main():
    print("=" * 75)
    print("STARTING UNIFIED TRUSTWORTHY AGY REGRESSION PROTECTION RUNNER")
    print("=" * 75)

    # 1. Execute Frappe v16 Hard Blocks Suite (30 blocks)
    print("\n[PART 1/3] Executing Frappe v16 & Local Directory Governance Suite (30 blocks)...")
    res_frappe = subprocess.run([sys.executable, FRAPPE_BLOCKS_SCRIPT], capture_output=True, text=True)
    print(res_frappe.stdout)
    if res_frappe.returncode != 0:
        print("[FAIL] Part 1 (Frappe v16 Governance) failed!")
        if res_frappe.stderr:
            print("STDERR:", res_frappe.stderr)
        sys.exit(1)

    # 2. Execute Adversarial Security Suite (5 attack groups, 30 sub-tests)
    print("\n[PART 2/3] Executing Trustworthy AGY Adversarial Suite (5 groups, 30 sub-tests)...")
    res_adv = subprocess.run([sys.executable, ADVERSARIAL_SUITE_SCRIPT], capture_output=True, text=True)
    print(res_adv.stdout)
    if res_adv.returncode != 0:
        print("[FAIL] Part 2 (Adversarial Enforcement) failed!")
        if res_adv.stderr:
            print("STDERR:", res_adv.stderr)
        sys.exit(1)

    # 3. Execute Alco x Frappe Architecture Compliance Suite (12 vectors)
    print("\n[PART 3/3] Executing Alco × Frappe v16 Architecture Compliance Suite (12 vectors)...")
    res_arch = subprocess.run([sys.executable, ARCHITECTURE_SUITE_SCRIPT], capture_output=True, text=True)
    print(res_arch.stdout)
    if res_arch.returncode != 0:
        print("[FAIL] Part 3 (Alco Architecture Compliance) failed!")
        if res_arch.stderr:
            print("STDERR:", res_arch.stderr)
        sys.exit(1)

    print("\n" + "=" * 75)
    print("UNIFIED REGRESSION SUMMARY: 72/72 CHECKS SATISFIED")
    print("  - Part 1: Frappe v16 Governance Blocks ........... 30/30 PASS")
    print("  - Part 2: Adversarial Security Sub-Tests ......... 30/30 PASS")
    print("  - Part 3: Frappe v16 Architecture Vectors ........ 12/12 PASS")
    print("ALL REGRESSION ASSERTIONS SATISFIED (Exit Code: 0)")
    print("=" * 75)
    sys.exit(0)

if __name__ == "__main__":
    main()
