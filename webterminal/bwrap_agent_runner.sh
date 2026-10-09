#!/bin/bash
set -euo pipefail

# ==============================================================================
# AGY Agent Bubblewrap (bwrap) OS-Level Container Isolation Runner
# Version: 1.0.0
# Security Mode: STRICT FAIL-CLOSED
# Layers Enforced:
#   1. Mount Namespace: Root filesystem read-only, private tmpfs on /tmp & /dev/shm
#   2. PID Namespace: Host processes and sibling agents invisible
#   3. IPC Namespace: Shared memory and POSIX queues strictly isolated
#   4. User Namespace: Unprivileged sandboxing without setuid root
#   5. Project Workspace Bound: Only target project is writable; peer paths masked
#   6. Credential & Brain Masking: ~/.ssh, brain/ transcripts, summaries db masked
# ==============================================================================

PROJECT_KEY="${1:-}"
shift || true

if [ -z "$PROJECT_KEY" ]; then
    echo "[BWRAP_RUNNER ERROR]: Missing project key argument. Usage: $0 <project_key> [command...]" >&2
    exit 101
fi

BWRAP_BIN="/usr/bin/bwrap"
if [ ! -x "$BWRAP_BIN" ]; then
    echo "[BWRAP_RUNNER ERROR]: Bubblewrap binary '$BWRAP_BIN' is not executable or missing" >&2
    exit 102
fi

declare -A PROJECT_PATHS=(
    ["yt"]="/home/azureuser/IroScript_Projects/Social Media/youtube"
    ["frappe"]="/home/azureuser/IroScript_Projects/Frappe-erp-Alco"
    ["tg"]="/home/azureuser/IroScript_Projects/Social Media/telegram-bot"
    ["history"]="/home/azureuser/IroScript_Projects/Personal Life/PERSONAL AI AGENT"
    ["kids"]="/home/azureuser/IroScript_Projects/Personal Life/kids_tube_with_folder_seection"
    ["rust"]="/home/azureuser/IroScript_Projects/Personal Life/Rust_Task_With_Time_Keeping_And_Live_Note"
    ["article"]="/home/azureuser/IroScript_Projects/Article_Publishing_Management/Article-Publishing-Platform"
    ["game"]="/home/azureuser/IroScript_Projects/Article_Publishing_Management/3D-Game-Design-Studio"
    ["research"]="/home/azureuser/IroScript_Projects/Whatsapp master/webterminal/Agy Whatsapp Agents/Ask-And-Research"
    ["report"]="/home/azureuser/IroScript_Projects/Whatsapp master/webterminal/Agy Whatsapp Agents/Reporting-Agent"
    ["codex"]="/home/azureuser/IroScript_Projects/OpenAI_Codex"
)

TARGET_DIR="${PROJECT_PATHS[$PROJECT_KEY]:-}"
if [ -z "$TARGET_DIR" ] || [ ! -d "$TARGET_DIR" ]; then
    echo "[BWRAP_RUNNER ERROR]: Target project directory for '$PROJECT_KEY' is invalid or does not exist: '$TARGET_DIR'" >&2
    exit 103
fi

BWRAP_ARGS=(
    --unshare-user
    --unshare-ipc
    --unshare-pid
    --unshare-uts
    --ro-bind / /
    --tmpfs /tmp
    --tmpfs /dev/shm
    --proc /proc
    --dev /dev
    --tmpfs /home/azureuser/IroScript_Projects
)

# Recursively create parent dirs inside the tmpfs mount point
REL_PATH="${TARGET_DIR#/home/azureuser/IroScript_Projects/}"
IFS='/' read -ra PARTS <<< "$REL_PATH"
ACC="/home/azureuser/IroScript_Projects"
for ((i=0; i<${#PARTS[@]}-1; i++)); do
    ACC="$ACC/${PARTS[i]}"
    BWRAP_ARGS+=(--dir "$ACC")
done

BWRAP_ARGS+=(
    --bind "$TARGET_DIR" "$TARGET_DIR"
    --tmpfs /home/azureuser/.ssh
    --tmpfs /home/azureuser/.gemini/antigravity-cli/brain
    --ro-bind /dev/null /home/azureuser/.gemini/antigravity-cli/conversation_summaries.db
    --chdir "$TARGET_DIR"
    --setenv WORKSPACE "$TARGET_DIR"
    --setenv AGENT_PROJECT_KEY "$PROJECT_KEY"
)

if [ $# -eq 0 ]; then
    CMD=("/bin/bash")
else
    CMD=("$@")
fi

exec "$BWRAP_BIN" "${BWRAP_ARGS[@]}" "${CMD[@]}"
