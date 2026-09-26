#!/bin/bash
tmux has-session -t agy 2>/dev/null || tmux new-session -d -s agy -n AI-Agent
windows=("AI-Agent" "Bash-Terminal" "Linux-Shell" "yt" "frappe" "tg" "history" "kids" "rust" "article" "game" "research")
for w in "${windows[@]}"; do
  tmux list-windows -t agy -F "#{window_name}" 2>/dev/null | grep -q "^$" || tmux new-window -t agy -n ""
done
