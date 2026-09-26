#!/usr/bin/env python3
"""
Safe Archive Engine (Points 32-35 of Delete-Proof Specification)
Converts any requested deletion into a secure, verifiable archive operation.
Never deletes the original object without verified archive staging and audit record.
"""

import os
import sys
import shutil
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

ARCHIVE_ROOT = Path("/home/azureuser/GLOBAL-ARCHIVE")
MANIFEST_FILE = ARCHIVE_ROOT / "archive_logs" / "archive_manifest.jsonl"

def calculate_checksum(file_path):
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "checksum_unavailable"

def archive_path(target_path_str, reason="Requested by user or agent"):
    target = Path(target_path_str).resolve()
    if not target.exists():
        return {
            "status": "ERROR",
            "message": f"Target path {target} does not exist"
        }

    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y%m%d_%H%M%S_%f")
    archive_dest_dir = ARCHIVE_ROOT / date_str / f"{timestamp_str}_{target.name}"
    archive_dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = archive_dest_dir / target.name

    try:
        if target.is_dir():
            shutil.copytree(str(target), str(dest_path), symlinks=True)
            original_type = "directory"
            file_count = sum(1 for _ in dest_path.rglob("*"))
            checksum = f"{file_count}_items"
        else:
            shutil.copy2(str(target), str(dest_path))
            original_type = "file"
            checksum = calculate_checksum(dest_path)

        manifest_entry = {
            "timestamp": now.isoformat() + "Z",
            "original_path": str(target),
            "archive_path": str(dest_path),
            "type": original_type,
            "checksum": checksum,
            "reason": reason,
            "status": "ARCHIVED_SAFELY"
        }

        with open(MANIFEST_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(manifest_entry) + "\n")

        return {
            "status": "SUCCESS",
            "message": f"Archived safely to {dest_path}",
            "manifest": manifest_entry
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to safely archive {target}: {str(e)}"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_to_archive> [reason]")
        sys.exit(1)
    
    target_arg = sys.argv[1]
    reason_arg = sys.argv[2] if len(sys.argv) > 2 else "Manual archive request"
    res = archive_path(target_arg, reason_arg)
    print(json.dumps(res, indent=2))
