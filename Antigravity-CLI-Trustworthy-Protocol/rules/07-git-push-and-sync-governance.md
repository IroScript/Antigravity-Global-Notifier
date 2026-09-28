# GIT PUSH, REMOTE REPOSITORY SYNC & COMMIT HISTORY GOVERNANCE

This document establishes the mandatory operational rules for remote Git synchronization, commit messaging standards, branch targeting, repository pre-validation, ambiguity prevention, tree integrity verification, and immutable commit history preservation across Google Antigravity CLI (`agy`) environments.

---

### SECTION 1: POST-EDIT GIT PUSH & COMMIT MESSAGE SPECIFICATION
1. **Mandatory Post-Edit Remote Push**:
   Following any code creation, modification, or configuration edit in tracked repositories, AGY must immediately commit and push the changes to the remote Git repository.
2. **Automatic Post-Edit Commit Message**:
   For automated post-edit pushes performed without explicit user push requests, the commit message MUST be formatted as **`unverified`** (or prefixed with `unverified:`).
3. **Explicit User-Requested Push Attribution**:
   When the USER explicitly commands to push (e.g., *"Gitpush"*, *"Push koro"*, *"Git push"*), the commit message MUST explicitly disclose that the Gitpush request originated directly from the user (e.g., `feat: <description> (User-requested gitpush)` or `User-requested gitpush: <summary>`).

---

### SECTION 2: REPOSITORY PRE-VALIDATION, MULTI-REPO DISAMBIGUATION & `main` BRANCH TARGETING
4. **Mandatory Repository Pre-Inspection**:
   Prior to executing any push, AGY must verify:
   - Physical existence of a valid `.git` directory in the target project root (`git rev-parse --is-inside-work-tree`).
   - Configured and reachable remote URL (`git remote -v`).
5. **Zero-Guessing Multi-Repository & Ambiguity Guard**:
   Because multiple projects may be interlinked or nested across workspaces:
   - If `.git` or a valid remote connection is missing, OR
   - If multiple candidate Git repositories exist for the target files/project,
   AGY is **STRICTLY FORBIDDEN from guessing or assuming which repository to push to**. AGY must immediately pause and explicitly ask the USER to specify the intended target repository.
6. **Mandatory `main` Branch Target**:
   All pushes must target the **`main`** branch unless the user explicitly orders a different named branch.

---

### SECTION 3: POST-PUSH SHA ALIGNMENT & TRACKED TREE INTEGRITY
7. **Two-Point SHA Alignment Verification**:
   Immediately after every push execution, AGY must run both of the following inspection commands to verify SHA alignment:
   - Local HEAD SHA: `git rev-parse HEAD`
   - Remote Branch SHA: `git ls-remote origin main`
8. **Strict SHA Equality Assertion**:
   AGY must compare both SHA-1 values. Remote GitHub SHA MUST strictly equal local HEAD SHA (`remote_SHA == local_SHA`). If a discrepancy or lag is detected, it must be reported immediately as a failure or pending sync state.
9. **Tracked Tree Structure & Content Verification**:
   AGY must verify that all locally tracked files and folders match the tracked file tree on the remote GitHub repository (via GitHub API, `git ls-tree`, or comparative tree inspection).
10. **Transparent Disclosure If Online Verification Is Impeded**:
    If remote online verification cannot be completed (e.g., network timeout, API rate limit, credential barrier, or service outage), AGY is strictly forbidden from pretending the check passed. AGY MUST explicitly explain to the user:
    - Exactly why online verification was not possible.
    - The verbatim error message, HTTP status code, or command failure received.
    - The local fallback status and exact unverified vectors.

---

### SECTION 4: COMMIT HISTORY IMMUTABILITY & VERIFICATION EVIDENCE
11. **Zero History Rewrite / Force-Push Ban**:
    AGY is strictly prohibited from:
    - Force-pushing (`git push --force`, `git push -f`, `git push --force-with-lease`).
    - History rewriting (`git commit --amend` on pushed commits, `git rebase -i`, `git filter-branch`).
    - Destructive branch reset (`git reset --hard`).
    - Commit or history deletion (`git push origin --delete`).
12. **Mandatory Empirical Evidence & Disclosure**:
    If any verification vector or check cannot be fully executed, AGY must never conceal or gloss over the omission. AGY must explicitly report:
    - The specific reason why the verification could not be completed.
    - All available machine evidence and test outputs collected so far.
