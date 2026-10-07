#!/usr/bin/env bash
# set_agy_model.sh — Switch the model/effort of an AGY CLI agent running in tmux.
#
# Drives the interactive `/model` picker inside the tmux window (never bare bash).
# Safe to call for the agent's OWN window: it waits until the agent is idle
# (turn finished, empty input box) before opening the picker.
#
# Usage:
#   set_agy_model.sh <window> <model query> [low|medium|high] [max_wait_seconds]
#   set_agy_model.sh --status <window>
# Examples:
#   set_agy_model.sh agy:0 opus high
#   set_agy_model.sh 0 "sonnet 5.5" medium
#   set_agy_model.sh frappe "3.8 flash" low
#   nohup set_agy_model.sh agy:0 sonnet high 900 >/dev/null 2>&1 &   # from inside agy:0 itself
set -uo pipefail

WEBTERM="/home/azureuser/.webterminal"
LOG="$WEBTERM/model_switch.log"

log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }
die() { echo "ERROR: $*"; log "ERROR: $*"; exit 1; }

norm_window() {
  local w="${1:-agy:0}"
  case "$w" in
    agy:*) echo "$w" ;;
    main|master|agy0|whatsapp) echo "agy:0" ;;
    reporting) echo "agy:report" ;;
    *) echo "agy:$w" ;;
  esac
}

pane() { tmux capture-pane -p -t "$WIN" 2>/dev/null; }

current_model() {
  if [ "$WIN" = "agy:codex" ]; then
    pane | grep -E 'GPT-[0-9]' | tail -1 | sed -E 's/^[[:space:]]*//; s/[[:space:]]+$//' | awk '{print $1" "$2}'
    return
  fi
  # Status bar: "? for shortcuts" (idle) or "esc to cancel" (running)
  pane | grep -E '(for shortcuts|esc to cancel)' | tail -1 | sed -E 's/.*(for shortcuts|esc to cancel)[[:space:]]+//; s/[[:space:]]+$//' \
    | awk -F' · ' '{ if (NF>=2 && ($2=="low"||$2=="medium"||$2=="high")) print $1" · "$2; else print $1 }'
}

is_idle() {
  local p tail_p input
  p="$(pane)"
  tail_p="$(echo "$p" | tail -n 8)"
  if [ "$WIN" = "agy:codex" ]; then
    echo "$tail_p" | grep -q 'Ask Codex to do anything' || return 1
    echo "$tail_p" | grep -qE 'esc to interrupt|◦ Working|Running command' && return 1
    return 0
  fi
  echo "$tail_p" | grep -q 'for shortcuts' || return 1
  echo "$tail_p" | grep -qE 'esc to cancel|Working\.\.\.|Generating\.\.\.|Running command|Loading\.\.\.' && return 1
  echo "$p" | grep -q 'Switch Model' && return 1
  # Input box (last line starting with ">") must be empty
  input="$(echo "$p" | grep -E '^>' | tail -1 | sed -E 's/^>[[:space:]]*//; s/[[:space:]]+$//')"
  [ -z "$input" ]
}

picker_open() { pane | grep -q 'Switch Model'; }

highlighted_item() {
  # The highlighted row inside the picker (after the "Search:" line) starts with "> "
  pane | awk '/Switch Model/{p=1} p && /Search:/{s=1; next} s && /^> /{sub(/^> /,""); sub(/[[:space:]]+\(current\).*$/,""); sub(/[[:space:]]+$/,""); print; exit}'
}

matches_query() {  # every word of the query must appear in the item (case-insensitive)
  local item="${1,,}" q="${2,,}" w
  for w in $q; do [[ "$item" == *"$w"* ]] || return 1; done
  return 0
}

clear_search() { local i; for i in $(seq 1 40); do tmux send-keys -t "$WIN" BSpace; done; sleep 0.4; }

