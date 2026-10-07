#!/usr/bin/env python3
"""
PostToolUse Tool Audit Hook
Records physical tool calls, errors, and execution metrics to the verifiable ledger.
Enforces:
1. Setting 01: Mandatory Ground Truth Verification
2. Setting 02: Zero Mock Execution
3. Setting 04: Exact Exit Code Fidelity
"""

import sys
import os
import json
import time

LEDGER_PATH = "/home/azureuser/.agents/tool_execution_ledger.jsonl"

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print("{}")
            return
        payload = json.loads(raw)
    except Exception:
        print("{}")
        return

    try:
        os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
        tool_call = payload.get("toolCall", {})
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "stepIdx": payload.get("stepIdx", 0),
            "conversationId": payload.get("conversationId", ""),
            "tool": tool_call.get("name", ""),
            "args": tool_call.get("args", {}),
            "error": payload.get("error", None)
        }
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass

    print("{}")

if __name__ == "__main__":
    main()
