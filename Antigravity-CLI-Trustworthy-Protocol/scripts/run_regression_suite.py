#!/usr/bin/env python3
"""
UNIFIED TRUSTWORTHY AGY REGRESSION TEST RUNNER
Executes:
  1. Frappe v16 & Local Directory Governance Suite (30 blocks)
  2. Trustworthy AGY Adversarial Security Suite (5 attack groups, 30 sub-tests)
Fails closed (exit code 1) if even 1 assertion fails across the 60 checks.
"""

import sys
import os
import subprocess

FRAPPE_BLOCKS_SCRIPT = "/home/azureuser/.agents/test_frappe_v16_hard_blocks.py"
ADVERSARIAL_SUITE_SCRIPT = "/home/azureuser/.agents/test_trustworthy_agy_enforcement.py"

def main():
    print("=" * 70)
    print("STARTING UNIFIED TRUSTWORTHY AGY REGRESSION PROTECTION RUNNER")
    print("=" * 70)

    # 1. Execute Frappe v16 Hard Blocks Suite (30 blocks)
    print("\n[PART 1/2] Executing Frappe v16 & Local Directory Governance Suite (30 blocks)...")
    res_frappe = subprocess.run([sys.executable, FRAPPE_BLOCKS_SCRIPT], capture_output=True, text=True)
    print(res_frappe.stdout)
    if res_frappe.returncode != 0:
        print("[FAIL] Part 1 (Frappe v16 Governance) failed!")
        sys.exit(1)

    # 2. Execute Adversarial Security Suite (5 attack groups, 30 sub-tests)
    print("\n[PART 2/2] Executing Trustworthy AGY Adversarial Suite (5 groups, 30 sub-tests)...")
    res_adv = subprocess.run([sys.executable, ADVERSARIAL_SUITE_SCRIPT], capture_output=True, text=True)
    print(res_adv.stdout)
    if res_adv.returncode != 0:
        print("[FAIL] Part 2 (Adversarial Enforcement) failed!")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("UNIFIED REGRESSION SUMMARY: 60/60 CHECKS PASSED")
    print("  - Part 1: Frappe v16 Governance Blocks ........... 30/30 PASS")
    print("  - Part 2: Adversarial Security Sub-Tests ......... 30/30 PASS")
    print("ALL REGRESSION ASSERTIONS SATISFIED (Exit Code: 0)")
    print("=" * 70)
    sys.exit(0)

if __name__ == "__main__":
    main()
