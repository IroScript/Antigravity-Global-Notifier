#!/usr/bin/env bash
# ensure_no_plan_mode.sh — Continuously ensure no AGY agent stays in 'plan' mode.
# When an agent is idle ('? for shortcuts') and in 'plan' mode, sends BTab (Shift+Tab) to switch to normal execution mode.

while true; do
  for win in 0 yt frappe tg history kids rust article game research; do
    pane=$(tmux capture-pane -p -t "agy:$win" 2>/dev/null | tail -n 6)
    if echo "$pane" | grep -qE "\? for shortcuts|\? for" && echo "$pane" | grep -q "plan ·"; then
      echo "[$(date -u +%FT%TZ)] Window agy:$win is idle in plan mode. Sending BTab to cycle out..."
      tmux send-keys -t "agy:$win" BTab
      sleep 0.3
    fi
  done
  sleep 2
done
