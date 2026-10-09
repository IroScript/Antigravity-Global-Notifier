#!/bin/bash
# ==============================================================================
# Independent Out-of-Process Watchdog for AGY WhatsApp Bridge
# Verifies PID alive status and heartbeat timestamp freshness.
# ==============================================================================
set -u

USER_HOME="${HOME:-/home/azureuser}"
HEARTBEAT_FILE="$USER_HOME/.webterminal/wa_heartbeat.json"
WATCHDOG_LOG="$USER_HOME/.webterminal/wa_watchdog.log"
SERVICE_NAME="agy-whatsapp.service"
MAX_STALE_SECONDS=120

export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

log_msg() {
  local msg="$1"
  local now
  now="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "[$now] [WATCHDOG] $msg" >> "$WATCHDOG_LOG"
}

restart_service() {
  local reason="$1"
  log_msg "TRIGGERING RESTART of $SERVICE_NAME. Reason: $reason"
  systemctl --user restart "$SERVICE_NAME"
  local rc=$?
  if [ $rc -eq 0 ]; then
    log_msg "Restart command dispatched successfully (rc=0)."
  else
    log_msg "Restart command failed with exit code $rc."
  fi
}

# 1. Check if the process is running
BRIDGE_PID="$(pgrep -f "node.*whatsapp_bridge\.js" | head -n 1)"
if [ -z "$BRIDGE_PID" ]; then
  restart_service "No running node process matching whatsapp_bridge.js found."
  exit 0
fi

# 2. Check if heartbeat file exists
if [ ! -f "$HEARTBEAT_FILE" ]; then
  restart_service "Heartbeat file $HEARTBEAT_FILE does not exist."
  exit 0
fi

# 3. Check heartbeat freshness
NOW_EPOCH="$(date +%s)"
HB_TIMESTAMP_MS="$(python3 -c "import json; data=json.load(open('$HEARTBEAT_FILE')); print(int(data.get('timestamp', 0)))" 2>/dev/null || echo 0)"
HB_EPOCH=$((HB_TIMESTAMP_MS / 1000))
AGE=$((NOW_EPOCH - HB_EPOCH))

if [ "$AGE" -gt "$MAX_STALE_SECONDS" ]; then
  restart_service "Heartbeat is stale ($AGE seconds old > $MAX_STALE_SECONDS max)."
  exit 0
fi

# Everything healthy
exit 0
