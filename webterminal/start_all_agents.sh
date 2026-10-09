#!/usr/bin/env bash
# start_all_agents.sh — Initialize and launch all AGY agents and WhatsApp bridge in tmux.
set -e

echo "=== Initializing tmux session 'agy' ==="
tmux has-session -t agy 2>/dev/null || tmux new-session -d -s agy -n AI-Agent

# List of named windows
windows=("AI-Agent" "Bash-Terminal" "Linux-Shell" "yt" "frappe" "tg" "history" "kids" "rust" "article" "game" "research" "report" "codex")
for w in "${windows[@]}"; do
  tmux list-windows -t agy -F "#{window_name}" 2>/dev/null | grep -q "^${w}$" || tmux new-window -t agy -n "${w}"
done

sleep 1

# Window 0: AI-Agent (Master Orchestrator agy:0)
if ! tmux capture-pane -p -t agy:0 2>/dev/null | grep -qE "Antigravity CLI|shortcuts|for shortcuts|esc to cancel|Switch Model"; then
  echo "Starting agy:0 (Master Agent)..."
  tmux send-keys -t agy:0 "cd /home/azureuser && ~/.webterminal/start_agy0.sh" Enter
fi

# Window 1: Bash-Terminal (WhatsApp bridge runs as systemd service agy-whatsapp.service)
tmux send-keys -t agy:1 "cd /home/azureuser" Enter
XDG_RUNTIME_DIR=/run/user/$(id -u) systemctl --user start agy-whatsapp.service 2>/dev/null || true

# Window 2: Linux-Shell
tmux send-keys -t agy:2 "cd /home/azureuser" Enter

# Worker AGY CLI Agents mapping: window -> cwd
declare -A agent_dirs=(
  ["yt"]="/home/azureuser/IroScript_Projects/Social Media/youtube"
  ["frappe"]="/home/azureuser/Frappe-erp-Alco"
  ["tg"]="/home/azureuser/IroScript_Projects/Social Media/telegram-bot"
  ["history"]="/home/azureuser/IroScript_Projects/Personal Life/Digital History management/PERSONAL AI AGENT"
  ["kids"]="/home/azureuser/IroScript_Projects/Personal Life/kids_tube_with_folder_seection"
  ["rust"]="/home/azureuser/IroScript_Projects/Personal Life/Rust_Task_With_Time_Keeping_And_Live_Note"
  ["article"]="/home/azureuser/IroScript_Projects/Article_Publishing_Management/Article-Publishing-Platform"
  ["game"]="/home/azureuser/IroScript_Projects/Article_Publishing_Management/3D-Game-Design-Studio"
  ["research"]="/home/azureuser/IrakIroan/IroScript_Projects/Ask-And-Research-Agent"
)

for win in "${!agent_dirs[@]}"; do
  dir="${agent_dirs[$win]}"
  if [ -d "$dir" ]; then
    if ! tmux capture-pane -p -t "agy:$win" 2>/dev/null | grep -qE "Antigravity CLI|shortcuts|for shortcuts|esc to cancel|Switch Model"; then
      echo "Starting agy:$win in $dir..."
      tmux send-keys -t "agy:$win" "cd '$dir' && ~/.local/bin/agy --dangerously-skip-permissions" Enter
    fi
  fi
done

# Window: report (Reporting Agent)
rep_dir="/home/azureuser/IroScript_Projects/Whatsapp master/webterminal/Agy Whatsapp Agents/Reporting-Agent"
if [ -d "$rep_dir" ]; then
  if ! tmux capture-pane -p -t "agy:report" 2>/dev/null | grep -qE "Check completed|cycle|Sentinel"; then
    echo "Starting agy:report..."
    tmux send-keys -t "agy:report" "cd '$rep_dir' && python3 sentinel_reporter.py" Enter
  fi
fi

# Window: codex (OpenAI Codex CLI Agent)
codex_dir="/home/azureuser/IroScript_Projects/OpenAI_Codex"
if [ -d "$codex_dir" ]; then
  if ! tmux capture-pane -p -t "agy:codex" 2>/dev/null | grep -qE "OpenAI Codex|Ask Codex|YOLO mode|shortcuts"; then
    echo "Starting agy:codex..."
    tmux send-keys -t "agy:codex" "cd '$codex_dir' && codex --dangerously-bypass-approvals-and-sandbox" Enter
  fi
fi

echo "=== All AGY agents and WhatsApp bridge launched successfully ==="
