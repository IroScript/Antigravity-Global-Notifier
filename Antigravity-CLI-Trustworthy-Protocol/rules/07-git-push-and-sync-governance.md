# GIT PUSH, REMOTE REPOSITORY SYNC & COMMIT HISTORY GOVERNANCE

This document establishes the mandatory operational rules for remote Git synchronization, commit messaging standards, branch targeting, tree integrity verification, and immutable commit history preservation across Google Antigravity CLI (`agy`) environments.

---

### SECTION 1: POST-EDIT GIT PUSH & COMMIT MESSAGE SPECIFICATION
1. **Mandatory Post-Edit Remote Push**:
   Following any code creation, modification, or configuration edit in tracked repositories, AGY must immediately commit and push the changes to the remote Git repository.
2. **Automatic Post-Edit Commit Message**:
   For automated post-edit pushes performed without explicit user push requests, the commit message MUST be formatted as **`unverified`** (or prefixed with `unverified:`).
3. **Explicit User-Requested Push Attribution**:
   When the USER explicitly commands to push (e.g., *"Gitpush"*, *"Push koro"*, *"Git push"*), the commit message MUST explicitly disclose that the Gitpush request originated directly from the user (e.g., `feat: <description> (User-requested gitpush)` or `User-requested gitpush: <summary>`).

---

### SECTION 2: MANDATORY `main` BRANCH TARGETING & SHA-1 ALIGNMENT
4. **Target Branch Restriction**:
   All pushes must target the **`main`** branch unless the user explicitly orders a different named branch.
5. **Two-Point SHA Alignment Verification**:
   Immediately after every push execution, AGY must run both of the following inspection commands to verify SHA alignment:
   - Local HEAD SHA: `git rev-parse HEAD`
   - Remote Branch SHA: `git ls-remote origin main`
6. **Strict SHA Equality Assertion**:
   AGY must compare both SHA-1 values. Remote GitHub SHA MUST strictly equal local HEAD SHA (`remote_SHA == local_SHA`). If a discrepancy or lag is detected, it must be reported immediately as a failure or pending sync state.

---

### SECTION 3: LOCAL VS REMOTE TRACKED TREE INTEGRITY & ONLINE DISCLOSURE
7. **Tracked Tree Structure & Content Verification**:
   AGY must verify that all locally tracked files and folders match the tracked file tree on the remote GitHub repository (via GitHub API, `git ls-tree`, or comparative tree inspection).
8. **Transparent Disclosure If Online Verification Is Impeded**:
   If remote online verification cannot be completed (e.g., network timeout, API rate limit, credential barrier, or service outage), AGY is strictly forbidden from pretending the check passed. AGY MUST explicitly explain to the user:
   - Exactly why online verification was not possible.
   - The verbatim error message or status code received.
   - The local fallback status and exact unverified vectors.

---

### SECTION 4: COMMIT HISTORY IMMUTABILITY & EMPIRICAL EVIDENCE
9. **Zero History Rewrite / Force-Push Ban**:
   AGY is strictly prohibited from:
   - Force-pushing (`git push --force`, `git push -f`, `git push --force-with-lease`).
   - History rewriting (`git commit --amend` on pushed commits, `git rebase -i`, `git filter-branch`).
   - Destructive branch reset (`git reset --hard`).
   - Commit or history deletion (`git push origin --delete`).
10. **Mandatory Machine Evidence in Sync Reports**:
    Every Git synchronization report must provide empirical machine evidence:
    - Target repository remote URL.
    - Commit SHA and message.
    - Local vs Remote SHA alignment proof.
    - Exact exit codes of `git push`, `git ls-remote`, and `git rev-parse`.
