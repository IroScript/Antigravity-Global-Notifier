#!/usr/bin/env python3
"""
Ask & Research Agent - Dedicated Database & REST API Service (v2.0 - Relational Research Architecture)
Manages persistence of all User Queries (Ask & Research) and Relational Research Artifacts
(research_runs, research_sources, research_findings, research_elements, research_exports)
into the centralized SQLite database via REST API endpoints.

Database: /home/azureuser/IroScript_Projects/Ask-And-Research-Agent/ask_and_research.db
Port: 8095
"""

import os
import sys
import json
import time
import sqlite3
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime, timezone

BASE_DIR = os.environ.get("ASK_RESEARCH_BASE_DIR", "/home/azureuser/IroScript_Projects/Ask-And-Research-Agent")
DB_PATH = os.path.join(BASE_DIR, "ask_and_research.db")
PORT = 8095
HOST = "0.0.0.0"

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Interactions table (Logs every Ask and Research turn)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interaction_id TEXT UNIQUE NOT NULL,
        timestamp TEXT NOT NULL,
        mode TEXT NOT NULL, -- 'ask' or 'research'
        research_subtype TEXT DEFAULT 'none',
        user_query TEXT NOT NULL,
        agent_response TEXT NOT NULL,
        topic_title TEXT DEFAULT '',
        topic_slug TEXT DEFAULT '',
        has_elements INTEGER DEFAULT 0,
        metadata_json TEXT DEFAULT '{}',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Relational Research Architecture Tables
    # 2.1 research_runs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_runs (
        research_id TEXT PRIMARY KEY,
        query TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'completed', -- 'in_progress', 'completed', 'failed'
        started_at TEXT NOT NULL,
        completed_at TEXT,
        metadata_json TEXT DEFAULT '{}'
    );
    """)

    # 2.2 research_sources
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_sources (
        source_id TEXT PRIMARY KEY,
        research_id TEXT NOT NULL,
        url TEXT,
        title TEXT NOT NULL,
        publisher TEXT,
        published_at TEXT,
        accessed_at TEXT NOT NULL,
        source_data TEXT DEFAULT '{}',
        FOREIGN KEY (research_id) REFERENCES research_runs(research_id) ON DELETE CASCADE
    );
    """)

    # 2.3 research_findings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_findings (
        finding_id TEXT PRIMARY KEY,
        research_id TEXT NOT NULL,
        claim TEXT NOT NULL,
        evidence TEXT NOT NULL,
        source_id TEXT,
        confidence REAL DEFAULT 1.0,
        metadata_json TEXT DEFAULT '{}',
        FOREIGN KEY (research_id) REFERENCES research_runs(research_id) ON DELETE CASCADE,
        FOREIGN KEY (source_id) REFERENCES research_sources(source_id)
    );
    """)

    # 2.4 research_elements
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_elements (
        element_id TEXT PRIMARY KEY,
        research_id TEXT NOT NULL,
        element_type TEXT NOT NULL,
        content TEXT NOT NULL,
        metadata_json TEXT DEFAULT '{}',
        FOREIGN KEY (research_id) REFERENCES research_runs(research_id) ON DELETE CASCADE
    );
    """)

    # 2.5 research_exports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_exports (
        export_id TEXT PRIMARY KEY,
        research_id TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL, -- 'excel', 'markdown_en', 'markdown_bn', 'json'
        created_at TEXT NOT NULL,
        FOREIGN KEY (research_id) REFERENCES research_runs(research_id) ON DELETE CASCADE
    );
    """)
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_mode ON interactions(mode);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_created ON interactions(created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_run ON research_sources(research_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_run ON research_findings(research_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_elements_run ON research_elements(research_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_exports_run ON research_exports(research_id);")
    
    conn.commit()
    conn.close()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/api/health":
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT count(*) as count FROM interactions;")
                int_count = cur.fetchone()["count"]
                cur.execute("SELECT count(*) as count FROM research_runs;")
                runs_count = cur.fetchone()["count"]
                cur.execute("SELECT count(*) as count FROM research_sources;")
                src_count = cur.fetchone()["count"]
                cur.execute("SELECT count(*) as count FROM research_findings;")
                find_count = cur.fetchone()["count"]
                cur.execute("SELECT count(*) as count FROM research_elements;")
                elem_count = cur.fetchone()["count"]
                cur.execute("SELECT count(*) as count FROM research_exports;")
                exp_count = cur.fetchone()["count"]
                conn.close()
                db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
                self._send_json(200, {
                    "status": "healthy",
                    "service": "Ask & Research Relational DB REST API",
                    "port": PORT,
                    "db_path": DB_PATH,
                    "db_size_bytes": db_size,
                    "total_interactions": int_count,
                    "total_research_runs": runs_count,
                    "total_sources": src_count,
                    "total_findings": find_count,
                    "total_elements": elem_count,
                    "total_exports": exp_count,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                self._send_json(500, {"status": "error", "error": str(e)})
            return

        elif path == "/api/stats":
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT count(*) as total FROM interactions;")
                total = cur.fetchone()["total"]
                cur.execute("SELECT count(*) as ask_count FROM interactions WHERE mode = 'ask';")
                ask_count = cur.fetchone()["ask_count"]
                cur.execute("SELECT count(*) as res_count FROM interactions WHERE mode = 'research';")
                res_count = cur.fetchone()["res_count"]
                cur.execute("SELECT count(*) as runs_count FROM research_runs;")
                runs_count = cur.fetchone()["runs_count"]
                cur.execute("SELECT count(*) as src_count FROM research_sources;")
                src_count = cur.fetchone()["src_count"]
                cur.execute("SELECT count(*) as find_count FROM research_findings;")
                find_count = cur.fetchone()["find_count"]
                cur.execute("SELECT count(*) as elem_count FROM research_elements;")
                elem_count = cur.fetchone()["elem_count"]
                cur.execute("SELECT count(*) as exp_count FROM research_exports;")
                exp_count = cur.fetchone()["exp_count"]
                
                cur.execute("SELECT research_subtype, count(*) as cnt FROM interactions GROUP BY research_subtype;")
                subtypes = {row["research_subtype"]: row["cnt"] for row in cur.fetchall()}
                conn.close()
                self._send_json(200, {
                    "total_interactions": total,
                    "ask_count": ask_count,
                    "research_count": res_count,
                    "research_runs_count": runs_count,
                    "sources_count": src_count,
                    "findings_count": find_count,
                    "elements_count": elem_count,
                    "exports_count": exp_count,
                    "subtypes": subtypes,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        elif path == "/api/interactions":
            limit = int(params.get("limit", [50])[0])
            offset = int(params.get("offset", [0])[0])
            mode = params.get("mode", [None])[0]
            search = params.get("search", [None])[0]

            query = "SELECT * FROM interactions WHERE 1=1"
            args = []
            if mode:
                query += " AND mode = ?"
                args.append(mode)
            if search:
                query += " AND (user_query LIKE ? OR agent_response LIKE ? OR topic_title LIKE ?)"
                wild = f"%{search}%"
                args.extend([wild, wild, wild])

            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            args.extend([limit, offset])

            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute(query, args)
                rows = [dict(row) for row in cur.fetchall()]
                conn.close()
                self._send_json(200, {
                    "count": len(rows),
                    "limit": limit,
                    "offset": offset,
                    "interactions": rows
                })
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        elif path.startswith("/api/interactions/"):
            int_id = path.split("/api/interactions/")[1].strip()
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM interactions WHERE interaction_id = ? OR id = ?", (int_id, int_id if int_id.isdigit() else -1))
                row = cur.fetchone()
                if not row:
                    conn.close()
                    self._send_json(404, {"error": "Interaction not found", "id": int_id})
                    return
                data = dict(row)
                conn.close()
                self._send_json(200, data)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        # ── RELATIONAL RESEARCH ENDPOINTS ──
        elif path == "/api/research/runs":
            limit = int(params.get("limit", [50])[0])
            offset = int(params.get("offset", [0])[0])
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM research_runs ORDER BY started_at DESC LIMIT ? OFFSET ?", (limit, offset))
                runs = [dict(r) for r in cur.fetchall()]
                conn.close()
                self._send_json(200, {"count": len(runs), "runs": runs})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        elif path.startswith("/api/research/runs/"):
            res_id = path.split("/api/research/runs/")[1].strip()
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM research_runs WHERE research_id = ?", (res_id,))
                run_row = cur.fetchone()
                if not run_row:
                    conn.close()
                    self._send_json(404, {"error": "Research run not found", "research_id": res_id})
                    return
                
                bundle = dict(run_row)
                cur.execute("SELECT * FROM research_sources WHERE research_id = ? ORDER BY accessed_at ASC", (res_id,))
                bundle["sources"] = [dict(r) for r in cur.fetchall()]
                
                cur.execute("SELECT * FROM research_findings WHERE research_id = ?", (res_id,))
                bundle["findings"] = [dict(r) for r in cur.fetchall()]
                
                cur.execute("SELECT * FROM research_elements WHERE research_id = ?", (res_id,))
                bundle["elements"] = [dict(r) for r in cur.fetchall()]
                
                cur.execute("SELECT * FROM research_exports WHERE research_id = ?", (res_id,))
                bundle["exports"] = [dict(r) for r in cur.fetchall()]
                
                conn.close()
                self._send_json(200, bundle)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        else:
            self._send_json(404, {"error": "Endpoint not found", "path": path})

    def do_POST(self):
        # 1. Interactions endpoint (backward compatible)
        if self.path in ("/api/interactions", "/api/record", "/api/record_interaction"):
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_len).decode("utf-8")
                payload = json.loads(raw_body)
            except Exception as e:
                self._send_json(400, {"error": f"Invalid JSON payload: {e}"})
                return

            user_query = payload.get("user_query") or payload.get("query") or payload.get("prompt") or ""
            agent_response = payload.get("agent_response") or payload.get("response") or payload.get("answer") or ""
            mode = (payload.get("mode") or "ask").lower().strip()
            if mode not in ("ask", "research"):
                mode = "ask"
            
            research_subtype = payload.get("research_subtype") or payload.get("subtype") or ("none" if mode == "ask" else "medium")
            topic_title = payload.get("topic_title") or payload.get("topic") or ""
            topic_slug = payload.get("topic_slug") or ""
            metadata = payload.get("metadata") or {}

            if not user_query and not topic_title:
                self._send_json(400, {"error": "Missing required field: user_query or topic_title"})
                return

            interaction_id = payload.get("interaction_id") or f"intk_{int(time.time()*1000)}_{os.urandom(4).hex()}"
            timestamp = payload.get("timestamp") or datetime.now(timezone.utc).isoformat()

            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO interactions (
                    interaction_id, timestamp, mode, research_subtype,
                    user_query, agent_response, topic_title, topic_slug,
                    has_elements, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?);
                """, (
                    interaction_id, timestamp, mode, research_subtype,
                    user_query, agent_response, topic_title, topic_slug,
                    json.dumps(metadata, ensure_ascii=False)
                ))
                inserted_id = cur.lastrowid
                conn.commit()
                conn.close()

                self._send_json(201, {
                    "status": "success",
                    "id": inserted_id,
                    "interaction_id": interaction_id,
                    "mode": mode,
                    "timestamp": timestamp
                })
            except Exception as e:
                self._send_json(500, {"error": f"Failed to persist to database: {e}"})

        # 2. Relational Research Run Endpoint
        elif self.path in ("/api/research/run", "/api/research/runs"):
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_len).decode("utf-8")
                payload = json.loads(raw_body)
            except Exception as e:
                self._send_json(400, {"error": f"Invalid JSON payload: {e}"})
                return

            research_id = payload.get("research_id") or f"res_{int(time.time()*1000)}_{os.urandom(4).hex()}"
            query = payload.get("query", "")
            title = payload.get("title", "") or query[:80]
            status = payload.get("status", "completed")
            started_at = payload.get("started_at") or datetime.now(timezone.utc).isoformat()
            completed_at = payload.get("completed_at") or datetime.now(timezone.utc).isoformat()
            run_metadata = payload.get("metadata") or {}

            sources = payload.get("sources", [])
            findings = payload.get("findings", [])
            elements = payload.get("elements", [])
            exports = payload.get("exports", [])

            try:
                conn = get_db()
                cur = conn.cursor()

                # Insert research_runs
                cur.execute("""
                INSERT OR REPLACE INTO research_runs (
                    research_id, query, title, status, started_at, completed_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    research_id, query, title, status, started_at, completed_at,
                    json.dumps(run_metadata, ensure_ascii=False)
                ))

                # Insert sources
                for s in sources:
                    sid = s.get("source_id") or f"src_{int(time.time()*1000)}_{os.urandom(3).hex()}"
                    cur.execute("""
                    INSERT OR REPLACE INTO research_sources (
                        source_id, research_id, url, title, publisher, published_at, accessed_at, source_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        sid, research_id, s.get("url", ""), s.get("title", "Untitled Source"),
                        s.get("publisher", ""), s.get("published_at", ""),
                        s.get("accessed_at", started_at),
                        json.dumps(s.get("source_data", {}), ensure_ascii=False)
                    ))

                # Insert findings
                for f in findings:
                    fid = f.get("finding_id") or f"fnd_{int(time.time()*1000)}_{os.urandom(3).hex()}"
                    cur.execute("""
                    INSERT OR REPLACE INTO research_findings (
                        finding_id, research_id, claim, evidence, source_id, confidence, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                    """, (
                        fid, research_id, f.get("claim", ""), f.get("evidence", ""),
                        f.get("source_id"), f.get("confidence", 1.0),
                        json.dumps(f.get("metadata", {}), ensure_ascii=False)
                    ))

                # Insert elements
                for e in elements:
                    eid = e.get("element_id") or f"elem_{int(time.time()*1000)}_{os.urandom(3).hex()}"
                    cur.execute("""
                    INSERT OR REPLACE INTO research_elements (
                        element_id, research_id, element_type, content, metadata_json
                    ) VALUES (?, ?, ?, ?, ?);
                    """, (
                        eid, research_id, e.get("element_type", "section"),
                        e.get("content", ""), json.dumps(e.get("metadata", {}), ensure_ascii=False)
                    ))

                # Insert exports
                for exp in exports:
                    xid = exp.get("export_id") or f"exp_{int(time.time()*1000)}_{os.urandom(3).hex()}"
                    cur.execute("""
                    INSERT OR REPLACE INTO research_exports (
                        export_id, research_id, file_path, file_type, created_at
                    ) VALUES (?, ?, ?, ?, ?);
                    """, (
                        xid, research_id, exp.get("file_path", ""), exp.get("file_type", "excel"),
                        exp.get("created_at", completed_at)
                    ))

                conn.commit()
                conn.close()

                self._send_json(201, {
                    "status": "success",
                    "research_id": research_id,
                    "sources_saved": len(sources),
                    "findings_saved": len(findings),
                    "elements_saved": len(elements),
                    "exports_saved": len(exports)
                })
            except Exception as e:
                self._send_json(500, {"error": f"Failed to persist research run: {e}"})

        else:
            self._send_json(404, {"error": "Endpoint not found", "path": self.path})

def run_server():
    init_db()
    server = ThreadedHTTPServer((HOST, PORT), RequestHandler)
    print(f"[*] Ask & Research REST API Service listening on http://{HOST}:{PORT}")
    print(f"[*] Target SQLite DB: {DB_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
