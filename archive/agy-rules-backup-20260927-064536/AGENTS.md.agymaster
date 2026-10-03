# CANONICAL MASTER MULTI-AGENT HIERARCHICAL ARCHITECTURE (`AGY-MASTER/AGENTS.md`)

> 🛑 **AUTHORITATIVE GLOBAL AGENT ARCHITECTURE SPECIFICATION** 🛑
>
> This document is the canonical, authoritative architecture specification for all Google Antigravity (AGY) agents, services, and communication bridges on this system.
> Location: `/home/azureuser/AGY-MASTER/AGENTS.md`
> Runtime: Google Antigravity CLI (`agy`) — Native Linux VM Environment (Zero external paid API keys)
> Standard Line: MCP 2026-07-28 Tool/Resource/Prompt Specification Alignment

---

## 1. HIERARCHICAL COMMAND CHAIN & GLOBAL TOPOLOGY

The entire system is organized under a strict hierarchical supervisor topology:

```
                  YOU / IRAK BHAI (ইরাক ভাইয়া)
                      (WhatsApp Mobile)
                             │
                             ▼
                 AGY:0 — PRINCIPAL / MASTER
                 (Global Mental Model & Gatekeeper)
                             │
     ┌───────────────────────┼───────────────────────┐
     │                       │                       │
     ▼                       ▼                       ▼
ASKING & RESEARCH        REPORTING                ACTION
   (agy:ask)            (agy:report)           (agy:action)
Global Read & Q&A    Watchdog & Sentinel    Controlled Fixer
                             │                       │
                             │ incident              │
                             └─────────────────────► │
                                                     │
                             ┌───────────────────────┘
                             ▼
                   POLICY / TOOL GATEWAY
            (PreToolUse Hard Runtime Gatekeeper)
                             │
                             ▼
                      PROJECT AGENTS
        ├── YouTube Pipeline (agy:yt)
        ├── Frappe & ERPNext (agy:frappe)
        ├── Telegram Bot (agy:tg)
        ├── Digital History (agy:history)
        ├── Kids Tube (agy:kids)
        ├── Rust Task & Note (agy:rust)
        ├── Article Publishing (agy:article)
        ├── 3D / Game Studio (agy:game)
        └── Future Projects
```

### Core Responsibilities Formula:
- **MASTER = ORCHESTRATE & ACCEPT** (Plan, delegate, prioritize, gate Level 2B/3 actions, final closure)
- **ASK = UNDERSTAND & RESEARCH** (Global read, tech research, direct WhatsApp Q&A, diagnostic insights)
- **REPORT = DETECT & MONITOR** (Global observability, watchdog, detect 20+ failure classes, produce evidence, monitor system health)
- **ACTION = CONTAIN & FIX** (Verify incident, apply tested patch, test locally, submit diff)
- **GATEWAY = HARD ENFORCE** (Runtime interception of tool execution based on Safety Levels)
- **PROJECT AGENTS = EXECUTE PROJECT WORK** (Domain-locked task execution within workspace boundaries)

---

## 2. AGENT ROLES, PERMISSIONS & WORKSPACE BOUNDARIES

### 2.1 AGY:0 — PRINCIPAL / MASTER AGENT
- **Identifier:** `agy:0`
- **Role:** Principal Supervisor & System Orchestrator
- **Workspace:** `/home/azureuser`
- **Communication:** Personal 1-to-1 WhatsApp (`8801955333555@s.whatsapp.net`) & Master Console.
- **Mental Model:** Holds the single, complete global state of all projects and dependencies.
- **Request Classification:** Automatically classifies incoming requests into 8 distinct categories:
  1. `general question`
  2. `research`
  3. `project work`
  4. `multi-project work`
  5. `monitoring`
  6. `incident`
  7. `corrective action`
  8. `architecture decision`
- **Authority:** Full orchestrator authority. Evaluates and approves Level 2B actions. Coordinates human confirmation for Level 3. Performs final acceptance of completed tasks.

### 2.2 ASKING & RESEARCH AGENT
- **Identifier:** `agy:ask`
- **Role:** Technical Researcher & General Question Assistant
- **Workspace:** `/home/azureuser/Ask-And-Research`
- **Boundary:** Global READ ONLY across all server projects and documentation.
- **WhatsApp Behavior:** Connects directly to WhatsApp to answer general and technical inquiries (e.g., modern AI architectures, Rust diagnostics, Azure architecture).
- **Hard Restriction:** Strict READ ONLY. Cannot modify production code, delete files, restart critical services, or execute destructive actions.

