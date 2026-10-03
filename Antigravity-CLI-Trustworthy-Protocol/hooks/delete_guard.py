#!/usr/bin/env python3
"""
Delete Guard Hook - Delete Feature Approved Architecture (v3.0)
Updated per user requirement:
"Only delete feature lagbe, maane aage delete lock chhilo now delete or feature approved thakbe"

Enforces:
1. Delete Feature = APPROVED & PERMITTED for workspace files, builds, folders, caches, and cleanup operations.
2. Critical System Roots (/etc, /boot, /root, /usr, /bin, /sbin, /) = PROTECTED from catastrophic destruction.
3. Cryptographic Verification Secret Key exfiltration = PROHIBITED.
4. Privilege Escalation (sudo, su) = RESTRICTED.
"""

import sys
import os
import re
import json
import shlex
import uuid
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = "/home/azureuser/AGY-MASTER/POLICIES/protected_registry.json"
INCIDENT_DIR = "/home/azureuser/AGY-MASTER/INCIDENTS/active"
INCIDENT_LOG = "/home/azureuser/AGY-MASTER/INCIDENTS/delete_attempts.jsonl"
ARCHIVE_ROOT = "/home/azureuser/GLOBAL-ARCHIVE"

# System-level root paths that must never be wiped
CRITICAL_SYSTEM_ROOTS = [
    "/",
    "/etc",
    "/bin",
    "/sbin",
    "/usr",
    "/boot",
    "/root",
    "/sys",
    "/proc",
    "/dev"
]

PROTECTED_CONFIG_PATTERNS = [
    r".*\.verification_secret\.key$",
    r"/etc/.*",
    r"/bin/.*",
    r"/sbin/.*",
    r"/usr/.*",
    r"/boot/.*",
    r"/root/.*"
]

def log_incident(tool_name, details, reason, rule_id):
    os.makedirs(INCIDENT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(INCIDENT_LOG), exist_ok=True)
    
    now = datetime.now(timezone.utc)
    inc_id = f"INC-DEL-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    
    incident = {
        "incident_id": inc_id,
        "timestamp": now.isoformat(),
        "severity": "CRITICAL",
        "detector": "DELETE_GUARD_PRETOOLUSE",
        "tool": tool_name,
        "details": details,
        "decision": "DENIED",
        "reason": reason,
        "rule_id": rule_id
    }

    try:
        inc_file = os.path.join(INCIDENT_DIR, f"{inc_id}.json")
        with open(inc_file, "w", encoding="utf-8") as f:
            json.dump(incident, f, indent=2)
        with open(INCIDENT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(incident) + "\n")
    except Exception as e:
        sys.stderr.write(f"Failed to log incident: {e}\n")

    return incident

def is_path_protected_config(target_path):
    target = os.path.abspath(target_path)
    for pat in PROTECTED_CONFIG_PATTERNS:
        if re.search(pat, target):
            return True
    return False

def inspect_command(command_str):
    # Rule 39: Destructive Git push operations (force, lease, delete)
    if re.search(r'git\s+push\b.*(?:\s+-(?:f|-force|-force-with-lease|-delete)\b|\s+--force\b|\s+--force-with-lease\b|\s+--delete\b)', command_str):
        return True, "Destructive 'git push --force / -f / --delete' is strictly prohibited (Rule 39)", "RULE_39_GIT_FORCE_PUSH"

    # Rule 40: Destructive Git branch -D / gh repo delete
    if re.search(r'git\s+branch\b.*(?:\s+-D\b)', command_str):
        return True, "Destructive 'git branch -D' force-deletion is prohibited (Rule 40)", "RULE_40_GIT_FORCE_BRANCH_DELETE"
    if re.search(r'gh\s+repo\s+delete\b', command_str):
        return True, "Destructive 'gh repo delete' repository deletion is prohibited (Rule 40)", "RULE_40_GH_REPO_DELETE"

    # Rule 41: Secret key reading/dumping/exfiltration prevention
    if re.search(r'\.verification_secret\.key\b', command_str):
        read_exfil_cmds = r'\b(?:cat|head|tail|more|less|grep|awk|sed|strings|od|xxd|hexdump|base64|curl|wget|nc|scp|cp|mv|ln|dd)\b'
        if re.search(read_exfil_cmds, command_str) or re.search(r'open\s*\(.*verification_secret', command_str):
            return True, "Direct reading, dumping, or exfiltration of the cryptographic verification secret key is strictly prohibited (Rule 41)", "RULE_41_SECRET_KEY_READ_DENIED"

    # Check for catastrophic root destruction
    for root_dir in CRITICAL_SYSTEM_ROOTS:
        pattern = rf'\brm\s+(?:-[a-zA-Z]*r[a-zA-Z]*\s+)?{re.escape(root_dir)}(?:/\*|\s*$)'
        if re.search(pattern, command_str):
            return True, f"Catastrophic deletion of system root directory '{root_dir}' is prohibited", "CRITICAL_SYSTEM_ROOT_PROTECT"

    # Rule 26: Privilege escalation
    clean_str = re.sub(r'["\'].*?["\']', '', command_str)
    segments = re.split(r'[;&|\n`$()]', clean_str)
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        try:
            tokens = shlex.split(seg)
        except Exception:
            tokens = seg.split()
        if not tokens:
            continue
        cmd = tokens[0]
        cmd_base = cmd.split('/')[-1]
        if cmd_base in ['sudo', 'su', 'pkexec', 'doas']:
            return True, f"Privilege escalation via '{cmd_base}' is prohibited for AGY (Rule 26, 27)", "RULE_26_27_PRIV_ESCALATION"

    # DELETE FEATURE APPROVED:
    # All standard deletions (rm, rmdir, unlink, shutil.rmtree, os.remove, git clean, find -delete)
    # in user workspaces are fully authorized and permitted!
    return False, "Delete feature approved", "ALLOW"

def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "allow"}))
            return
        payload = json.loads(raw_input)
    except Exception as e:
        err_msg = f"Failed to parse hook payload: {e}"
        print(json.dumps({
            "decision": "deny",
            "reason": f"🛑 [DELETE-GUARD FAIL-CLOSED] {err_msg}"
        }))
        return

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args", {})

    if tool_name == "run_command":
        cmd_line = args.get("CommandLine", "")
        is_dest, reason, rule_id = inspect_command(cmd_line)
        if is_dest:
            inc = log_incident(tool_name, {"CommandLine": cmd_line}, reason, rule_id)
            print(json.dumps({
                "decision": "deny",
                "reason": f"🛑 [DELETE-GUARD HARD DENIAL: {rule_id}] {reason}. Inc-ID: {inc['incident_id']}."
            }))
            return

    # Default Allow for all other operations (delete feature approved)
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
