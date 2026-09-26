#!/usr/bin/env bash
# ==============================================================================
# /home/azureuser/AGY-MASTER/DRAFTS/03-immutable-files.sh (DRAFT ONLY)
# ==============================================================================
# Purpose: Applies Linux Inode Immutability (chattr +i) to critical
#          configuration files, and LAST, to the AGY-MASTER directory itself.
#
# CHANGE LOG (fixed from previous draft):
# - FIXED ORDERING BUG: the previous version applied chattr +i to the
#   AGY-MASTER directory without first guaranteeing all runtime subdirectories
#   (TASKS, INCIDENTS, ACTIONS, REPORTS, DRAFTS) already existed. Locking the
#   parent BEFORE those subdirectories exist would make it impossible to
#   create them afterward without a chattr-capable sudo session, which draft
#   01 deliberately removes. This script now creates and verifies all
#   subdirectories FIRST, and locks AGY-MASTER itself LAST.
# - Added existence + ownership verification before locking.
#
# ARCHITECTURAL SECURITY COUPLING (WHY THIS WORKS):
# ------------------------------------------------------------------------------
# In the original audit, 'chattr +i' was classified as "bypassable" because:
#   AGY -> child process -> sudo -> root -> chattr -i <file>
#
# Once draft 01 (01-sudoers-restricted.draft) is active:
# 1. 'chattr' is STRICTLY EXCLUDED from sudoers (deny-by-default).
# 2. 'azureuser' has CapEff = 0 (zero effective Linux capabilities).
# 3. Removing '+i' requires the kernel capability CAP_LINUX_IMMUTABLE, which
#    is only available to a real root context — not grantable via this
#    restricted sudoers file.
# 4. Without sudo access to chattr and without CAP_LINUX_IMMUTABLE, azureuser
#    (even a compromised AGY process running as azureuser) cannot remove '+i'
#    under any circumstance — not via C, Python, or direct syscalls.
# 5. Direct syscalls (unlink, rename, truncate, or the ioctl FS_IOC_SETFLAGS
#    used by chattr itself) will return errno EPERM (Operation not permitted)
#    directly from the ext4 filesystem layer, before reaching any userland code.
# ==============================================================================

set -euo pipefail

echo "=== [DRAFT EXECUTION] STEP 1: ENSURING RUNTIME SUBDIRECTORIES EXIST ==="
echo "(Must happen BEFORE locking the parent, or these can never be created later)"

REQUIRED_SUBDIRS=(
    "/home/azureuser/AGY-MASTER/TASKS/queue"
    "/home/azureuser/AGY-MASTER/TASKS/active"
    "/home/azureuser/AGY-MASTER/TASKS/completed"
    "/home/azureuser/AGY-MASTER/INCIDENTS/active"
    "/home/azureuser/AGY-MASTER/INCIDENTS/resolved"
    "/home/azureuser/AGY-MASTER/ACTIONS/pending"
    "/home/azureuser/AGY-MASTER/ACTIONS/approved"
    "/home/azureuser/AGY-MASTER/ACTIONS/history"
    "/home/azureuser/AGY-MASTER/REPORTS/daily"
    "/home/azureuser/AGY-MASTER/DRAFTS"
)

for dir in "${REQUIRED_SUBDIRS[@]}"; do
    mkdir -p "$dir"
    chown azureuser:azureuser "$dir"
    echo "[+] Verified: $dir"
done

echo "=== STEP 2: APPLYING IMMUTABILITY TO CRITICAL TOP-LEVEL FILES ==="

PROTECTED_FILES=(
    "/home/azureuser/AGY-MASTER/AGENTS.md"
    "/home/azureuser/AGY-MASTER/PROJECT_REGISTRY.md"
    "/home/azureuser/AGY-MASTER/POLICIES/safety_levels.json"
    "/home/azureuser/AGY-MASTER/POLICIES/protected_registry.json"
    "/home/azureuser/.gemini/config/hooks.json"
    "/home/azureuser/.bashrc"
    "/home/azureuser/.profile"
)

for file in "${PROTECTED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "[+] Setting immutable flag (+i) on: $file"
        sudo chattr +i "$file"
    else
        echo "[-] File not found, skipping: $file"
    fi
done

echo "=== STEP 3 (LAST): LOCKING AGY-MASTER DIRECTORY ITSELF ==="
echo "(All subdirectories above must already exist — verified in Step 1)"

if [[ -d "/home/azureuser/AGY-MASTER" ]]; then
    echo "[+] Setting directory-level immutable flag on: /home/azureuser/AGY-MASTER"
    sudo chattr +i "/home/azureuser/AGY-MASTER"
else
    echo "[!] ERROR: /home/azureuser/AGY-MASTER does not exist. Aborting."
    exit 1
fi

echo "=== IMMUTABILITY STATUS INSPECTION ==="
for file in "${PROTECTED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        lsattr "$file"
    fi
done
lsattr -d "/home/azureuser/AGY-MASTER"

echo "=== SANITY CHECK: CONFIRM SUBDIRECTORIES ARE STILL WRITABLE INSIDE THEMSELVES ==="
TEST_FILE="/home/azureuser/AGY-MASTER/TASKS/queue/.write-test-$$"
if touch "$TEST_FILE" 2>/dev/null; then
    echo "[+] PASS: Can still write inside TASKS/queue/ (expected — only the parent is locked)"
    rm -f "$TEST_FILE"
else
    echo "[!] WARNING: Cannot write inside TASKS/queue/ — check ownership/permissions"
fi

echo "=== COMPLETED DRAFT VERIFICATION ==="
