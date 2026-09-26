# HARDENED FOUR-LAYER DEFENSE ARCHITECTURE & PRE-IMPLEMENTATION GATES

Location: `/home/azureuser/AGY-MASTER/REPORTS/HARDENED_FOUR_LAYER_ARCHITECTURE_AND_PRE_IMPLEMENTATION_GATES.md`  
Date: 25 September 2026  
Author: AGY Principal Master Agent  
Reviewer: Iraq Bhai (ইরাক ভাইয়া)  
Status: CANONICAL SPECIFICATION & PRE-IMPLEMENTATION GATEWAY

---

## 1. THE 4-LAYER DEFENSE ARCHITECTURE

A tool-interception hook alone CANNOT guarantee that an agent cannot cause harmful side-effects. Antigravity's `PreToolUse` hook operates strictly at the application layer and cannot intercept subprocesses, background daemons, or direct shell escapes.

Therefore, total safety requires four concentric defense layers:

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: Antigravity Policy Gateway (PreToolUse Interceptor) │
│ - Tool call validation (allow/deny binary decision)         │
│ - Operation-aware regex filtering (git, docker, destructive)│
│ - Self-protection against hook/policy modification          │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ LAYER 2: OS Identity Separation & Privilege Containment      │
│ - azureuser (Human/Admin with sudo)                         │
│ - agy-master (Orchestrator, no sudo, no docker)             │
│ - project-agent-user (Domain worker, no sudo, no docker)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ LAYER 3: Filesystem Permissions & DAC/ACL Hardening         │
│ - Policy/Hook files owned by root/admin (read-only to agent)│
│ - Workspaces owned by project users; cross-project read-only│
│ - Sensitive files (.ssh, .env, systemd) inaccessible        │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ LAYER 4: Process & Systemd Service Isolation                │
│ - Systemd NoNewPrivileges=true, ProtectSystem=strict        │
│ - Process boundaries prevent tmux/kill interference          │
│ - Container boundaries prevent host filesystem mounting     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. OS IDENTITY SEPARATION BLUEPRINT

### The Critical Structural Weakness
The audit confirmed:
`azureuser ALL=(ALL) NOPASSWD: ALL`
If the agent runs under the same Linux identity as the administrator, any bypass of `PreToolUse` (e.g. via dynamic Python script or command injection) immediately grants root privileges.

### Target 3-Tier Identity Topology

| Identity | Linux User | Sudo Access | Docker Access | SSH/Cloud Keys | Permitted Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Human Admin** | `azureuser` | `NOPASSWD: ALL` | Yes | Yes | Server maintenance, disaster recovery, bootstrap |
| **Master Agent** | `agy-master` | **NONE** | **NONE** | Read-only public | Orchestrator, task router, policy gateway execution |
| **Project Workers** | `agy-worker` | **NONE** | **NONE** | **NONE** | Domain-locked project directories only |

### Worker Identity Restrictions
Worker agents MUST have:
1. `sudo` → Completely disabled.
2. `docker` → Removed from docker group; cannot access `/var/run/docker.sock`.
3. `SSH keys` → Cannot read `/home/azureuser/.ssh/id_*`.
4. `Cloud credentials` → Cannot access Azure metadata or CLI tokens.
5. `Systemd` → Cannot execute `systemctl` modifications.
6. `Cross-project write` → Filesystem permissions enforce workspace boundaries.
7. `Hook/Policy files` → Owned by `azureuser`, mode `0644` (read-only to agents).

---

## 3. TIMEOUT & FAIL-CLOSED SCIENTIFIC PROTOCOL

### Critical Realization
We CANNOT assume that an Antigravity hook timeout automatically yields a `DENY`.
Official documentation defines hook timeout parameters, but if native CLI behavior defaults to fail-open upon hook execution timeout, the application hook alone cannot provide fail-closed guarantees.

### 6-Scenario Experimental Test Matrix

