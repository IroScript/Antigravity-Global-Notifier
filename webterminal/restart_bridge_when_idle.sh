#!/bin/bash
# Restart WhatsApp bridge (tmux agy:1) only when agy:0 and agy:frappe are idle.
# Idle = bottom status line has no "esc to cancel" for 3 checks in a row (15s apart).
LOG=/home/azureuser/.webterminal/bridge_restart_watch.log
WT=/home/azureuser/.webterminal
busy() {
  for w in agy:0 agy:frappe; do
    tmux has-session -t "$w" 2>/dev/null || continue
    tmux capture-pane -p -t "$w" | tail -3 | grep -q "esc to cancel" && return 0
  done
  return 1
}
echo "$(date -u +%FT%TZ) watcher started" >> "$LOG"
idle=0
for i in $(seq 1 1440); do   # up to 6 hours
  if busy; then idle=0; else idle=$((idle+1)); fi
  if [ "$idle" -ge 3 ]; then
    echo "$(date -u +%FT%TZ) agents idle -> restarting bridge" >> "$LOG"
    tmux send-keys -t agy:1 C-c
    sleep 3
    tmux send-keys -t agy:1 "cd '$WT' && node whatsapp_bridge.js" Enter
    sleep 20
    if pgrep -f "node whatsapp_bridge.js" >/dev/null; then
      echo "$(date -u +%FT%TZ) bridge running again (pid $(pgrep -f 'node whatsapp_bridge.js' | head -1))" >> "$LOG"
    else
      echo "$(date -u +%FT%TZ) WARNING bridge NOT running after restart" >> "$LOG"
    fi
    exit 0
  fi
  sleep 15
done
echo "$(date -u +%FT%TZ) gave up (agents busy 6h), bridge not restarted" >> "$LOG"
