#!/usr/bin/env bash
# ==============================================================================
# Antigravity-CLI-Trustworthy-Protocol: One-Click Installer & Activator
# Sets up global governance, runtime rules, lifecycle hooks, and interceptors
# for a fresh Google Antigravity CLI installation on any Linux machine.
# ==============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_HOME="${HOME:-/home/azureuser}"

echo "======================================================================"
echo " Antigravity CLI Trustworthy Protocol: Automated Setup"
echo " Repo Source: ${REPO_DIR}"
echo " Target Home: ${TARGET_HOME}"
echo "======================================================================"

# 1. Ensure target directory hierarchy exists
mkdir -p "${TARGET_HOME}/.gemini/config"
mkdir -p "${TARGET_HOME}/.gemini/antigravity-cli"
mkdir -p "${TARGET_HOME}/.agents/rules"
mkdir -p "${TARGET_HOME}/.agents/hooks"
mkdir -p "${TARGET_HOME}/.local/bin"
mkdir -p "${TARGET_HOME}/AGY-MASTER/INCIDENTS/active"

# 2. Link Global Governance & Rules
ln -sf "${REPO_DIR}/governance/AGENTS.md" "${TARGET_HOME}/.gemini/AGENTS.md"
ln -sf "${REPO_DIR}/governance/AGENTS.md" "${TARGET_HOME}/.gemini/config/AGENTS.md"
ln -sf "${REPO_DIR}/governance/GEMINI.md" "${TARGET_HOME}/.gemini/GEMINI.md"
ln -sf "${REPO_DIR}/governance/GEMINI.md" "${TARGET_HOME}/.gemini/config/GEMINI.md"
ln -sf "${REPO_DIR}/governance/AGENTS.md" "${TARGET_HOME}/AGENTS.md"
ln -sf "${REPO_DIR}/governance/GEMINI.md" "${TARGET_HOME}/GEMINI.md"

for rule_file in "${REPO_DIR}/rules/"*.md; do
    if [ -f "${rule_file}" ]; then
        bname="$(basename "${rule_file}")"
        ln -sf "${rule_file}" "${TARGET_HOME}/.agents/rules/${bname}"
    fi
done

# 3. Link Lifecycle Hooks & Verifiers
ln -sf "${REPO_DIR}/hooks/hooks.json" "${TARGET_HOME}/.gemini/config/hooks.json"
ln -sf "${REPO_DIR}/hooks/hooks.json" "${TARGET_HOME}/.agents/hooks.json"
ln -sf "${REPO_DIR}/hooks/delete_guard.py" "${TARGET_HOME}/.agents/hooks/delete_guard.py"
ln -sf "${REPO_DIR}/hooks/completion_gate_stop_hook.py" "${TARGET_HOME}/.agents/hooks/completion_gate_stop_hook.py"
ln -sf "${REPO_DIR}/scripts/verify_10_fold.py" "${TARGET_HOME}/.agents/verify_10_fold.py"
ln -sf "${REPO_DIR}/scripts/safe_archive.py" "${TARGET_HOME}/.agents/safe_archive.py"

# 4. Link OS Binary Interceptors
ln -sf "${REPO_DIR}/interceptors/scoped_rm.py" "${TARGET_HOME}/.local/bin/rm"
ln -sf "${REPO_DIR}/interceptors/unzip" "${TARGET_HOME}/.local/bin/unzip"

# Ensure executable permissions on scripts and interceptors
chmod 755 "${REPO_DIR}/scripts/verify_10_fold.py"
chmod 755 "${REPO_DIR}/scripts/safe_archive.py"
chmod 755 "${REPO_DIR}/hooks/delete_guard.py"
chmod 755 "${REPO_DIR}/hooks/completion_gate_stop_hook.py"
chmod 755 "${REPO_DIR}/interceptors/scoped_rm.py"
chmod 755 "${REPO_DIR}/interceptors/unzip"

# 5. Initialize settings.json if missing
SETTINGS_FILE="${TARGET_HOME}/.gemini/antigravity-cli/settings.json"
if [ ! -f "${SETTINGS_FILE}" ]; then
    cat <<EOF > "${SETTINGS_FILE}"
{
  "trustedWorkspaces": [
    "${TARGET_HOME}"
  ],
  "context": {
    "fileName": "AGENTS.md"
  },
  "hooks": {
    "BeforeTool": [
      {
        "matcher": ".*",
        "command": "/usr/bin/python3 ${TARGET_HOME}/.agents/hooks/delete_guard.py"
      }
    ]
  }
}
EOF
    chmod 600 "${SETTINGS_FILE}"
    echo "[+] Initialized default settings.json"
fi
ln -sf "${SETTINGS_FILE}" "${TARGET_HOME}/.agents/settings.json"

# 6. Initialize verification HMAC secret key if missing
KEY_FILE="${TARGET_HOME}/.agents/.verification_secret.key"
if [ ! -f "${KEY_FILE}" ]; then
    python3 -c "import secrets; print(secrets.token_hex(32))" > "${KEY_FILE}"
    chmod 600 "${KEY_FILE}"
    echo "[+] Generated fresh HMAC verification secret key"
fi

# 7. Self-Test & Verification Run
echo "[*] Running initial 10-fold verification test..."
python3 "${REPO_DIR}/scripts/verify_10_fold.py" \
    --task-name "fresh_installation_bootstrap" \
    --workspace "${TARGET_HOME}" \
    --files "${REPO_DIR}/governance/AGENTS.md" \
            "${REPO_DIR}/rules/06-additive-governance.md" \
            "${REPO_DIR}/hooks/hooks.json" \
    --test-cmd "python3 -c 'import os; assert os.path.exists(\"${TARGET_HOME}/.gemini/AGENTS.md\"); print(\"Bootstrap Verified\")'" \
    --negative-cmd "rm -f ${REPO_DIR}/governance/AGENTS.md"

echo "======================================================================"
echo " Antigravity Trustworthy Protocol: Setup Completed Successfully!"
echo " All 6 Rules, 56 Directives, Hooks, and Interceptors are ACTIVE."
echo "======================================================================"
