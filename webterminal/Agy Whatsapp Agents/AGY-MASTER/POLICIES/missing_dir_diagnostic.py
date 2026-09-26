#!/usr/bin/env python3
"""
Missing Directory Diagnostic Protocol (Point 36 of Delete-Proof Specification)
When a project directory is reported missing, this script inspects:
1. /proc process open file descriptors
2. Filesystem mount states (df, mount)
3. Kernel ring buffer / dmesg for I/O or filesystem errors
4. GLOBAL-ARCHIVE for safe archive records
Prohibits immediate blind re-creation/overwriting.
"""

import os
import sys
import glob
import subprocess
import json
from datetime import datetime

def run_cmd(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, timeout=5)
        return res.stdout.strip()
    except Exception as e:
        return f"Error executing {cmd_list}: {e}"

def diagnose_missing_path(target_path):
    target_path = os.path.abspath(target_path)
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "target_path": target_path,
        "exists_on_disk": os.path.exists(target_path),
        "parent_exists": os.path.exists(os.path.dirname(target_path)),
        "mount_state": {},
        "open_fds": [],
        "archive_matches": [],
        "kernel_fs_alerts": [],
        "recommendation": ""
    }

    # 1. Mount state
    mount_out = run_cmd(["mount"])
    report["mount_state"]["relevant_mounts"] = [
        line for line in mount_out.splitlines()
        if any(part in line for part in ["/home", "/dev/nvme", "ext4"])
    ]

    # 2. Check /proc for open file descriptors pointing to target or (deleted)
    open_fd_matches = []
    try:
        for fd_link in glob.glob("/proc/[0-9]*/fd/*"):
            try:
                dest = os.readlink(fd_link)
                if target_path in dest:
                    pid = fd_link.split("/")[2]
                    cmdline = ""
                    try:
                        with open(f"/proc/{pid}/cmdline", "r") as f:
                            cmdline = f.read().replace("\x00", " ").strip()
                    except Exception:
                        pass
                    open_fd_matches.append({
                        "pid": pid,
                        "fd_link": fd_link,
                        "target": dest,
                        "cmdline": cmdline[:100]
                    })
            except (OSError, FileNotFoundError):
                continue
    except Exception as e:
        report["open_fd_error"] = str(e)

    report["open_fds"] = open_fd_matches[:20]

    # 3. Check GLOBAL-ARCHIVE
    archive_manifest = "/home/azureuser/GLOBAL-ARCHIVE/archive_logs/archive_manifest.jsonl"
    if os.path.exists(archive_manifest):
        try:
            with open(archive_manifest, "r", encoding="utf-8") as f:
                for line in f:
                    if target_path in line:
                        try:
                            report["archive_matches"].append(json.loads(line))
                        except Exception:
                            pass
        except Exception:
            pass

    # 4. Kernel fs errors
    dmesg_out = run_cmd(["dmesg", "-T"])
    fs_lines = [
        l for l in dmesg_out.splitlines()[-50:]
        if any(k in l.lower() for k in ["ext4", "error", "remount", "corrupt", "io error"])
    ]
    report["kernel_fs_alerts"] = fs_lines

    # Recommendation
    if report["exists_on_disk"]:
        report["recommendation"] = "Path actually exists. No recreation needed."
    elif report["open_fds"]:
        report["recommendation"] = "Path is held by active processes or unlinked fd. Do NOT recreate. Investigate holding processes."
    elif report["archive_matches"]:
        report["recommendation"] = f"Found in GLOBAL-ARCHIVE. Restore safely from archive rather than blank recreation."
    else:
        report["recommendation"] = "Path missing and not in archive. External administrative review required."

    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_to_diagnose>")
        sys.exit(1)
    
    rep = diagnose_missing_path(sys.argv[1])
    print(json.dumps(rep, indent=2))
