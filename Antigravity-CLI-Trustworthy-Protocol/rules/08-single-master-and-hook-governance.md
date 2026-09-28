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
   Critical security, delete prevention, and synchronization constraints must never rely solely on LLM text comprehension. They must be backed by hard programmatic Python hooks (`BeforeTool`, `Stop`) that intercept commands and fail closed.
6. **Mandatory Git Push Stop Hook Enforcement (`SETTING_65`)**:
   The native Stop Hook (`completion_gate_stop_hook.py`) must programmatically verify git synchronization across all tracked workspace repositories prior to allowing task completion. If uncommitted changes or unpushed commits exist:
   - The Stop Hook must reject agent termination (`decision: continue`).
   - AGY must commit changes with `unverified` and push to the `main` branch.
   - AGY must verify SHA alignment (`remote_SHA == local_SHA`) before completion is permitted.