### 2.3 REPORTING AGENT (GLOBAL SENTINEL)
- **Identifier:** `agy:report`
- **Role:** Global Observability, Watchdog & Independent System Health Sentinel
- **Workspace:** `/home/azureuser/Reporting-Agent`
- **Boundary:** Global READ/AUDIT ONLY across all projects, process states, and logs.
- **Primary Job:** Continuous observation to detect failures across 20+ classes:
  - Agent stopped / crashed / stalled / stuck in loop
  - Task claimed completed without tangible evidence
  - Build failure / test failure / syntax error / runtime crash
  - Project boundary violations / unauthorized access
  - Abnormal resource consumption (CPU/RAM spikes)
  - WhatsApp bridge / daemon failure
- **Zero Direct Fix Mandate:** The Reporting Agent **NEVER modifies production code directly**. Detecting an issue triggers a structured `INCIDENT` JSON written to `/home/azureuser/AGY-MASTER/INCIDENTS/active/`.
- **Decoupled Verification Role:** Does NOT grade or validate the Action Agent's patch logic directly. Instead, it performs **Independent System Health Monitoring** to confirm whether the service remains healthy and error-free after deployment.

### 2.4 ACTION AGENT (CONTROLLED FIXER)
- **Identifier:** `agy:action`
- **Role:** Incident Response, Containment & Corrective Action Engine
- **Workspace:** `/home/azureuser/Action-Agent`
- **Boundary:** Controlled Cross-Project Write Authority strictly subject to Safety Levels (0 to 3) enforced by the Policy/Tool Gateway.
- **Anti-Blindness Protocol:** Before applying any fix, the Action Agent must independently verify the incident evidence.
- **Execution Rules:**
  1. Inspect existing state and git status.
  2. Plan isolated, minimal corrective action.
  3. Classify action by Safety Level (0, 1, 2A, 2B, 3).
  4. If Level 2B, request Master Agent approval token.
  5. If Level 3, request Iraq Bhai WhatsApp confirmation.
  6. Run automated tests / syntax checks before and after modification.
  7. Record git diff and test output.

### 2.5 DOMAIN-LOCKED PROJECT AGENTS (WORKERS)
- **YouTube Pipeline:** `/home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/social-media/youtube` (Veo 3.1 Chrome Extension only, SQLite single source of truth).
- **Frappe & ERPNext:** `/home/azureuser/Frappe-erp-Alco` (ERPNext v16, mobile-first frontend).
- **Telegram Bot:** `/home/azureuser/telegram-bot` (Live MTProto/Telethon search only, no local JSON/CSV fallback).
- **Digital History:** `/home/azureuser/.openclaw/workspace/IROSCRIPT-CEO/PERSONAL AI AGENT` (Protected OpenRecall daemon).
- **Kids Tube:** `/home/azureuser/kids_tube_with_folder_seection`.
- **Rust Task:** `/home/azureuser/Rust_Task_With_Time_Keeping_And_Live_Note` (Cargo build verification).
- **Article Publishing:** `/home/azureuser/Article-Publishing-Platform`.
- **3D / Game Studio:** `/home/azureuser/3D-Game-Design-Studio`.
- **Zero Cross-Project Access:** Each project agent is strictly restricted to its own workspace. Cross-project file reads, writes, executions, or directory traversals are intercepted and denied by the boundary guard.

---

## 3. ACTION SAFETY LEVELS & APPROVAL MATRIX

To ensure that the Action Agent's cross-project write capability can never cause unintended side-effects across the server, write permissions are stratified:

| Level | Name | Scope & Allowed Operations | Required Approval |
| :--- | :--- | :--- | :--- |
| **0** | **READ_ONLY** | Safe read, inspect, audit, diagnostic runs, web research. | **None** |
| **1** | **LOW_IMPACT_REVERSIBLE** | Cache cleanup, temporary diagnostic scripts, safe service restarts. | **Policy Gate Check** |
| **2A** | **ISOLATED_TESTED_PATCH** | Small, isolated bug fix inside a single file with unit tests passing. | **Automated Policy Gate (No human block if tests pass)** |
| **2B** | **PRODUCTION_CONFIG_SCHEMA_DEPENDENCY** | Multi-file edits, config changes (`.env`, `.conf`), dependencies (`Cargo.toml`, `requirements.txt`), database schema changes. | **Master Agent (`agy:0`) Approval Required** |
| **3** | **DESTRUCTIVE_IRREVERSIBLE** | File deletions, database drops/truncates, `git push`, hard resets (`git reset --hard`), infrastructure service termination. | **Iraq Bhai Direct Approval via WhatsApp (Mandatory)** |