# ---------------------------------------------------------------- args
if [ "${1:-}" = "--status" ]; then
  WIN="$(norm_window "${2:-agy:0}")"
  tmux list-panes -t "$WIN" >/dev/null 2>&1 || die "tmux window $WIN not found"
  echo "$WIN: $(current_model)"
  exit 0
fi

[ $# -ge 2 ] || { sed -n '2,16p' "$0"; exit 1; }
WIN="$(norm_window "$1")"
RAW_Q="$(echo "$2" | tr '[:upper:]' '[:lower:]' | xargs)"
EFFORT="$(echo "${3:-}" | tr '[:upper:]' '[:lower:]')"
MAX_WAIT="${4:-600}"

# Normalize dashed names like gemini-3.1-pro-high -> gemini 3.1 pro high
NORMALIZED="${RAW_Q//-/ }"
if [ -z "$EFFORT" ]; then
  if [[ "$NORMALIZED" =~ [[:space:]](low|med|medium|high|max)$ ]]; then
    EFFORT="${BASH_REMATCH[1]}"
    NORMALIZED="$(echo "$NORMALIZED" | sed -E 's/[[:space:]](low|med|medium|high|max)$//' | xargs)"
  else
    EFFORT="high"
  fi
fi

case "$EFFORT" in
  low) EFF_IDX=0 ;; med|medium) EFF_IDX=1; EFFORT=medium ;; high|max) EFF_IDX=2; EFFORT=high ;;
  *) die "effort must be low|medium|high (got '$EFFORT')" ;;
esac

tmux list-panes -t "$WIN" >/dev/null 2>&1 || die "tmux window $WIN not found"

QUERY="$NORMALIZED"
STRIPPED="$(echo "$QUERY" | sed -E 's/\b(claude|gemini|model)\b//g' | xargs)"

# Smart candidates list (first that matches in picker wins)
CANDIDATES=()
[ -n "$STRIPPED" ] && CANDIDATES+=("$STRIPPED")
[ -n "$QUERY" ] && [ "$QUERY" != "$STRIPPED" ] && CANDIDATES+=("$QUERY")
case "$STRIPPED" in
  *3.1*|*pro*) CANDIDATES+=("3.1 pro" "3.1") ;;
  *3.8*|*flash*) CANDIDATES+=("3.8 flash" "3.8") ;;
  *3.7*) CANDIDATES+=("3.7 flash" "3.7") ;;
  *3.6*) CANDIDATES+=("3.6 flash" "3.6") ;;
  *opus*) CANDIDATES+=("opus" "5.5") ;;
  *sonnet*) CANDIDATES+=("sonnet" "5.5") ;;
esac

# ---------------------------------------------------------------- lock (one switch per window)
SAFE="${WIN//[^a-zA-Z0-9]/_}"
LOCK="$WEBTERM/model_switch_${SAFE}.lock"
exec 9>"$LOCK.flock"
flock -w 30 9 || die "another model switch is already running for $WIN"

log "Request: $WIN -> '$QUERY' ($EFFORT), current: $(current_model)"

# ---------------------------------------------------------------- wait for idle
waited=0
until is_idle; do
  [ "$waited" -ge "$MAX_WAIT" ] && die "$WIN stayed busy for ${MAX_WAIT}s; model not changed"
  sleep 3; waited=$((waited+3))
done
sleep 2; is_idle || { sleep 5; is_idle || die "$WIN became busy again; retry later"; }

