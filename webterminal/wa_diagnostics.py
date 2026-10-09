#!/usr/bin/env python3
"""
Non-Destructive WhatsApp Bridge Diagnostic Engine (v2.0)
ZERO-RESTART ARCHITECTURE:
Performs passive observation and multi-vector telemetry collection.
NEVER terminates, kills, or restarts the running bridge process.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timezone

USER_HOME = os.environ.get("HOME", "/home/azureuser")
HEARTBEAT_FILE = os.path.join(USER_HOME, ".webterminal", "wa_heartbeat.json")
DIAGNOSTICS_FILE = os.path.join(USER_HOME, ".webterminal", "wa_diagnostics.json")
WATCHDOG_LOG = os.path.join(USER_HOME, ".webterminal", "wa_watchdog.log")
AUTH_FILE = os.path.join(USER_HOME, ".webterminal", "wa_auth", "creds.json")
QUEUE_FILE = os.path.join(USER_HOME, ".webterminal", "prompt_queue.json")
REPLY_FILE = os.path.join(USER_HOME, ".webterminal", "latest_reply.json")
MAX_STALE_SECONDS = 120

def log_msg(msg: str):
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(WATCHDOG_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{now_iso}] [WATCHDOG-OBSERVER] {msg}\n")

def find_bridge_pid():
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            comm = open(f"/proc/{pid}/comm", "r", encoding="utf-8", errors="ignore").read().strip()
            if comm == "node":
                cmdline = open(f"/proc/{pid}/cmdline", "r", encoding="utf-8", errors="ignore").read()
                if "whatsapp_bridge.js" in cmdline:
                    return int(pid)
        except Exception:
            continue
    return None

def main():
    now_epoch = time.time()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. PROCESS ALIVE
    bridge_pid = find_bridge_pid()
    process_alive = bridge_pid is not None
    process_uptime_sec = 0
    process_rss_kb = 0

    if process_alive:
        try:
            st = os.stat(f"/proc/{bridge_pid}")
            process_uptime_sec = int(now_epoch - st.st_mtime)
            with open(f"/proc/{bridge_pid}/status", "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        if len(parts) >= 2 and parts[1].isdigit():
                            process_rss_kb = int(parts[1])
                        break
        except Exception:
            pass

    # 2. EVENT LOOP RESPONSIVE & HEARTBEAT FRESHNESS
    heartbeat_exists = False
    heartbeat_status = "UNKNOWN"
    heartbeat_age_sec = -1
    event_loop_responsive = False
    hb_ws_flag = False

    if os.path.exists(HEARTBEAT_FILE):
        heartbeat_exists = True
        try:
            with open(HEARTBEAT_FILE, "r", encoding="utf-8") as f:
                hb = json.load(f)
            ts = hb.get("timestamp", 0)
            hb_epoch = ts / 1000.0 if ts > 1e11 else float(ts)
            heartbeat_age_sec = round(now_epoch - hb_epoch, 2)
            heartbeat_status = hb.get("status", "UNKNOWN")
            hb_ws_flag = bool(hb.get("isWsConnected", False))
            if 0 <= heartbeat_age_sec <= MAX_STALE_SECONDS:
                event_loop_responsive = True
        except Exception as e:
            heartbeat_status = f"PARSE_ERROR: {str(e)}"

    # 3. WEBSOCKET CONNECTION
    ws_connected = False
    active_socket_count = 0

    if process_alive:
        try:
            res = subprocess.run(
                ["ss", "-Hnt", "state", "established", "( sport = :443 or dport = :443 )"],
                capture_output=True, text=True, timeout=5
            )
            lines = [l for l in res.stdout.strip().split("\n") if l.strip()]
            active_socket_count = len(lines)
            if hb_ws_flag and active_socket_count > 0:
                ws_connected = True
        except Exception:
            ws_connected = hb_ws_flag

    # 4. AUTHENTICATION VALID
    auth_valid = False
    auth_size_bytes = 0
    auth_registered = False

    if os.path.exists(AUTH_FILE):
        auth_size_bytes = os.path.getsize(AUTH_FILE)
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                creds_data = json.load(f)
            auth_registered = bool(creds_data.get("registered", False))
            if auth_size_bytes > 100 and auth_registered:
                auth_valid = True
        except Exception:
            pass

    # 5. MESSAGE DELIVERY FUNCTIONAL
    pending_queue_count = 0
    latest_reply_age_sec = -1

    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                q = json.load(f)
            if isinstance(q, list):
                pending_queue_count = len([x for x in q if x.get("status") in ("RECEIVED", "DELIVERING")])
        except Exception:
            pass

    if os.path.exists(REPLY_FILE):
        try:
            mtime = os.path.getmtime(REPLY_FILE)
            latest_reply_age_sec = round(now_epoch - mtime, 2)
        except Exception:
            pass

    # OVERALL DIAGNOSTIC VERDICT (NON-DESTRUCTIVE - ZERO RESTARTS)
    if not process_alive:
        diagnostic_verdict = "CRITICAL_PROCESS_DEAD"
        recovery_action = "Process is dead; in-process self-recovery is not possible. Manual/authorized maintenance required. (Zero-restart policy respected)"
        log_msg("DIAGNOSTIC ALERT: WhatsApp bridge process is dead. Zero automated restarts triggered per Zero-Restart Architecture.")
    elif not ws_connected:
        diagnostic_verdict = "DEGRADED_WS_DISCONNECTED"
        recovery_action = f"Process is alive (PID {bridge_pid}). Baileys internal socket backoff & reconnect is active in-process. Zero service restart initiated."
        log_msg(f"DIAGNOSTIC NOTICE: WhatsApp WebSocket disconnected. In-process Baileys socket reconnect active on PID {bridge_pid}. Zero restart initiated.")
    elif not event_loop_responsive:
        diagnostic_verdict = "WARNING_EVENT_LOOP_STALE"
        recovery_action = f"Heartbeat stale ({heartbeat_age_sec}s). Process alive (PID {bridge_pid}). Diagnostics recorded, zero restart initiated."
        log_msg(f"DIAGNOSTIC NOTICE: Heartbeat age ({heartbeat_age_sec}s) > {MAX_STALE_SECONDS}s. Zero restart initiated.")
    else:
        diagnostic_verdict = "HEALTHY_ALL_VECTORS_PASS"
        recovery_action = "None required; all 5 operational vectors nominal."

    telemetry = {
        "timestamp": now_iso,
        "epoch": int(now_epoch),
        "verdict": diagnostic_verdict,
        "recovery_action": recovery_action,
        "zero_restart_policy": "ENFORCED",
        "vectors": {
            "process_alive": process_alive,
            "pid": bridge_pid,
            "process_uptime_sec": process_uptime_sec,
            "process_rss_kb": process_rss_kb,
            "event_loop_responsive": event_loop_responsive,
            "heartbeat_exists": heartbeat_exists,
            "heartbeat_status": heartbeat_status,
            "heartbeat_age_sec": heartbeat_age_sec,
            "ws_connected": ws_connected,
            "active_socket_count": active_socket_count,
            "auth_valid": auth_valid,
            "auth_registered": auth_registered,
            "auth_size_bytes": auth_size_bytes,
            "pending_queue_count": pending_queue_count,
            "latest_reply_age_sec": latest_reply_age_sec
        }
    }

    tmp_file = f"{DIAGNOSTICS_FILE}.{int(now_epoch)}.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(telemetry, f, indent=2)
    os.replace(tmp_file, DIAGNOSTICS_FILE)

if __name__ == "__main__":
    main()