| Test ID | Hook Scenario | Mechanism | Native Antigravity Behavior | Required System Safe State |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-1** | Explicit Allow | Hook exits 0 with `{"decision": "allow"}` | Tool executes | Tool executes |
| **EXP-2** | Explicit Deny | Hook exits 0 with `{"decision": "deny"}` | Tool blocked with reason | Tool blocked |
| **EXP-3** | Hook Crash | Hook exits 1 / unhandled exception | **Must Test (Likely Fail-Open)** | **DENY (Via Shell Wrapper)** |
| **EXP-4** | Malformed JSON | Hook outputs non-JSON garbage | **Must Test (Likely Fail-Open)** | **DENY (Via Shell Wrapper)** |
| **EXP-5** | Hook Timeout | Hook sleeps past configured timeout | **Must Test (Likely Fail-Open)** | **DENY (Via Timeout Guard)** |
| **EXP-6** | Hook Killed | Hook process receives `SIGKILL` | **Must Test** | **DENY (Via Supervisor)** |

### Fail-Closed Shell Trap Wrapper
To guarantee Fail-Closed even if Python crashes or Antigravity fails open, the hook entrypoint is wrapped in a shell supervisor:
```bash
#!/bin/bash
# Hard fail-closed wrapper
set -euo pipefail
RESULT=$(python3 /home/azureuser/AGY-MASTER/POLICIES/policy_gateway.py 2>/dev/null) || {
    echo '{"decision": "deny", "reason": "🛑 FAIL-CLOSED: Policy gateway crashed or timed out."}'
    exit 0
}
if echo "$RESULT" | jq -e .decision >/dev/null 2>&1; then
    echo "$RESULT"
else
    echo '{"decision": "deny", "reason": "🛑 FAIL-CLOSED: Malformed gateway output."}'
fi
```

---

## 4. OPERATION-AWARE POLICY DEFINITIONS

### 4.1 Docker Operation Granularity
Docker is NOT universally Level 3. The gateway inspects arguments:

| Command | Safety Level | Gateway Decision | Rationale |
| :--- | :--- | :--- | :--- |
| `docker ps`, `docker ps -a` | Level 0 | **ALLOW** | Read-only container observability |
| `docker inspect <id>` | Level 0 | **ALLOW** | Read-only configuration inspection |
| `docker logs <id>` | Level 0 | **ALLOW** | Read-only stdout/stderr inspection |
| `docker build .` | Level 1 / 2A | **ALLOW** | Local project image build (if within boundary) |
| `docker run -v /:/host ...` | Level 3 | **HARD DENY** | Host filesystem mount / root escape attempt |
| `docker run --privileged ...` | Level 3 | **HARD DENY** | Privileged container escape attempt |
| `docker exec -u 0 ...` | Level 3 | **HARD DENY** | Container root privilege escalation |

### 4.2 Git Operation Granularity
Git is NOT universally Level 3. Safe operations are permitted:

| Command | Safety Level | Gateway Decision | Rationale |
| :--- | :--- | :--- | :--- |
| `git status`, `git diff`, `git log` | Level 0 | **ALLOW** | Read-only inspection |
| `git add <file>` | Level 1 / 2A | **ALLOW** | Project-local staging |
| `git commit -m "..."` | Level 2A | **ALLOW** | Project-local atomic checkpoint |
| `git checkout -b <branch>` | Level 1 | **ALLOW** | Safe isolated feature branching |
| `git push` | Level 3 | **HARD DENY** | Autonomous remote modification prohibited |
| `git push --force` | Level 3 | **HARD DENY** | Destructive remote overwrite |
| `git reset --hard` | Level 3 | **HARD DENY** | Destructive uncommitted work loss |
| `git clean -fd` | Level 3 | **HARD DENY** | Unrecoverable file deletion |

---

## 5. HARDENED LEVEL 2A SPECIFICATION ("SINGLE FILE != SAFE")

A single-file modification is ONLY classified as **Level 2A (ALLOW)** if it satisfies ALL 12 conditions simultaneously:

1. **Single File:** The tool call touches exactly one target file.
2. **Approved Project Subtree:** File resides inside the agent's canonical project directory.
3. **Non-Sensitive Path:** Not `/etc`, `/usr`, `/root`, `/home/azureuser/.ssh`, etc.
4. **Non-Policy File:** Not `safety_levels.json`, `policy_gateway.py`, etc.
5. **Non-Hook File:** Not `hooks.json` or any registered hook script.
6. **Non-Secret File:** Not `.env`, `.env.*`, `credentials.json`, `id_rsa`, `token.txt`.
7. **Non-Auth File:** Not password files, auth configs, or OAuth tokens.
8. **Non-Infrastructure File:** Not `Dockerfile`, `docker-compose.yml`, systemd service units.
9. **Non-Dependency File:** Not `package.json`, `package-lock.json`, `Cargo.toml`, `Cargo.lock`, `requirements.txt`.
10. **Non-Schema File:** Not database migrations, DDL files, SQL dump files.
11. **Validated Diff:** Changes are isolated to code functions/classes (no backdoor/eval patterns).
12. **Local Tests Pass:** Project unit tests / syntax checks must be executed and pass.