if [ "$WIN" = "agy:codex" ]; then
  TARGET_IDX=1
  TARGET_NAME="GPT-6.1-Sol"
  case "$STRIPPED" in
    *astra*) TARGET_IDX=2; TARGET_NAME="GPT-6-Astra" ;;
    *6*sol*|*6.0*sol*) TARGET_IDX=3; TARGET_NAME="GPT-6-Sol" ;;
    *6*luna*) TARGET_IDX=4; TARGET_NAME="GPT-6-Luna" ;;
    *5.6*sol*) TARGET_IDX=5; TARGET_NAME="GPT-5.6-Sol" ;;
    *5.6*terra*|*terra*) TARGET_IDX=6; TARGET_NAME="GPT-5.6-Terra" ;;
    *5.6*luna*) TARGET_IDX=7; TARGET_NAME="GPT-5.6-Luna" ;;
    *5.5*) TARGET_IDX=8; TARGET_NAME="GPT-5.5" ;;
    *6.1*|*sol*) TARGET_IDX=1; TARGET_NAME="GPT-6.1-Sol" ;;
    1|2|3|4|5|6|7|8) TARGET_IDX="$STRIPPED"; TARGET_NAME="Model #$STRIPPED" ;;
  esac

  echo "$$" > "$LOCK"
  cleanup_codex() { rm -f "$LOCK"; tmux send-keys -t "$WIN" Escape; sleep 0.3; tmux send-keys -t "$WIN" C-c; }
  trap cleanup_codex EXIT

  tmux send-keys -t "$WIN" "/model" Enter; sleep 0.8
  tmux send-keys -t "$WIN" Enter; sleep 0.8
  tmux send-keys -t "$WIN" "$TARGET_IDX"; sleep 0.8

  REASON_NUM=1
  case "$EFFORT" in
    low) REASON_NUM=1 ;;
    med|medium) REASON_NUM=2 ;;
    high|max) REASON_NUM=3 ;;
    extra|xhigh) REASON_NUM=4 ;;
  esac
  tmux send-keys -t "$WIN" "$REASON_NUM"; sleep 1.5

  trap - EXIT; rm -f "$LOCK"
  NOW="$(current_model)"
  log "Done: $WIN now '$NOW' ($TARGET_NAME $EFFORT)"
  echo "OK $WIN -> $TARGET_NAME $EFFORT | current: $NOW"
  exit 0
fi

# Marker so the WhatsApp bridge holds new prompts while the picker is open
echo "$$" > "$LOCK"
cleanup() { rm -f "$LOCK"; if picker_open; then tmux send-keys -t "$WIN" Escape; sleep 0.5; picker_open && tmux send-keys -t "$WIN" Escape; fi; }
trap cleanup EXIT

# ---------------------------------------------------------------- open picker
tmux send-keys -t "$WIN" -l '/model'; sleep 0.6
tmux send-keys -t "$WIN" Enter
for i in $(seq 1 15); do picker_open && break; sleep 0.4; done
picker_open || die "could not open /model picker in $WIN"

# ---------------------------------------------------------------- search
FOUND=""
for cand in "${CANDIDATES[@]}"; do
  tmux send-keys -t "$WIN" -l "$cand"; sleep 1
  item="$(highlighted_item)"
  if [ -n "$item" ] && matches_query "$item" "$cand"; then FOUND="$item"; break; fi
  clear_search
done
[ -n "$FOUND" ] || die "no model matching '$QUERY' in $WIN picker"

# ---------------------------------------------------------------- effort (if the model supports it)
if pane | grep -q 'Effort'; then
  for i in 1 2 3 4; do tmux send-keys -t "$WIN" Left; sleep 0.15; done
  for ((i=0; i<EFF_IDX; i++)); do tmux send-keys -t "$WIN" Right; sleep 0.15; done
  sleep 0.4
else
  EFFORT="n/a"
fi

tmux send-keys -t "$WIN" Enter
sleep 2.5
trap - EXIT; rm -f "$LOCK"
picker_open && { tmux send-keys -t "$WIN" Escape; sleep 0.5; picker_open && tmux send-keys -t "$WIN" Escape; die "picker did not accept selection"; }

NOW="$(current_model)"
CONFIRM="$(pane | grep -E 'Model set to' | tail -1 | sed -E 's/.*Model set to[[:space:]]*//; s/[[:space:]]+$//')"
log "Done: $WIN now '$NOW' (confirm: '$CONFIRM')"
echo "OK $WIN -> ${CONFIRM:-$NOW} | status bar: $NOW"