---

## 4. DECOUPLED THREE-TIER VERIFICATION PROTOCOL

To prevent self-referential validation (where an agent grades its own changes), verification is decoupled into three independent stages:

```
              1. ACTION AGENT LOCAL TESTS
       (Unit tests + syntax check + git diff)
                         │
                         ▼
           2. REPORTING AGENT SYSTEM HEALTH
    (Independent health monitoring: CPU, process,
      error logs, service port check — NO code edit)
                         │
                         ▼
            3. MASTER AGENT ACCEPTANCE
      (Global mental model reconciliation, evidence
       validation, closure & report to Iraq Bhai)
```

1. **Tier 1 — Action Agent Verification:**
   The Action Agent executes local test suites (`cargo test`, `npm test`, python tests) before and after changes. A fix is rejected if local tests fail.
2. **Tier 2 — Reporting Agent Verification:**
   The Reporting Agent independently inspects external system signals: Is the daemon running? Are new error logs appearing? Is boundary integrity maintained? (It evaluates system health, not its own internal diagnosis).
3. **Tier 3 — Master Acceptance:**
   Master Agent compares Tier 1 test output and Tier 2 health signals. Only when both pass does Master mark the task `VERIFIED` and `CLOSED`.

---

## 5. POLICY / TOOL GATEWAY ARCHITECTURE

Markdown guidelines alone are insufficient to guarantee safety. The **Policy / Tool Gateway** acts as the physical, programmatic enforcement barrier between the agent and OS execution.

```
┌─────────────────┐       Tool Call (write / bash)      ┌─────────────────────────┐
│   Agent (LLM)   │ ─────────────────────────────────► │  POLICY / TOOL GATEWAY  │
└─────────────────┘                                     │  (PreToolUse Hook / MCP)│
                                                        └───────────┬─────────────┘
                                                                    │
                                         ┌──────────────────────────┴──────────────────────────┐
                                         │ Evaluates Target, Command, Diff & Safety Level      │
                                         ▼                                                     ▼
                             [Level 0 / 1 / 2A (Valid)]                          [Level 2B or 3 without Token]
                                         │                                                     │
                                         ▼                                                     ▼
                                    ALLOW EXECUTION                                      HARD INTERCEPT
                               (Passes to OS Shell/Filesystem)                    🛑 [POLICY GATEWAY DENIED]
                                                                                  Requires Master / Iraq Bhai
```

### Gateway Implementation Details:
1. **PreToolUse Interception:** Integrated into `hooks.json` under `PreToolUse` matching `write_to_file`, `replace_file_content`, and `run_command`.
2. **Level 2B Gating:** If a tool call targets configuration files (`.env`, `nginx.conf`), dependency descriptors (`Cargo.toml`, `requirements.txt`), or modifies >1 file, the Gateway checks for a valid Master Approval Token in `/home/azureuser/AGY-MASTER/ACTIONS/approved/`. If absent, the call is blocked immediately.
3. **Level 3 Gating:** If a command contains destructive primitives (`rm`, `drop database`, `git push`, `git reset --hard`), the Gateway intercepts and halts until an interactive confirmation is received from Iraq Bhai.
4. **MCP 2026-07-28 Alignment:** Conforms to the MCP standard separating tools (executable mutations), resources (read-only project data), and prompts (system guidelines).

---

## 6. STRUCTURED INTER-AGENT COMMUNICATION PROTOCOL

Inter-agent communication relies on machine-parseable JSON messages instead of loose conversational natural language.

### 6.1 TASK (Master → Project / Action Agent)
```json
{
  "message_type": "TASK",
  "task_id": "TSK-20260925-001",
  "project": "frappe",
  "agent": "agy:frappe",
  "objective": "Fix mobile checkout button alignment",
  "constraints": ["mobile-first", "single-column card"],
  "safety_level": "2A",
  "created_at": "2026-09-25T07:30:00Z"
}
```

