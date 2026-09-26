#!/usr/bin/env python3
"""
Reporting Agent Sentinel Watchdog: Google Drive 24/7 Live Sync Reporter
Workspace: /home/azureuser/Reporting-Agent
Role: Global Observability, Watchdog & Independent Sentinel (agy:report)
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
JSONL_LOG = os.path.join(REPORT_DIR, "gdrive_sync_metrics.jsonl")
MD_REPORT = os.path.join(REPORT_DIR, "LATEST_GDRIVE_SYNC_REPORT.md")
MASTER_DIR = os.path.join(os.path.dirname(BASE_DIR), "AGY-MASTER")
MASTER_REPORT = os.path.join(MASTER_DIR, "REPORTS", "gdrive_live_sync_sentinel.md")
INCIDENT_DIR = os.path.join(MASTER_DIR, "INCIDENTS", "active")
RCLONE_REMOTE = "personaldrive:Azure_VM_Live_Backup_Fateh_Ali"

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(MASTER_REPORT), exist_ok=True)
os.makedirs(INCIDENT_DIR, exist_ok=True)

def check_service_status():
    try:
        res = subprocess.run(
            ["systemctl", "--user", "is-active", "gdrive-live-sync"],
            capture_output=True, text=True, timeout=10
        )
        return res.stdout.strip()
    except Exception as e:
        return f"error: {e}"

def get_drive_size():
    try:
        res = subprocess.run(
            ["/usr/bin/rclone", "size", RCLONE_REMOTE],
            capture_output=True, text=True, timeout=180
        )
        if res.returncode == 0:
            lines = res.stdout.strip().split("\n")
            objects = 0
            size_str = "0 B"
            bytes_val = 0
            for l in lines:
                if "Total objects:" in l:
                    parts = l.split(":")
                    if len(parts) > 1:
                        objects = parts[1].strip().split()[0]
                elif "Total size:" in l:
                    parts = l.split(":")
                    if len(parts) > 1:
                        size_str = parts[1].strip()
                        if "(" in size_str and "Byte)" in size_str:
                            b_part = size_str.split("(")[1].split("Byte")[0].strip()
                            bytes_val = int(b_part) if b_part.isdigit() else 0
            return True, {
                "total_objects": objects,
                "total_size": size_str,
                "total_bytes": bytes_val,
                "raw": res.stdout.strip()
            }
        else:
            return False, {"error": res.stderr.strip() or res.stdout.strip()}
    except subprocess.TimeoutExpired:
        return False, {"error": "rclone size timed out after 180s"}
    except Exception as e:
        return False, {"error": str(e)}

def run_sentinel_check():
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()
    service_status = check_service_status()
    success, drive_data = get_drive_size()

    metric_record = {
        "timestamp": now_str,
        "detector": "agy:report",
        "service_status": service_status,
        "drive_query_success": success,
        "metrics": drive_data
    }

    # Append to JSONL durable storage
    with open(JSONL_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(metric_record) + "\n")

    # If service is not active, trigger incident
    if service_status != "active":
        inc_id = f"INC-SYNC-{now.strftime('%Y%m%d%H%M%S')}"
        incident = {
            "message_type": "INCIDENT",
            "incident_id": inc_id,
            "project": "gdrive_sync",
            "agent": "agy:report",
            "severity": "CRITICAL",
            "detector": "gdrive_live_sync_sentinel",
            "evidence": {
                "service_status": service_status,
                "timestamp": now_str
            },
            "recommended_action": "Restart gdrive-live-sync service and verify logs"
        }
        with open(os.path.join(INCIDENT_DIR, f"{inc_id}.json"), "w", encoding="utf-8") as f:
            json.dump(incident, f, indent=2)

    # Render Markdown Report
    objects = drive_data.get("total_objects", "N/A")
    size_str = drive_data.get("total_size", "N/A")
    raw_output = drive_data.get("raw", "") if success else drive_data.get("error", "Error")

    md_content = f"""# Google Drive 24/7 Live Sync Sentinel Health Report
**Reporting Agent (`agy:report`) Global Observability Record**

- **Last Audit Timestamp:** `{now_str}`
- **Service Status:** `{service_status.upper()}`
- **Remote Remote:** `{RCLONE_REMOTE}`
- **Total Backed Up Objects:** `{objects}`
- **Total Backup Volume:** `{size_str}`

## Raw Rclone Metric
```text
{raw_output}
```

---
*Reported independently by agy:report (Sentinel Watchdog)*
"""

    for target_path in [MD_REPORT, MASTER_REPORT]:
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(md_content)
        except Exception as e:
            pass

    print(f"[{now_str}] Check completed: Status={service_status}, Objects={objects}, Size={size_str}")

def main():
    if "--once" in sys.argv:
        run_sentinel_check()
        return

    print("Reporting Agent Sentinel Watchdog started (5-minute interval).")
    while True:
        try:
            run_sentinel_check()
        except Exception as e:
            print(f"Error in sentinel cycle: {e}", file=sys.stderr)
        time.sleep(300)

if __name__ == "__main__":
    main()
