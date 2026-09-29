#!/usr/bin/env python3
"""
Comprehensive Delete Guard Hook (Iraq Bhai's 40-Point Delete-Proof Architecture Specification - v2.2)
Intercepts all destructive operations at the PreToolUse stage.
Enforces:
1. Global Delete = PROHIBITED across CLI, Shell, Python, Subprocesses, and Child Agents.
2. Cryptographic Verification Secret Key read/dump/exfiltration = PROHIBITED.
3. Verifier scripts and Hook tampering/overwriting = PROHIBITED.
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

# Load Protected Registry
PROTECTED_WORKSPACES = [
    "/home/azureuser/AGY-MASTER",
    "/home/azureuser/Frappe-erp-Alco",
    "/home/azureuser/Rust_Task_With_Time_Keeping_And_Live_Note",
    "/home/azureuser/kids_tube_with_folder_seection",
    "/home/azureuser/Article-Publishing-Platform",
    "/home/azureuser/3D-Game-Design-Studio",
    "/home/azureuser/telegram-bot",
    "/home/azureuser/Ask-And-Research",
    "/home/azureuser/Reporting-Agent",
    "/home/azureuser/Action-Agent",
    "/home/azureuser/.openclaw",
    "/home/azureuser/GLOBAL-ARCHIVE"
]

PROTECTED_CONFIG_PATTERNS = [
    r".*\.agents/hooks\.json$",
    r".*\.agents/rules/.*",
    r".*\.agents/verify_10_fold\.py$",
    r".*\.agents/hooks/.*",
    r".*AGENTS\.md$",
    r".*GEMINI\.md$",
    r".*\.agents/verification_state\.json$",
    r".*\.agents/\.verification_secret\.key$",
    r".*\.agents/consumed_nonces\.jsonl$",
    r".*\.agents/.*\.key$",
    r".*Antigravity-CLI-Trustworthy-Protocol/hooks/.*",
    r".*Antigravity-CLI-Trustworthy-Protocol/scripts/.*",
    r".*\.gemini/config/hooks\.json$",
    r".*AGY-MASTER/POLICIES/.*",
    r".*GLOBAL-ARCHIVE/.*",
    r".*\.config/rclone/rclone\.conf$",
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
        "rule_id": rule_id,
        "safe_alternative": f"Move target to {ARCHIVE_ROOT} using /home/azureuser/AGY-MASTER/POLICIES/safe_archive.py"
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
    real_target = os.path.realpath(target)
    for pat in PROTECTED_CONFIG_PATTERNS:
        if re.search(pat, target) or re.search(pat, real_target):
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

    # Rule 42: Protected verification trust file tampering via chmod/mv/ln
    if re.search(r'\b(?:chmod|mv|ln)\b.*(?:\.agents/|\.verification_secret|Antigravity-CLI-Trustworthy-Protocol/hooks|Antigravity-CLI-Trustworthy-Protocol/scripts)', command_str):
        return True, "Tampering with verification trust files via chmod/mv/ln is prohibited (Rule 41)", "RULE_41_TRUST_FILE_TAMPERING"

    # Rule 43: Verifier / Hook Script Overwrite Prevention via shell redirection
    if re.search(r'>\s*.*?(?:verify_10_fold\.py|completion_gate_stop_hook\.py|delete_guard\.py|hooks\.json|\.verification_secret)', command_str):
        return True, "Shell redirection truncation/overwrite of verification scripts, hooks, or keys is strictly prohibited (Rule 35, 38, 41)", "RULE_38_41_VERIFIER_TAMPER_DENIED"

    # Rule 5: find ... -delete or find ... -exec/execdir/ok rm (including /bin/rm)
    if re.search(r'find\b.*(?:\s+-(?:delete|(?:exec|execdir|ok|okdir)\s+(?:/[a-zA-Z0-9_\-\.]+/)?rm\b))', command_str):
        return True, "Indirect deletion via 'find -delete / -exec rm' is prohibited (Rule 4, 5)", "RULE_4_5_FIND_DELETE"

    # Command substitution attempts: `...rm...` or $(...rm...)
    if re.search(r'[`$]\(?[^`$)]*\b(?:rm|unlink|rmdir)\b', command_str):
        return True, "Command substitution containing deletion command is prohibited (Rule 1, 2)", "RULE_1_2_COMMAND_SUBST"

    # Wrapper execution attempts: eval 'rm...', sh -c 'rm...', bash -c 'rm...'
    if re.search(r'(?:eval|sh\s+-c|bash\s+-c)\s+.*?\b(?:rm|unlink|rmdir)\b', command_str):
        return True, "Indirect command wrapper invocation of deletion command is prohibited (Rule 1, 2)", "RULE_1_2_WRAPPER_DELETE"

    # Rule 44: sed -i / sed --in-place tampering
    if re.search(r'\bsed\b.*?(?:-[a-zA-Z]*i\b|--in-place)', command_str):
        for tok in command_str.split():
            tok_clean = tok.strip('\'"')
            if is_path_protected_config(tok_clean):
                return True, f"In-place file tampering via 'sed -i' on protected path '{tok_clean}' is strictly prohibited (Rule 38, 41)", "RULE_SED_INPLACE_DENIED"

    # Rule 45: tee overwrite targeting protected path
    if re.search(r'\btee\b', command_str):
        for tok in command_str.split():
            tok_clean = tok.strip('\'"')
            if not tok_clean.startswith('-') and is_path_protected_config(tok_clean):
                return True, f"Overwriting protected path '{tok_clean}' via 'tee' is strictly prohibited (Rule 38, 41)", "RULE_TEE_OVERWRITE_DENIED"

    # Rule 46: perl -i tampering
    if re.search(r'\bperl\b.*?(?:-[a-zA-Z]*i\b)', command_str):
        for tok in command_str.split():
            tok_clean = tok.strip('\'"')
            if is_path_protected_config(tok_clean):
                return True, f"In-place file tampering via 'perl -i' on protected path '{tok_clean}' is strictly prohibited (Rule 38, 41)", "RULE_PERL_INPLACE_DENIED"

    # Rule 47: Python inline open write/append on protected config
    if re.search(r'python[0-9.]*\s+-c\b.*?(?:open\s*\([^)]*[\'\"][wa\+]|write_text|write_bytes)', command_str):
        for pat in PROTECTED_CONFIG_PATTERNS:
            kw = pat.replace('.*', '').replace('$', '').replace('\\', '')
            if kw and kw in command_str:
                return True, f"Inline Python file overwrite targeting protected resource '{kw}' is prohibited (Rule 38, 41)", "RULE_PYTHON_FILE_WRITE_DENIED"

    # Rule 10: git clean
    if re.search(r'git\s+clean\b', command_str):
        return True, "Destructive 'git clean' operation is prohibited (Rule 10)", "RULE_10_GIT_CLEAN"

    # Rule 11: git reset --hard
    if re.search(r'git\s+reset\s+--hard\b', command_str):
        return True, "Destructive 'git reset --hard' is prohibited in protected workspaces (Rule 11)", "RULE_11_GIT_RESET_HARD"

    # Rule 12: git checkout -- or git restore
    if re.search(r'git\s+checkout\s+--', command_str) or re.search(r'git\s+restore\b', command_str):
        return True, "Destructive 'git checkout --' / 'git restore' is prohibited (Rule 12)", "RULE_12_GIT_CHECKOUT_REVERT"

    # Rule 13: rsync --delete
    if re.search(r'rsync\b.*--delete', command_str):
        return True, "Destructive 'rsync --delete' is prohibited (Rule 13)", "RULE_13_RSYNC_DELETE"

    # Rule 8 & 9: Redirection file truncation (e.g. > file, >> file if malicious)
    redirs = re.findall(r'>\s*([^&|0-9\s]+)', command_str)
    for t in redirs:
        clean_t = t.strip('"\'')
        if clean_t not in ['/dev/null', '&1', '&2', '']:
            if is_path_protected_config(clean_t):
                return True, f"Shell redirection truncation into protected path '{clean_t}' is prohibited (Rule 8, 35, 38)", "RULE_8_38_TRUNCATION"

    # Rule 16: chattr -i
    if re.search(r'chattr\b.*(?:\s+-[a-zA-Z]*i\b)', command_str):
        return True, "Stripping Linux immutable attribute (+i -> -i) is strictly prohibited (Rule 16, 38)", "RULE_16_CHATTR_STRIP"

    # Rule 3: Python destructive operations in one-liners or invoked scripts
    if re.search(r'os\.(?:remove|unlink|rmdir)\(', command_str):
        return True, "Python os file/directory deletion is prohibited (Rule 3)", "RULE_3_PYTHON_OS_DELETE"
    if re.search(r'shutil\.rmtree\(', command_str):
        return True, "Python shutil.rmtree directory wipe is prohibited (Rule 3)", "RULE_3_PYTHON_SHUTIL_RMTREE"
    if re.search(r'Path\(.*\)\.(?:unlink|rmdir)\(', command_str):
        return True, "Python Pathlib deletion is prohibited (Rule 3)", "RULE_3_PYTHON_PATHLIB_DELETE"

    # Strip quoted strings to inspect actual shell command tokens
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

        # Rule 1 & 2: Direct removal
        if cmd_base in ['rm', 'rmdir', 'unlink']:
            return True, f"Direct deletion command '{cmd_base}' is strictly prohibited. Use safe_archive instead (Rule 1, 2)", "RULE_1_2_DIRECT_DELETE"

        # Rule 23: Truncation
        if cmd_base in ['truncate', 'fallocate']:
            return True, f"File truncation command '{cmd_base}' is prohibited (Rule 9, 23)", "RULE_9_23_TRUNCATE"

        # Rule 26: Privilege escalation
        if cmd_base in ['sudo', 'su', 'pkexec', 'doas']:
            return True, f"Privilege escalation via '{cmd_base}' is prohibited for AGY (Rule 26, 27)", "RULE_26_27_PRIV_ESCALATION"

        # Rule 4: xargs rm
        if cmd_base == 'xargs' and any(t.split('/')[-1] == 'rm' for t in tokens):
            return True, "Indirect deletion via 'xargs rm' is prohibited (Rule 4)", "RULE_4_XARGS_RM"

        # Rule 15: chmod -R 000 / chmod 000
        if cmd_base == 'chmod' and ('000' in tokens or '-R' in tokens and any(x in tokens for x in ['000', '-w'])):
            return True, "Destructive chmod permission removal is prohibited (Rule 15)", "RULE_15_CHMOD_STRIP"

        # Rule 6, 7 & 14: mv / cp overwriting protected path
        if cmd_base == 'mv' and len(tokens) >= 3:
            dest = tokens[-1].strip('"\'')
            if os.path.exists(dest) and is_path_protected_config(dest):
                return True, f"Destructive mv overwrite targeting protected path '{dest}' is prohibited (Rule 6, 7, 14)", "RULE_6_7_14_MV_OVERWRITE"

    return False, "Safe", "ALLOW"

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
            "reason": f"🛑 [DELETE-PROOF FAIL-CLOSED] {err_msg}"
        }))
        return

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args", {})

    # 1. RUN_COMMAND
    if tool_name == "run_command":
        cmd_line = args.get("CommandLine", "")
        is_dest, reason, rule_id = inspect_command(cmd_line)
        if is_dest:
            inc = log_incident(tool_name, {"CommandLine": cmd_line}, reason, rule_id)
            print(json.dumps({
                "decision": "deny",
                "reason": f"🛑 [DELETE-PROOF HARD DENIAL: {rule_id}] {reason}. Inc-ID: {inc['incident_id']}."
            }))
            return

    # 2. WRITE_TO_FILE
    elif tool_name == "write_to_file":
        target_file = args.get("TargetFile", "")
        overwrite = args.get("Overwrite", False)
        
        if is_path_protected_config(target_file):
            reason = f"Overwriting protected system/policy/archive target '{target_file}' is strictly prohibited (Rule 35, 38)"
            inc = log_incident(tool_name, {"TargetFile": target_file, "Overwrite": overwrite}, reason, "RULE_38_POLICY_TAMPERING")
            print(json.dumps({
                "decision": "deny",
                "reason": f"🛑 [DELETE-PROOF HARD DENIAL: RULE_38] {reason}. Inc-ID: {inc['incident_id']}."
            }))
            return

    # 3. REPLACE_FILE_CONTENT
    elif tool_name == "replace_file_content":
        target_file = args.get("TargetFile", "")
        if is_path_protected_config(target_file):
            if os.path.basename(target_file) in ["AGENTS.md", "GEMINI.md"]:
                pass
            else:
                reason = f"Modifying protected system/policy/archive target '{target_file}' via replace_file_content is strictly prohibited (Rule 35, 38)"
            inc = log_incident(tool_name, {"TargetFile": target_file}, reason, "RULE_38_POLICY_TAMPERING")
            print(json.dumps({
                "decision": "deny",
                "reason": f"🛑 [DELETE-PROOF HARD DENIAL: RULE_38] {reason}. Inc-ID: {inc['incident_id']}."
            }))
            return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
