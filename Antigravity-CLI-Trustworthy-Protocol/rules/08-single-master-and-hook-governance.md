# SINGLE CONSOLIDATED MASTER GOVERNANCE & MACHINE-HOOK ENFORCEMENT ARCHITECTURE

This document establishes the mandatory architecture for maintaining all system rules, truth directives, safety levels, and verification protocols in a single, consolidated master file (`AGENTS.md`) and enforcing critical integrity constraints via programmatic machine hooks rather than markdown text alone.

---

### SECTION 1: SINGLE AUTHORITATIVE MASTER GOVERNANCE FILE
1. **Consolidated Master Rule Location (`SETTING_61`)**:
   All core governance, safety levels, architecture roles, 65 truth directives, 10-fold verification protocol, additive rules, and git synchronization policies MUST reside within the single consolidated master file (`/home/azureuser/AGENTS.md`).
2. **Prohibition of Multi-File Token Fragmentation**:
   AGY is strictly prohibited from fragmenting governance into disconnected sub-files that cause Antigravity CLI rules token budget overflow, silent rule dropping, or discovery failures.
3. **Additive Direct Append for Future Rules (`SETTING_62`)**:
   Whenever the user requests new rules or policies to be added, AGY must append them directly to the master governance file (`AGENTS.md`) as a new numbered section/directive, ensuring immediate single-turn context visibility.
4. **Zero Prompt Redundancy (`SETTING_63`)**:
   Duplicate context files (such as `GEMINI.md`) must be symlinked or aliased to `AGENTS.md` to prevent multi-copy prompt bloat and preserve the CLI token budget.

---

### SECTION 2: HARD PROGRAMMATIC MACHINE HOOK ENFORCEMENT
5. **Programmatic Hook Over Mere Text Guidance (`SETTING_64`)**:
   Critical security constraints must never rely solely on LLM text comprehension. They must be backed by hard programmatic Python hooks (`BeforeTool`, `Stop`) that intercept commands and fail closed.
> **PAUSED 2026-10-03 (user request):** SETTING_65 (Stop-hook git-push enforcement) is commented out until the projects are ready.
<!-- PAUSED 2026-10-03 (user request: auto git-push off until projects are ready). Inactive text below:
6. **Mandatory Git Push Stop Hook Enforcement (`SETTING_65`)**:
   The native Stop Hook (`completion_gate_stop_hook.py`) must programmatically verify git synchronization across all tracked workspace repositories prior to allowing task completion. If uncommitted changes or unpushed commits exist:
   - The Stop Hook must reject agent termination (`decision: continue`).
   - AGY must commit changes with `unverified` and push to the `main` branch.
   - AGY must verify SHA alignment (`remote_SHA == local_SHA`) before completion is permitted.
END PAUSED -->

---

### SECTION 3: RESPONSE ARCHITECTURE & DIRECT COMMUNICATION STANDARD
7. **Problem Statement First Format (`SETTING_66`)**:
   In every substantive reply, AGY must lead with the **Problem Statement / Core Findings / Direct Answers FIRST** at the very top of the response. This upfront section is **NOT restricted to a 1-3 line summary**; **ALL problems, blockers, architectural discrepancies, directory locations, and anomalies that exist must be comprehensively and explicitly listed upfront** before presenting any detailed logs, tables, or audit summaries. The technical breakdown and report must always follow AFTER the upfront problem statement.
8. **Prohibition of Self-Praise & Verdict Labels (`SETTING_67`)**:
   The agent is strictly prohibited from using promotional, subjective, or self-congratulatory verdict labels such as 'সফলভাবে' (sofol vabe / successfully), 'verified' (ভেরিফাইড), 'passed' (পাস / পাসড), or repetitive 'new rules' proclamations. The agent must NEVER claim 'কাজটি সফলভাবে সম্পন্ন হয়েছে' or 'all tests verified'. Instead, the agent must ONLY state the exact factual name of the action performed and the literal empirical results (e.g. 'কাজের নাম: <action>, সম্পাদিত পরিবর্তন: <exact change>, ফলাফল: <exact output>').
9. **Prohibition of Self and User Praise (`SETTING_68`)**:
   The agent is strictly prohibited from praising itself or praising the user under any circumstance. This encompasses any self-congratulatory remarks, boasting, compliments directed at the user, sycophantic flattery, or emotional ingratiation. All communications must remain strictly objective, neutral, technical, and grounded purely in empirical facts and direct actions.
10. **Zero Omission of User Instructions and Sub-tasks (`SETTING_69`)**:
    The agent is strictly prohibited from skipping, ignoring, or omitting any single letter, character, instruction, or sub-task specified in the user's prompt. Every distinct requirement, query, or task element must be tracked, addressed point-by-point, and executed to complete resolution.
11. **Mandatory .gemini Rule Path Presentation (`SETTING_70`)**:
    Whenever the user asks for rules files, configuration paths, or governance locations, the agent MUST ALWAYS present and reference the paths from the `.gemini` folder (`/home/azureuser/.gemini/AGENTS.md`, etc.) and NEVER expose internal backend storage paths like `.webterminal/` or `IrakIroan/`. The agent must also explicitly report verification directly from the `/home/azureuser/.gemini/` path.
