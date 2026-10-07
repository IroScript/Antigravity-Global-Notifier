#!/usr/bin/env python3
import sys
import sqlite3

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/sqlite3_cli.py <database> [sql]")
        sys.exit(1)
        
    db_file = sys.argv[1]
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    if len(sys.argv) == 2:
        print(f"SQLite 3 (Python CLI) connected to {db_file}")
        conn.close()
        return

    sql_arg = sys.argv[2]
    statements = [s.strip() for s in sql_arg.split(";") if s.strip()]
    cur = conn.cursor()
    for stmt in statements:
        try:
            cur.execute(stmt)
            rows = cur.fetchall()
            for r in rows:
                if len(r) == 1:
                    print(r[0])
                else:
                    print("|".join(str(v) for v in r))
        except Exception as e:
            print(f"Error: {e}")
            conn.close()
            sys.exit(1)
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
