#!/bin/bash
# Start the MAIN WhatsApp agent (tmux agy:0).
# No --model flag on purpose: AGY uses the last /model selection
# (stored in ~/.gemini/antigravity-cli/settings.json) as the default.
cd /home/azureuser || exit 1
exec /home/azureuser/.local/bin/agy --mode plan --dangerously-skip-permissions "$@"
