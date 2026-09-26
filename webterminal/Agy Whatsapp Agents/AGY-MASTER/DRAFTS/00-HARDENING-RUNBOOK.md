# DELETE-PROOF HARDENING RUNBOOK & DEPLOYMENT CHECKLIST

Target Host: Azure VM `FatehAli` (Debian/Ubuntu, Kernel: 6.12.107+deb13-cloud-amd64)  
Target User: `azureuser` (UID: 1000, GID: 1000)  
Classification: PRODUCTION SYSTEM HARDENING RUNBOOK (FAIL-SAFE / ZERO-LOCKOUT PROTOCOL)  
Created: 2026-09-26  
Status: READY FOR HUMAN-IN-THE-LOOP EXECUTION  

---

> 🛑 **SAFETY FIRST MANDATE:**  
> Do NOT execute these steps blindly or in a single batch.  
> Execute **ONE step at a time**, verify the **Expected Output**, and confirm before proceeding to the next step.  
> If any step produces an error, HALT immediately and use the **Rollback Procedure** listed in that section.

---

## RUNBOOK OVERVIEW & EXECUTION PHASES

```
[ PHASE 0: SAFETY NETS ]
  Step 1: Azure VM Disk Snapshot (Azure Portal)
  Step 2: Open Azure Serial Console (Browser Tab)
         │
         ▼
[ PHASE 1: LEAST-PRIVILEGE SUDOERS DEPLOYMENT ]
  Step 3: Syntax Validation via visudo
  Step 4: Install 99-azureuser-restricted (Coexistence mode)
  Step 5: Two-Session Verification Test
  Step 6: Deactivate 90-cloud-init-users (Wildcard Removal)
         │
         ▼
[ PHASE 2: FILESYSTEM & DIRECTORY LOCKING ]
  Step 7: Pre-create Subdirs + File Immutability + Directory Lock (+i)
         │
         ▼
[ PHASE 3: FINAL INDEPENDENT VERIFICATION ]
  Step 8: Execute 05-verification-tests.sh (7/7 PASS Mandate)
```

---

## PHASE 0: SAFETY NETS (EXTERNAL ROLLBACK INSURANCE)

