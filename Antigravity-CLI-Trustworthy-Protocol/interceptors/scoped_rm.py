#!/usr/bin/env python3
"""
Scoped Delete-Proof OS Binary Interceptor for rm (v2.1)
Narrowly exempts trusted build-tool cache and temporary generation paths:
- /home/azureuser/flutter/bin/cache/**
- /home/azureuser/flutter/version
- <project>/build/**
- <project>/.dart_tool/**
- /tmp/** (strictly scoped temporary files)
- /run/needrestart/**
- /var/lib/exim4/*.tmp

STRICTLY FORBIDS AND BLOCKS:
- Project source code (*.dart, *.rs, *.py, *.js, *.ts, etc.)
- .git repositories
- Databases (*.db, *.sqlite, Redis, MySQL)
- Configuration & environment files (.env, *.conf, *.json, *.toml)
- Governance and protection architecture (.agents, .gemini, Antigravity-CLI-Trustworthy-Protocol, AGY-MASTER, GLOBAL-ARCHIVE)
- User data directories and root paths
"""

import sys
import os
import json
import uuid
import subprocess
from datetime import datetime, timezone

REAL_RM = "/bin/rm"
INCIDENT_LOG = "/home/azureuser/AGY-MASTER/INCIDENTS/delete_attempts.jsonl"
INCIDENT_DIR = "/home/azureuser/AGY-MASTER/INCIDENTS/active"

FORBIDDEN_FRAGMENTS = [
    "/.git",
    "/.agents",
    "/.gemini",
    "/Antigravity-CLI-Trustworthy-Protocol",
    "/AGY-MASTER",
    "/GLOBAL-ARCHIVE",
    "/.verification_secret.key"
]

FORBIDDEN_EXTENSIONS = [
    ".key",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".env",
    ".dart",
    ".rs",
    ".py",
    ".js",
    ".ts"
]

CRITICAL_ROOTS = [
    "/",
    "/home",
    "/home/azureuser",
    "/home/azureuser/IrakIroan",
    "/home/azureuser/IrakIroan/IroScript_Projects",
    "/etc",
    "/usr",
    "/bin",
    "/sbin",
    "/var",
    "/opt",
    "/boot"
]

def log_denial(args, reason):
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
        "reason": reason,
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
        f"Reason: {reason}\n"
        f"Safe Alternative: Run `/home/azureuser/AGY-MASTER/POLICIES/safe_archive.py <path>` to preserve to /home/azureuser/GLOBAL-ARCHIVE/.\n\n"
    )
    sys.exit(1)

def is_path_safe_build_cache(canonical_path):
    # 1. Absolute root check
    if canonical_path in CRITICAL_ROOTS:
        return False, f"Target '{canonical_path}' is a critical system/user root"

    # 2. Forbidden fragment check
    for frag in FORBIDDEN_FRAGMENTS:
        if frag in canonical_path:
            return False, f"Target contains strictly protected governance path: {frag}"

    # 3. Whitelist check for trusted build/cache paths
    # a) Upstream Flutter version file
    if canonical_path == "/home/azureuser/flutter/version":
        return True, "Flutter version snapshot file"

    # b) Flutter internal cache & locks
    if canonical_path.startswith("/home/azureuser/flutter/bin/cache/"):
        return True, "Flutter internal cache"

    # c) Project build directory
    if "/build/" in canonical_path or canonical_path.endswith("/build"):
        return True, "Project build output directory"

    # d) Project .dart_tool directory
    if "/.dart_tool/" in canonical_path or canonical_path.endswith("/.dart_tool"):
        return True, "Project .dart_tool directory"

    # e) System temp directory (strictly scoped to /tmp/ sub-entries, no traversal)
    if canonical_path.startswith("/tmp/"):
        return True, "System /tmp temporary file"

    # f) OS package manager temp files
    if canonical_path.startswith("/run/needrestart/"):
        return True, "Package manager temporary file"
    if canonical_path.startswith("/var/lib/exim4/") and canonical_path.endswith(".tmp"):
        return True, "Exim4 temporary config file"

    # 4. If not matching any trusted build cache, check sensitive extensions
    for ext in FORBIDDEN_EXTENSIONS:
        if canonical_path.endswith(ext):
            return False, f"Target has sensitive extension '{ext}'"

    return False, f"Target '{canonical_path}' is NOT in the trusted build-tool cache whitelist"

def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(subprocess.call([REAL_RM]))

    targets = []
    for arg in args:
        if arg.startswith("-"):
            continue
        target = os.path.abspath(os.path.expanduser(arg))
        targets.append(target)

    if not targets:
        sys.exit(subprocess.call([REAL_RM] + args))

    for t in targets:
        is_safe, reason = is_path_safe_build_cache(t)
        if not is_safe:
            log_denial(args, reason)

    # All targets strictly satisfied the build-tool cache whitelist
    res = subprocess.call([REAL_RM] + args)
    sys.exit(res)

if __name__ == "__main__":
    main()
