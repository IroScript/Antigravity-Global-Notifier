# EXTERNAL IMMUTABLE BACKUP ARCHITECTURE (WORM & REMOTE GIT)

Target Host: Azure VM `FatehAli`
Status: DRAFT SPECIFICATION (NO ACTIONS EXECUTED)

CHANGE LOG (fixed from previous draft):
- FLAGGED: the git backup script's `git push origin main` line was commented
  out in the original draft. As written, that script only commits locally —
  if the VM disk is destroyed, that local git history is destroyed with it,
  which defeats the entire purpose of an "external" backup. Section 3 below
  now requires setting up a deploy key BEFORE uncommenting the push line, and
  the script has a safety check that warns (rather than silently no-oping) if
  no push remote is reachable.

---

## 1. WHY EXTERNAL IMMUTABLE BACKUP IS MANDATORY

Even with strict sudoers and `chattr +i`, an attacker with physical/hypervisor
access, a kernel exploit, or a disk failure could still destroy local data.
The only defense that survives total VM compromise is **storage outside the
VM**:
- The VM has **zero Azure credentials** and **no Managed Identity**.
- Data stored in an Azure Blob Storage container with **Immutable Blob
  Storage (WORM — Write Once, Read Many)** cannot be deleted or overwritten
  by any process inside the VM, because the VM has no credential path to
  Azure Resource Manager at all.

---

## 2. AZURE BLOB WORM POLICY SETUP (EXECUTE FROM AZURE CLOUD SHELL)

> 🛑 **CRITICAL OPERATIONAL REQUIREMENT:**
> These Azure CLI commands **CANNOT** and **MUST NOT** be executed from
> inside the `FatehAli` VM (it has no Azure credentials to do so anyway).
> Run them from **Azure Cloud Shell** (https://shell.azure.com) or an
> external admin workstation logged in as yourself.

### Step 1: Create a Dedicated Backup Storage Account
```bash
RESOURCE_GROUP="fatehali-rg"
LOCATION="eastus"   # match your VM's region
STORAGE_ACCOUNT="fatehalibackupstorage$RANDOM"
CONTAINER_NAME="immutable-vm-backups"

az storage account create \
    --name "$STORAGE_ACCOUNT" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --allow-blob-public-access false

az storage container create \
    --name "$CONTAINER_NAME" \
    --account-name "$STORAGE_ACCOUNT" \
    --auth-mode login
```

### Step 2: Configure Time-Based WORM Immutability Policy
```bash
# Unlocked mode first lets you test / adjust the retention period.
az storage container immutability-policy create \
    --account-name "$STORAGE_ACCOUNT" \
    --container-name "$CONTAINER_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --period 30 \
    --allow-protected-append-writes true

# Locking is IRREVERSIBLE until the retention period expires — even by the
# Azure subscription owner. Only run this once you are certain the policy
# (retention period, container) is correct:
# az storage container immutability-policy lock \
#     --account-name "$STORAGE_ACCOUNT" \
#     --container-name "$CONTAINER_NAME" \
#     --resource-group "$RESOURCE_GROUP"
```

### Step 3: How data actually gets INTO this container
The commands above only create the container — they do not move any data.
From the VM (which has no Azure credentials), you cannot use `az storage
blob upload` with `--auth-mode login`. Two practical options:
- **SAS token method**: generate a time-limited, upload-only SAS token from
  Cloud Shell (`az storage container generate-sas --permissions aw ...`) and
  give only that token string to the VM's backup script/cron job. A leaked
  upload-only SAS cannot be used to delete existing immutable blobs anyway.
- **Azure Storage-explorer / azcopy from an external machine**: pull backups
  down to an admin workstation first, then push from there — keeps the VM
  fully credential-less.

---

## 3. AUTOMATED REMOTE GIT PUSH (DISASTER RECOVERY)

For code repositories like `Frappe-erp-Alco`, `alco_app`, and `AGY-MASTER`,
pushing commits to an external private Git remote (GitHub/GitLab) means local
deletion is recoverable via `git clone` even if the VM is gone entirely.

### Prerequisite (do this BEFORE relying on the script below):
1. Create a private repository on GitHub/GitLab for each of `Frappe-erp-Alco`
   and `AGY-MASTER` (if they don't already have a remote).
2. Generate a dedicated **deploy key** (SSH key with push access scoped to
   just that repo, not your personal account key):
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/agy_deploy_key -N "" -C "agy-backup-deploy-key"
   ```
   Add the **public** key as a deploy key with write access on the remote
   repo's settings page. Keep the private key readable only by azureuser
   (`chmod 600`).
3. Configure the repo to use that key specifically (via `core.sshCommand` or
   an SSH config `Host` alias), and confirm with a manual test push before
   trusting the cron job.

### Draft Backup Script: `/home/azureuser/AGY-MASTER/DRAFTS/git-sync-backup.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_REPOS=(
    "/home/azureuser/Frappe-erp-Alco"
    "/home/azureuser/AGY-MASTER"
)

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FAILURES=0

for repo in "${BACKUP_REPOS[@]}"; do
    if [[ -d "$repo/.git" ]]; then
        echo "[+] Syncing repository: $repo at $TIMESTAMP"
        cd "$repo"

        # Confirm a push remote is actually configured before relying on this
        if ! git remote get-url origin >/dev/null 2>&1; then
            echo "[!] WARNING: $repo has no 'origin' remote configured — commits will stay LOCAL ONLY. This defeats the purpose of external backup."
            FAILURES=$((FAILURES + 1))
            continue
        fi

        git add -A
        if ! git diff-index --quiet HEAD --; then
            git commit -m "Automated DR Snapshot: $TIMESTAMP"
        fi

        # Push is now active (not commented out) — but only reaches here if
        # the prerequisite deploy-key setup above has been completed and
        # tested manually at least once.
        if ! git push origin main; then
            echo "[!] WARNING: push failed for $repo — check deploy key / network"
            FAILURES=$((FAILURES + 1))
        fi
    else
        echo "[-] Not a git repo, skipping: $repo"
    fi
done

if [[ $FAILURES -gt 0 ]]; then
    echo "[!] $FAILURES repo(s) did not reach the remote this run — investigate before trusting this backup."
    exit 1
fi
```

### Crontab Integration (Draft):
```cron
# Run every night at 02:00 AM UTC
0 2 * * * /bin/bash /home/azureuser/AGY-MASTER/DRAFTS/git-sync-backup.sh >> /home/azureuser/AGY-MASTER/REPORTS/daily/git-backup.log 2>&1
```

**Do not enable this cron job until you have manually run the script once,
confirmed it pushes successfully, and confirmed the commit is visible on
GitHub/GitLab from a separate machine.**
