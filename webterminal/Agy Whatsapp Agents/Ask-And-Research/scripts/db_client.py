#!/usr/bin/env python3
"""
Ask & Research Agent - Database REST API Client Helper
Provides a reliable interface to record both Ask and Research interactions
into the centralized SQLite database via REST API (port 8095) with direct SQLite fallback.
"""

import os
import sys
import json
import time
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_BASE_URL = os.environ.get("ASK_RESEARCH_API_URL", "http://127.0.0.1:8095")
BASE_DIR = os.environ.get("ASK_RESEARCH_BASE_DIR", "/home/azureuser/IroScript_Projects/Ask-And-Research-Agent")
DB_PATH = os.path.join(BASE_DIR, "ask_and_research.db")

def record_interaction(
    mode: str,
    user_query: str,
    agent_response: str,
    research_subtype: str = "none",
    topic_title: str = "",
    topic_slug: str = "",
    elements: dict = None,
    metadata: dict = None
) -> dict:
    """
    Records an interaction into the SQLite database via REST API.
    If the REST API is unavailable, falls back directly to SQLite local insertion.
    """
    mode = mode.lower().strip()
    if mode not in ("ask", "research"):
        mode = "ask"
    
    if mode == "ask" and research_subtype == "none":
        research_subtype = "none"
    elif mode == "research" and research_subtype == "none":
        research_subtype = "medium"

    payload = {
        "mode": mode,
        "user_query": user_query,
        "agent_response": agent_response,
        "research_subtype": research_subtype,
        "topic_title": topic_title or (user_query[:80] if mode == "research" else ""),
        "topic_slug": topic_slug,
        "elements": elements or {},
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # 1. Attempt REST API POST
    try:
        req = urllib.request.Request(
            f"{API_BASE_URL}/api/interactions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status in (200, 201):
                res_data = json.loads(resp.read().decode("utf-8"))
                res_data["method"] = "rest_api"
                return res_data
    except Exception as api_err:
        sys.stderr.write(f"[db_client] Notice: REST API call failed ({api_err}). Using direct SQLite fallback...\n")

    # 2. Direct SQLite Fallback
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cur = conn.cursor()
        int_id = f"intk_{int(time.time()*1000)}_{os.urandom(4).hex()}"
        cur.execute("""
        INSERT INTO interactions (
            interaction_id, timestamp, mode, research_subtype,
            user_query, agent_response, topic_title, topic_slug,
            has_elements, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            int_id, payload["timestamp"], mode, research_subtype,
            user_query, agent_response, payload["topic_title"], topic_slug,
            1 if elements else 0, json.dumps(payload["metadata"], ensure_ascii=False)
        ))
        
        if elements:
            raw_json = json.dumps(elements.get("raw_elements_json") or elements, ensure_ascii=False)
            cur.execute("""
            INSERT INTO research_elements (
                interaction_id, topic_title, research_subtype,
                executive_summary, theoretical_foundations,
                system_architecture, precursors_and_literature,
                feasibility_risk_matrix, realization_roadmap,
                raw_elements_json, excel_file_path, markdown_file_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                int_id,
                payload["topic_title"],
                research_subtype,
                elements.get("executive_summary", ""),
                elements.get("theoretical_foundations", ""),
                elements.get("system_architecture", ""),
                elements.get("precursors_and_literature", ""),
                elements.get("feasibility_risk_matrix", ""),
                elements.get("realization_roadmap", ""),
                raw_json,
                elements.get("excel_file_path", ""),
                elements.get("markdown_file_path", "")
            ))

        conn.commit()
        conn.close()
        return {
            "status": "success",
            "interaction_id": int_id,
            "mode": mode,
            "has_elements": bool(elements),
            "method": "direct_sqlite_fallback"
        }
    except Exception as db_err:
        sys.stderr.write(f"[db_client] Error: Direct SQLite insertion failed: {db_err}\n")
        return {"status": "error", "error": str(db_err)}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ask & Research Database CLI Client")
    subparsers = parser.add_subparsers(dest="command")

    rec_p = subparsers.add_parser("record")
    rec_p.add_argument("--mode", default="ask", choices=["ask", "research"])
    rec_p.add_argument("--query", required=True, help="User query or prompt")
    rec_p.add_argument("--response", required=True, help="Agent response")
    rec_p.add_argument("--subtype", default="none")
    rec_p.add_argument("--topic", default="")

    list_p = subparsers.add_parser("list")
    list_p.add_argument("--mode", default="")
    list_p.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    if args.command == "record":
        res = record_interaction(
            mode=args.mode,
            user_query=args.query,
            agent_response=args.response,
            research_subtype=args.subtype,
            topic_title=args.topic
        )
        print(json.dumps(res, indent=2))
    elif args.command == "list":
        try:
            url = f"{API_BASE_URL}/api/interactions?limit={args.limit}"
            if args.mode:
                url += f"&mode={args.mode}"
            with urllib.request.urlopen(url) as r:
                print(r.read().decode("utf-8"))
        except Exception as e:
            print(f"Error fetching from API: {e}")
    else:
        parser.print_help()
