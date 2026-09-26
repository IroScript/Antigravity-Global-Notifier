# PARENT DIRECTORY LOCK SPECIFICATION & ARCHITECTURAL COMPARISON

Target Directory: `/home/azureuser/AGY-MASTER`
Target Host: Azure VM `FatehAli`
Status: DRAFT / ARCHITECTURAL ANALYSIS (NO ACTIONS EXECUTED)

CHANGE LOG (fixed from previous draft):
- CORRECTED a claim in the original Option B analysis: setting `+i` on
  `AGY-MASTER` itself does NOT selectively allow writes only to files, while
  blocking directory rename. In ext4, `+i` on a directory blocks ALL new
  directory-entry operations inside it — creating, deleting, or renaming
  any file or subdirectory directly under it. Existing subdirectories that
  do NOT themselves have `+i` remain writable **inside themselves** (you can
  still edit a file's contents inside `TASKS/active/`), but you cannot add or
  remove entries in `AGY-MASTER/` itself once you've locked it.
- This means: every subdirectory AGY needs to write NEW files into (queue
  folders, logs, reports) MUST be created BEFORE `chattr +i` is applied to
  the parent, and none of those specific subdirectories should themselves
  get `+i` (only the parent + selected top-level files should).
- Execution order across drafts 02 and 03 has been made explicit — see
  Section 4.

---

## 1. THE PROBLEM: EXT4 DIRECTORY RENAMING VULNERABILITY

In Linux (POSIX / ext4), the permission to rename or delete a directory
depends on the write permission of its **PARENT directory**, not the
directory itself.

- Current Parent Directory: `/home/azureuser` (Owned by `azureuser:azureuser`,
  permission `drwxr-xr-x`)
- Because `azureuser` has write permission in `/home/azureuser`, any process
  running as `azureuser` can execute:
  ```bash
  mv /home/azureuser/AGY-MASTER /home/azureuser/AGY-MASTER-DELETED
  ```
  even if the files inside have individual `+i` protections.

---

## 2. COMPARATIVE ANALYSIS: OPTION A vs. OPTION B

| Dimension | Option A: Ownership `root:root` + Mode `755` | Option B: Directory-level `chattr +i` |
| :--- | :--- | :--- |
| **Mechanism** | Standard POSIX DAC (Discretionary Access Control) | Linux ext4 Inode Immutable Flag (`FS_IMMUTABLE_FL`) |
| **Can azureuser rename `AGY-MASTER`?** | **NO** — once `azureuser` loses write on the *parent* (`/home/azureuser` would need root ownership too, which is impractical) — see caveat below. | **NO (blocked by ext4 driver itself)**. An immutable directory cannot be renamed, moved, or have entries added/removed, regardless of parent permissions. |
| **Caveat** | Actually requires changing permissions on `/home/azureuser` too (the true parent), which affects azureuser's own home directory usability broadly. Changing only `AGY-MASTER`'s own ownership to root:root does **not** stop rename — rename permission is governed by the *containing* directory (`/home/azureuser`), not the directory being renamed. | No caveat — this correctly targets the actual vulnerable object. |
| **Can azureuser create NEW files/subdirs directly in `AGY-MASTER/`?** | No (root-owned, mode 755, no write bit for azureuser). | No (kernel immutability blocks any new directory entry). |
| **Can azureuser write inside EXISTING subdirectories (e.g. `TASKS/active/`)?** | Yes, if those subdirectories are still owned by azureuser. | Yes, if those subdirectories do not themselves have `+i`. |
| **Resilience against sudo escalation** | If azureuser regains any sudo/root path, `chown` reverses this instantly. | If `chattr` is excluded from sudoers (draft 01), azureuser **cannot** remove `+i` even with a compromised process, because removing it requires `CAP_LINUX_IMMUTABLE` which only root has and sudo won't grant. |

### Correction to the original draft's Option A row:
The original comparison implied Option A only requires changing `AGY-MASTER`'s
own ownership. That is incorrect — rename/delete permission comes from the
**parent** directory (`/home/azureuser`), so Option A would actually require
locking down `/home/azureuser` itself, which is invasive and affects
azureuser's whole home directory. **This is why Option B is the practical
recommendation** — it acts directly on `AGY-MASTER`, not its parent.

---

## 3. ARCHITECTURAL RECOMMENDATION: OPTION B (Directory `+i`, Pre-Created Subdirectories)

### Why Option B is superior:
1. `chattr +i` on `/home/azureuser/AGY-MASTER` completely solves the rename
   vulnerability: the ext4 kernel driver refuses to rename, move, or delete
   `AGY-MASTER`, and refuses to add/remove entries in it directly — regardless
   of `/home/azureuser`'s own permissions.
2. It requires no change to `/home/azureuser` itself, so azureuser's broader
   home-directory usability is untouched.
3. Combined with draft 01 (chattr removed from sudoers), azureuser has no path
   to reverse this — not via sudo, not via direct syscall (`ioctl` with
   `FS_IOC_SETFLAGS` requires `CAP_LINUX_IMMUTABLE`).

### The operational requirement this creates:
Because locking `AGY-MASTER` blocks new entries directly inside it, **every
subdirectory AGY will ever need to write new files into must already exist
before you apply `+i`**. This is why draft 03's script has been reordered —
see Section 4.

---

## 4. DRAFT COMMAND SPECIFICATION (FOR HUMAN REVIEW — DO NOT EXECUTE AUTONOMOUSLY)

### Correct execution order (this matters — reversing steps 1 and 3 below
### will lock AGY out of its own working directories):

```bash
# STEP 1 — Create ALL runtime state subdirectories AGY will ever write
# new files into, BEFORE locking the parent. Add any other subdirectory
# AGY's code creates at runtime to this list now — anything missed here
# will be impossible to create later without temporarily un-immutabilizing
# the parent (which requires sudo access to chattr, which draft 01 removes).
mkdir -p /home/azureuser/AGY-MASTER/TASKS/{queue,active,completed}
mkdir -p /home/azureuser/AGY-MASTER/INCIDENTS/{active,resolved}
mkdir -p /home/azureuser/AGY-MASTER/ACTIONS/{pending,approved,history}
mkdir -p /home/azureuser/AGY-MASTER/REPORTS/daily
mkdir -p /home/azureuser/AGY-MASTER/DRAFTS
chown -R azureuser:azureuser \
    /home/azureuser/AGY-MASTER/TASKS \
    /home/azureuser/AGY-MASTER/INCIDENTS \
    /home/azureuser/AGY-MASTER/ACTIONS \
    /home/azureuser/AGY-MASTER/REPORTS \
    /home/azureuser/AGY-MASTER/DRAFTS

# STEP 2 — Lock top-level canonical architecture files individually
sudo chattr +i /home/azureuser/AGY-MASTER/AGENTS.md
sudo chattr +i /home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md
sudo chattr +i /home/azureuser/AGY-MASTER/POLICIES/safety_levels.json
sudo chattr +i /home/azureuser/AGY-MASTER/POLICIES/protected_registry.json

# STEP 3 — LAST: lock the AGY-MASTER directory itself.
# Run this only after Steps 1 and 2 are fully verified complete — once this
# runs, no new file or subdirectory can be added directly under AGY-MASTER
# (existing subdirectories from Step 1 remain writable inside themselves).
sudo chattr +i /home/azureuser/AGY-MASTER
```

### Rollback Procedure (If Maintenance Required):
This MUST be run by a human with direct console/SSH access — it is not
available to azureuser via sudo once draft 01 is applied, by design. It
requires either temporarily re-adding a scoped `chattr` sudo rule, or logging
in as root directly via Azure Serial Console.
```bash
sudo chattr -i /home/azureuser/AGY-MASTER
sudo chattr -i /home/azureuser/AGY-MASTER/AGENTS.md
sudo chattr -i /home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md
sudo chattr -i /home/azureuser/AGY-MASTER/POLICIES/safety_levels.json
sudo chattr -i /home/azureuser/AGY-MASTER/POLICIES/protected_registry.json
```