**Violation of ANY condition escalates the action to Level 2B (DEFAULT DENY) or Level 3 (HARD DENY).**

---

## 6. POLICY SELF-PROTECTION

The Policy Gateway and its configurations are protected against tampering at two distinct levels:
1. **Gateway Interception:**
   - Any `write_to_file`, `replace_file_content`, or `run_command` targeting `hooks.json`, `policy_gateway.py`, `safety_levels.json`, `AGENTS.md` is intercepted and denied with:
     `🛑 HARD DENY: Tampering with policy or hook files is permanently prohibited.`
2. **Filesystem Ownership (OS Level):**
   - Files are owned by `azureuser:azureuser`.
   - File permissions: `chmod 0644 /home/azureuser/AGY-MASTER/POLICIES/*`.
   - Directory permissions: `chmod 0755 /home/azureuser/AGY-MASTER/POLICIES/`.
   - Worker agents running as `agy-worker` have read-only access and cannot write even if gateway is bypassed.

---

## 7. RULE DISTRIBUTION MATRIX (ZERO-BLOAT MAPPING)

| Rule Area | Exact Directive | Source File & Lines | Global AGENTS.md | Master AGENTS.md | Project AGENTS.md | Duplication Status | Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **System Universal** | Rules 1-11, 13-17 (Bengali, Iraq Bhai, paths, no push, tests first) | `/home/azureuser/AGENTS.md` (Lines 1-185) | Authoritative Root | Reference Only | Reference Only | None | Preserve at root |
| **Tri-Agent Model** | Rule 12 Evolution (Ask, Report, Action) | `/home/azureuser/AGY-MASTER/AGENTS.md` (Lines 70-130) | Superseded | Authoritative Specification | Boundary Only | None | Kept in AGY-MASTER |
| **Frappe Domain** | v16+, Python 3.12+, PyPika/frappe.qb, modern form controller, mobile-first | `/home/azureuser/AGENTS.md` (Lines 186-245) | Legacy Bloat | Cataloged | `Frappe-erp-Alco/AGENTS.md` | Duplicate in root | Extract ~60 lines to project file |
| **YouTube Domain** | Veo 3.1 Chrome Extension only, SQLite truth, No FFmpeg/OpenCV | `/home/azureuser/AGENTS.md` (Lines 747-820) | Legacy Bloat | Cataloged | `youtube/AGENTS.md` | Duplicate in root | Extract ~80 lines to project file |
| **Telegram Domain** | Live MTProto / Telethon search only, no local JSON/CSV search fallback | `/home/azureuser/AGENTS.md` (Lines 57-64) | Legacy Bloat | Cataloged | `telegram-bot/AGENTS.md` | Duplicate in root | Extract ~25 lines to project file |
| **Digital History** | OpenRecall daemon protection, run_openrecall.py lifecycle lock | `/home/azureuser/AGENTS.md` (Lines 29-32) | Legacy Bloat | Cataloged | `PERSONAL AI AGENT/AGENTS.md` | Duplicate in root | Extract ~15 lines to project file |

---

## 8. STRICT SEVEN-PHASE IMPLEMENTATION SEQUENCE

```
PHASE A: Gateway Engine & Test Suite Development (Offline, NO hook activation)
    ↓
PHASE B: Adversarial Offline Unit Testing (100% pass on 20+ attack scenarios)
    ↓
PHASE C: PreToolUse Hook Registration in hooks.json (With fail-closed shell trap)
    ↓
PHASE D: Live Non-Destructive Verification (Direct CLI tool calls tested)
    ↓
PHASE E: OS-Level Containment Hardening (Identity separation, sudoers lockdown)
    ↓
PHASE F: Localized Project Rule Injection (Zero-bloat domain sections)
    ↓
PHASE G: Concurrency Engine & Decoupled 3-Tier Verification (flock + independent verify)
```

**ABSOLUTE MANDATE:** No phase shall begin until all verifiable evidence from the preceding phase is recorded and confirmed.
