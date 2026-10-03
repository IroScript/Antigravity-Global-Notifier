# ADDITIVE GOVERNANCE, AUTOMATIC GLOBAL DEFAULTS & RUNTIME LOAD VERIFICATION

This document establishes the mandatory governance protocols for adding, propagating, and verifying rules across Google Antigravity CLI (`agy`) environments.

---

### SECTION 1: OFFICIAL-DOC-FIRST BASIS
1. **Authoritative Documentation Precedence**:
   Every new rule, lifecycle hook, configuration, or CLI customization must be grounded directly in the official Google Antigravity documentation archived at [`/home/azureuser/IrakIroan/IroScript_Projects/Antigravity-CLI-Trustworthy-Protocol/docs/antigravity/`](file:///home/azureuser/IrakIroan/IroScript_Projects/Antigravity-CLI-Trustworthy-Protocol/docs/antigravity/).
2. **Zero Fabricated Configuration Assumptions**:
   AGY must never invent configuration keys (such as assumptions from other tools). All configurations must conform strictly to official Antigravity CLI contracts (`rules.md`, `hooks.md`, `settings.json`).

---

### SECTION 2: ADDITIVE-ONLY RULE EVOLUTION
3. **Strict Prohibition of Rule Modification or Deletion**:
   Once a user-approved rule or policy is established in the workspace, AGY is strictly forbidden from modifying, weakening, replacing, substituting, or deleting it.
4. **Append-Only Additive Mechanism**:
   Any new user requirement must be appended as a new rule or directive. Existing rules retain 100% of their original wording and authority.
5. **Explicit User Override Gate**:
   A pre-existing rule may only be modified, replaced, or retired if the USER explicitly issues a command containing unambiguous terms: "modify rule X", "replace rule Y", or "delete rule Z".

---

### SECTION 3: AUTOMATIC GLOBAL DEFAULT FOR UNSPECIFIED PROJECT PROMPTS
6. **Default Global Assumption**:
   Whenever the USER instructs to add, set, or enforce rules (e.g., *"New rules add koro: ..."*, *"Rules set koro: ..."*, *"Add rule: ..."*) without explicitly specifying a project directory name, AGY MUST unconditionally classify and apply the rule as a **GLOBAL WORKSPACE RULE**.
7. **Single Source of Truth Target**:
   All such rules must be added directly into the central source-of-truth repository:
   [`/home/azureuser/IrakIroan/IroScript_Projects/Antigravity-CLI-Trustworthy-Protocol/`](file:///home/azureuser/IrakIroan/IroScript_Projects/Antigravity-CLI-Trustworthy-Protocol/)
   under `rules/` and indexed in `governance/AGENTS.md`.

---

### SECTION 4: AUTOMATIC CONTEXT PROPAGATION & MANDATORY LOAD EVIDENCE
8. **Immediate Runtime Symlink Binding**:
   When any new rule file is created in `rules/`, AGY must immediately symlink it into `/home/azureuser/.agents/rules/<rule-name>.md`.
   Because Antigravity CLI automatically discovers and loads all `.md` files in `.agents/rules/` on every conversation turn, this ensures zero-latency runtime propagation.
9. **Mandatory Load Verification Evidence**:
   AGY must never merely state that a rule was added. AGY must provide empirical machine evidence:
   - Target file physical existence and non-zero byte size (`stat` / `ls -l`).
   - Active symlink resolution (`readlink -f`).
   - SHA-256 cryptographic checksum.
   - Successful execution of 10-fold verification (`verify_10_fold.py`) confirming the rule is active and bound.

---

### SECTION 5: SCOPED PRIVILEGED OPERATIONS (NO GLOBAL UNBLOCKING)
10. **Prohibition of Global Destructive Exemptions**:
    No global unblocking of `sudo` / privilege escalation is permissible. (`rm` part removed 2026-10-03 - user request)
11. [REMOVED 2026-10-03 - user request: delete rules no longer needed]

---

### SECTION 6: INSTRUCTION-SOURCE CONTROL
12. **Authoritative Context Boundaries**:
    Only global configuration in `~/.gemini/`, workspace root `/home/azureuser/AGENTS.md`, and active rule files in `~/.agents/rules/*.md` are recognized as authoritative instructions.
13. **Rejection of Residual Subdirectory Instructions**:
    Residual or backup instruction files found in `old/`, `GLOBAL-ARCHIVE/`, or scratch testing directories are non-authoritative and must never be permitted to override or influence workspace governance.
