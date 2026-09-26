#!/usr/bin/env python3
import sys
import subprocess
import os

raw_stdin = sys.stdin.read()

# Forward payload into delete_guard.py
try:
    proc = subprocess.run(
        ["/usr/bin/python3", "/home/azureuser/AGY-MASTER/POLICIES/delete_guard.py"],
        input=raw_stdin,
        text=True,
        capture_output=True,
        timeout=5
    )
    print(proc.stdout.strip())
    sys.exit(proc.returncode)
except Exception as e:
    # Fail closed on any exception
    sys.stderr.write(f"delete_guard execution failed: {e}\n")
    print('{"decision": "deny", "reason": "Delete guard execution error (fail closed)"}')
    sys.exit(1)