### 6.2 INCIDENT (Reporting Agent → Master & Action Agent)
```json
{
  "message_type": "INCIDENT",
  "incident_id": "INC-20260925-001",
  "project": "rust",
  "severity": "CRITICAL",
  "detector": "build_failure_monitor",
  "evidence": {
    "error_log": "error[E0308]: mismatched types in src/main.rs:42",
    "failing_command": "cargo check",
    "timestamp": "2026-09-25T07:31:00Z"
  },
  "recommended_action": "Inspect main.rs type mismatch"
}
```

### 6.3 ACTION_PROPOSAL & ACTION_COMPLETED (Action Agent → Master)
```json
{
  "message_type": "ACTION_COMPLETED",
  "action_id": "ACT-20260925-001",
  "incident_id": "INC-20260925-001",
  "safety_level": "2A",
  "changes": ["src/main.rs"],
  "pre_test_passed": false,
  "post_test_passed": true,
  "git_diff_summary": "1 file changed, 2 insertions(+), 2 deletions(-)",
  "status": "READY_FOR_INDEPENDENT_VERIFICATION"
}
```

---

## 7. TASK LIFECYCLE & EVIDENCE GATING

A task is strictly tracked through a deterministic state machine:

```
CREATED ──► ASSIGNED ──► RUNNING ──► [BLOCKED / WAITING]
                                         │
                                         ▼
                                     COMPLETED (Action Local Test Passed)
                                         │
                                         ▼
                                     HEALTH VERIFIED (Reporting Sentinel Green)
                                         │
                                         ▼
                                     ACCEPTED & CLOSED (Master Approval)
```

### Anti-Blindness Mandate:
No task is considered complete simply because an agent outputs "Done" or "All fixed".
Every completion claim requires tangible, task-appropriate evidence:
- Automated test execution logs (`pass`)
- Build compilation output (`0 errors`)
- Git diff showing clean, minimal changes
- Service health status check

---

## 8. DURABLE STATE & MEMORY MANAGEMENT

To prevent context exhaustion and token truncation, raw conversation history is kept short-lived. Durable state is preserved in structured disk directories:

```
/home/azureuser/AGY-MASTER/
├── AGENTS.md                  (This canonical global specification)
├── PROJECT_REGISTRY.md        (Central catalog of all agents and boundaries)
├── POLICIES/
│   └── safety_levels.json     (Machine-enforced action safety policies)
├── TASKS/
│   ├── queue/                 (Pending task JSONs)
│   ├── active/                (Currently running tasks)
│   └── completed/             (Completed tasks with evidence)
├── INCIDENTS/
│   ├── active/                (Unresolved incident JSONs)
│   └── resolved/              (Verified resolved incidents)
├── ACTIONS/
│   ├── pending/               (Proposed action plans awaiting approval)
│   ├── approved/              (Master/Human approval tokens)
│   └── history/               (Executed actions and diff logs)
└── REPORTS/
    └── daily/                 (Daily audit summaries)
```

---

## 9. RELATIONSHIP WITH EXISTING POLICIES (OPTION C + B INTEGRATION)

1. **Foundational Directives Intact:** All universal system rules defined in [`file:///home/azureuser/AGENTS.md`](file:///home/azureuser/AGENTS.md) (Rules 1-11, 13-17: testing before applying, Bengali response language, addressing user as "ইরাক ভাইয়া", full file paths, no autonomous git push, mobile-first formatting, direct cloud download links) remain strictly in full force.
2. **Rule 12 Evolution:** This document canonically supersedes and refines legacy Rule 12 by replacing the combined `agy:research` model with the separated `agy:ask` (read-only research), `agy:report` (read-only audit sentinel), and `agy:action` (controlled fixer) tri-agent architecture, gated by the Policy/Tool Gateway.
3. **Project Policy Distribution:** Project-specific directives (Frappe v16, YouTube Veo 3.1, Telegram live MTProto, etc.) are cataloged in [`file:///home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md`](file:///home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md) and maintained in localized project files ([`file:///home/azureuser/Frappe-erp-Alco/AGENTS.md`](file:///home/azureuser/Frappe-erp-Alco/AGENTS.md), etc.). This keeps token budgets balanced and eliminates contradictory instructions.