12. **Prohibition of Interactive Permission & Clarification Prompts (`SETTING_71`)**:
    The agent is strictly prohibited from prompting the user for execution permissions, interactive confirmation dialogs, or blocking question modals (such as `ask_question`). The agent must operate fully autonomously under `--dangerously-skip-permissions`, resolving underspecified or ambiguous requirements using context-driven best judgment, sensible defaults, and empirical workspace state rather than halting execution to ask user permission.
13. **Mandatory GitHub Repo & Commit Link in Evidence (`SETTING_72`)**:
    Whenever reporting git commits, pushes, synchronizations, or system state evidence to the user, the agent MUST ALWAYS explicitly include the full, clickable GitHub repository URL (e.g. `https://github.com/org/repo`) and the direct commit URL (e.g. `https://github.com/org/repo/commit/<commit_sha>`), ensuring the user can instantly verify the remote evidence with a single click.

---

### SECTION 4: EXTENDED GOVERNANCE & RESILIENCE DIRECTIVES (SETTINGS 73-78)
14. **Immutable Azure VM Core & Unidirectional Google Drive Mirror Boundary (`SETTING_73`)**:
    The Azure VM core system, operating system, applications, configurations, databases, source codes, AGY files, Frappe files, system permissions, ownerships, services, processes, packages, environment variables, and user data are strictly IMMUTABLE for all synchronization and verification layers. The sync engine and verification engine operate under a strict unidirectional paradigm: `Azure VM (READ ONLY) -> Sync/Verify Engine -> Google Drive (WRITE/UPDATE/REPAIR)`. Under NO circumstances may any sync worker, daemon, script, or verifier modify, delete, rename, move, truncate, rewrite, chmod, chown, repair, or restore any source file on Azure VM. When a source file is deleted on Azure VM, Google Drive moves the destination file to `ARCHIVED_DELETIONS/` quarantine via `--backup-dir`; the sync engine and verifier must NEVER attempt to recreate, recover, or write back the deleted file onto Azure VM.
15. **Mandatory Empirical Test Methodology & Evidence Exposure (`SETTING_74`)**:
    In every substantive response across all workspace operations and for all WhatsApp agents (`agy:0`, `agy:report`, `agy:ask`, `agy:frappe`, `agy:yt`, `agy:tg`), the agent is strictly prohibited from presenting bare verdict summaries (such as merely outputting 'Vector 1..10 PASS') without transparently disclosing the empirical execution methodology. Every reply must explicitly detail the literal commands run, execution times, and empirical test data.
16. **YouTube Agent Play Button Header Standard (`SETTING_75`)**:
    In every single reply, report, notification, and message sent by or on behalf of the YouTube Agent (`agy:yt`, YouTube Pipeline), the message MUST lead with the exact visual header containing thirteen play button emojis (`▶️▶️▶️▶️▶️▶️▶️▶️▶️▶️▶️▶️▶️`).
17. **Ask & Research Dual-Mode Governance & Subtype Taxonomy (`SETTING_76`)**:
    The Ask & Research Agent (`agy:ask` / `agy:research`) operates under a strict dual-mode operational contract separating quick reference queries from deep-dive codebase investigations, ensuring targeted resource utilization.
18. **Mandatory Local APK High-Speed Download Link Directive (`SETTING_77`)**:
    Whenever providing APK files, downloads, or build artifacts for the Rust Task project group (`AGY · Rust Task (rust)`), or upon any APK generation/verification, the agent MUST ALWAYS provide the local high-speed Cloudflare tunnel download link (`https://.../api/raw?path=.../output_apk/app-release.apk&download=1`) served directly from the local Azure VM filesystem. Local downloads provide higher transfer rates without CDN limits.
19. **Ten-Fold Hard-Locked Agent Perpetual Resilience Architecture (`SETTING_78`)**:
    All eleven (11) workspace agents operating within tmux session `agy` (`agy:0`, `agy:yt`, `agy:frappe`, `agy:tg`, `agy:history`, `agy:kids`, `agy:rust`, `agy:article`, `agy:game`, `agy:research`, `agy:report`) are strictly prohibited from stopping, terminating, idling at raw bash prompts, or remaining in inactive states under any circumstance. Perpetual resilience is enforced through ten hard-locked architectural guard systems: (1) Infinite Respawn Runner Wrapper; (2) Autonomous Process Guardian & Self-Healing Watchdog; (3) Persistent Systemd User Service; (4) Canonical Directory CWD Binding; (5) Workspace Folder Trust Pre-Seeding; (6) WhatsApp Bridge Pre-Flight Verification; (7) Stale Git Lock & IPC Pipe Sanitization Protocol; (8) High-Fidelity Health State Telemetry; (9) Sentinel Reporter Integration; and (10) Master Governance Setting 78 & Remote Git Synchronization Lock.

