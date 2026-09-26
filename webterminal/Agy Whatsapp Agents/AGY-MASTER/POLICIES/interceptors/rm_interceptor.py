#!/usr/bin/env python3
"""
Intercepts any direct or indirect invocation of rm.
Logs the incident and blocks execution permanently under Delete-Proof Specification.
"""
import sys
import os
import json
import uuid
from datetime import datetime, timezone

INCIDENT_LOG = "/home/azureuser/AGY-MASTER/INCIDENTS/delete_attempts.jsonl"
INCIDENT_DIR = "/home/azureuser/AGY-MASTER/INCIDENTS/active"

def record_and_block():
    args = sys.argv[1:]
    now = datetime.now(timezone.utc)
    inc_id = f"INC-DEL-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    
    incident = {
        "incident_id": inc_id,
        "timestamp": now.isoformat() + "Z",
        "severity": "CRITICAL",
        "detector": "OS_BINARY_INTERCEPTOR",
        "tool": "rm",
        "arguments": args,
        "calling_pid": os.getpid(),
        "parent_pid": os.getppid(),
        "decision": "DENIED",
        "reason": "Direct deletion via 'rm' binary is permanently disabled under Iraq Bhai 40-Point Delete-Proof Architecture Specification (Rule 1, 2).",
        "safe_alternative": "Move target to /home/azureuser/GLOBAL-ARCHIVE using /home/azureuser/AGY-MASTER/POLICIES/safe_archive.py"
    }

    try:
        os.makedirs(INCIDENT_DIR, exist_ok=True)
        with open(os.path.join(INCIDENT_DIR, f"{inc_id}.json"), "w") as f:
            json.dump(incident, f, indent=2)
        with open(INCIDENT_LOG, "a") as f:
            f.write(json.dumps(incident) + "\n")
    except Exception:
        pass

    sys.stderr.write(
        f"\n🛑 [DELETE-PROOF HARD BLOCK]\n"
        f"Operation: rm {' '.join(args)}\n"
        f"Status: PERMANENTLY DENIED (Rule 1, 2)\n"
        f"Incident: {inc_id}\n"
        f"Reason: AGY has no deletion capability. Deletions are forbidden.\n"
        f"Safe Alternative: Run `/home/azureuser/AGY-MASTER/POLICIES/safe_archive.py <path>` to preserve to /home/azureuser/GLOBAL-ARCHIVE/.\n\n"
    )
    sys.exit(1)

if __name__ == "__main__":
    record_and_block()
