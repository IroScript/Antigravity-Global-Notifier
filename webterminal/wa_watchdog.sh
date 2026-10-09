#!/bin/bash
# ==============================================================================
# Non-Destructive Observational Watchdog for AGY WhatsApp Bridge
# ZERO-RESTART ARCHITECTURE:
# Pure diagnostic and telemetry collection. NEVER restarts, kills, or stops the bridge.
# Distinguishes: Process Alive | Event Loop Responsive | WebSocket Connected | Auth Valid | Delivery Functional
# ==============================================================================
set -euo pipefail

USER_HOME="${HOME:-/home/azureuser}"
DIAG_SCRIPT="$USER_HOME/.webterminal/wa_diagnostics.py"

if [ -f "$DIAG_SCRIPT" ]; then
  exec /usr/bin/python3 "$DIAG_SCRIPT"
else
  echo "[WATCHDOG] Diagnostic script $DIAG_SCRIPT not found." >&2
  exit 0
fi