### [ ] STEP 1: Create an Azure VM Disk Snapshot
- **Where:** Azure Portal (https://portal.azure.com)
- **Why:** If sudoers or filesystem permissions break the VM, restoring from snapshot takes under 3 minutes.
- **Action:**
  1. Go to **Virtual Machines** -> **FatehAli** -> **Disks**.
  2. Click on the **OS Disk**.
  3. Click **+ Create Snapshot**.
  4. Settings:
     - Name: `FatehAli-PreHardening-Snapshot`
     - Snapshot type: `Full`
     - Storage type: `Standard HDD` or `Standard SSD`
  5. Click **Review + create** -> **Create**.
- **Verification:** Snapshot status displays `Succeeded`.

---

### [ ] STEP 2: Open an Active Azure Serial Console Session
- **Where:** Azure Portal in a separate browser tab.
- **Why:** The Azure Serial Console connects directly to the VM's hardware ttyS0 kernel pipe. It bypasses SSH, network, and standard sudoers, allowing direct emergency root recovery if SSH or sudo breaks.
- **Action:**
  1. In Azure Portal, navigate to **FatehAli** -> **Help + troubleshooting** -> **Serial console**.
  2. Wait until the terminal prompt appears (`FatehAli login:`).
  3. Keep this browser tab open side-by-side throughout the entire procedure.

---

## PHASE 1: LEAST-PRIVILEGE SUDOERS DEPLOYMENT

### [ ] STEP 3: Independently Validate Sudoers Draft Syntax
- **Where:** Your existing SSH terminal on `FatehAli`.
- **Action:** Run the syntax validator as your own check:
  ```bash
  /usr/sbin/visudo -c -f /home/azureuser/AGY-MASTER/DRAFTS/01-sudoers-restricted.draft
  ```
- **Expected Output:**
  ```text
  /home/azureuser/AGY-MASTER/DRAFTS/01-sudoers-restricted.draft: parsed OK
  ```
  *Exit code must be `0`.*
- 🛑 **Gate:** If it does NOT print `parsed OK`, STOP! Do not proceed.

---

### [ ] STEP 4: Install Restricted Sudoers in Coexistence Mode
- **Where:** SSH terminal on `FatehAli`.
- **Note:** We install the new rule file, but leave the old `90-cloud-init-users` intact for now so you cannot be locked out while testing.
- **Action:**
  ```bash
  sudo cp /home/azureuser/AGY-MASTER/DRAFTS/01-sudoers-restricted.draft /etc/sudoers.d/99-azureuser-restricted
  sudo chmod 0440 /etc/sudoers.d/99-azureuser-restricted
  sudo visudo -c
  ```
- **Expected Output:**
  ```text
  /etc/sudoers: parsed OK
  /etc/sudoers.d/90-cloud-init-users: parsed OK
  /etc/sudoers.d/99-azureuser-restricted: parsed OK
  ```

---

### [ ] STEP 5: Two-Session Test Protocol
- **Action:**
  1. **DO NOT close your current SSH terminal.**
  2. Open a **SECOND** brand-new SSH terminal window from your computer:
     ```bash
     ssh azureuser@20.55.42.128
     ```
  3. In the second terminal, inspect active privileges:
     ```bash
     sudo -l
     ```
- **Verification:**
  - Verify that `NOEXEC: NOPASSWD:` appears associated with `APT_CMNDS`, `SYSTEMCTL_CMNDS`, and `DOCKER_CMNDS`.

---

### [ ] STEP 6: Deactivate Wildcard Sudo (`90-cloud-init-users`)
- **Where:** Primary SSH terminal.
- **Why:** This closes the critical trust-boundary flaw (`azureuser ALL=(ALL) NOPASSWD:ALL`).
- **Action:**
  ```bash
  # Rename cloud-init sudoers file to disable it safely without deleting
  sudo mv /etc/sudoers.d/90-cloud-init-users /etc/sudoers.d/90-cloud-init-users.disabled
  ```
- **Immediate Verification (Run in Second Terminal):**
  ```bash
  # 1. Broad root test (MUST FAIL):
  sudo -n whoami
  # Expected Output: sudo: a password is required OR sudo: user NOT in sudoers (Exit code non-zero)

  # 2. Whitelisted command test (MUST SUCCEED):
  sudo -n systemctl status ssh
  # Expected Output: Active: active (running) (Exit code 0)

  # 3. Prohibited dangerous command test (MUST FAIL):
  sudo -n chattr
  # Expected Output: sudo: a password is required OR command not allowed
  ```
- 🛑 **Emergency Rollback (If anything fails in Step 6):**
  In your primary terminal (or Serial Console):
  ```bash
  sudo mv /etc/sudoers.d/90-cloud-init-users.disabled /etc/sudoers.d/90-cloud-init-users
  ```

---

## PHASE 2: FILESYSTEM & DIRECTORY LOCKING

### [ ] STEP 7: Execute Directory & File Immutability Script
- **Where:** Primary SSH terminal.
- **Action:** Run the prepared script `03-immutable-files.sh`:
  ```bash
  bash /home/azureuser/AGY-MASTER/DRAFTS/03-immutable-files.sh
  ```
- **What this script does in strict sequence:**
  1. Pre-creates runtime subdirectories (`TASKS/`, `INCIDENTS/`, `ACTIONS/`, `REPORTS/`, `DRAFTS/`) with `azureuser:azureuser` ownership.
  2. Applies `sudo chattr +i` to canonical configuration files (`AGENTS.md`, `PROJECT_REGISTRY.md`, etc.).
  3. Applies `sudo chattr +i` to the parent directory `/home/azureuser/AGY-MASTER` (LAST).
  4. Runs a sanity test creating a temporary file in `TASKS/queue/` to confirm subdirectories remain writable.
- **Expected Output:**
  ```text
  === [DRAFT EXECUTION] STEP 1: ENSURING RUNTIME SUBDIRECTORIES EXIST ===
  [+] Verified: /home/azureuser/AGY-MASTER/TASKS/queue
  ...
  === STEP 2: APPLYING IMMUTABILITY TO CRITICAL TOP-LEVEL FILES ===
  [+] Setting immutable flag (+i) on: /home/azureuser/AGY-MASTER/AGENTS.md
  ...
  === STEP 3 (LAST): LOCKING AGY-MASTER DIRECTORY ITSELF ===
  [+] Setting directory-level immutable flag on: /home/azureuser/AGY-MASTER
  ...
  [+] PASS: Can still write inside TASKS/queue/ (expected — only the parent is locked)
  === COMPLETED DRAFT VERIFICATION ===
  ```
- 🛑 **Emergency Rollback (If directory needs to be unlocked):**
  Via Serial Console (as root):
  ```bash
  chattr -i /home/azureuser/AGY-MASTER
  ```

---

## PHASE 3: FINAL INDEPENDENT VERIFICATION

### [ ] STEP 8: Run Post-Hardening Verification Test Suite
- **Where:** Second SSH terminal (as regular `azureuser`).
- **Action:**
  ```bash
  bash /home/azureuser/AGY-MASTER/DRAFTS/05-verification-tests.sh
  ```
- **Required Acceptance Criteria (All 7 Tests):**
  - `[TEST 1]` sudo chattr -i denial -> **PASS (non-zero exit)**
  - `[TEST 2]` sudo -n whoami broad escalation -> **PASS (broad root blocked)**
  - `[TEST 3]` NOEXEC pager / subshell probe -> **PASS (no subshell spawned)**
  - `[TEST 4]` Direct SYS_unlink syscall on +i file -> **PASS (errno 1 EPERM returned by kernel)**
  - `[TEST 5A]` mv AGY-MASTER rename attempt -> **PASS (rename blocked)**
  - `[TEST 5B]` lsattr -d confirms immutable flag -> **PASS (i flag confirmed)**
  - `[TEST 6]` Subdirectory writeability sanity check -> **PASS (TASKS/queue/ writable)**
  - `[TEST 7]` Azure IMDS Managed Identity token endpoint -> **PASS (HTTP 400 Identity not found)**

- **Target Output:**
  ```text
  VERIFICATION SUMMARY: 7 / 7 TESTS PASSED, 0 FAILED
  ```

---

## COMPLETE POST-HARDENING STATE CHECKLIST

When all 8 steps are completed:
- [x] Sudoers whitelist active with `NOEXEC` (GTFOBins mitigated).
- [x] Wildcard `NOPASSWD: ALL` permanently deactivated.
- [x] `chattr` inaccessible to `azureuser` via sudo.
- [x] Critical files (`AGENTS.md`, `PROJECT_REGISTRY.md`) protected by ext4 inode `+i`.
- [x] Parent directory `AGY-MASTER` protected by inode `+i` (cannot be renamed or unlinked).
- [x] Direct syscalls (`SYS_unlink`) return `EPERM` from ext4 kernel filesystem driver.
- [x] Runtime state directories (`TASKS/`, `REPORTS/`) fully operational for normal agent workflows.
- [x] Zero Azure credentials on VM (Cloud-plane CanNotDelete lock untouched).
- [x] External Snapshot preserved in Azure Portal for rollback.
