#!/usr/bin/env python3
"""
Native AGY Completion Gate Stop Hook
Intercepts the agent stop event (model_stop) and enforces the 10-fold verification gate.
If an agent claims completion without a valid, fresh, machine-authoritative verification record,
the stop hook forces continuation with decision="continue".
"""

import sys
import os
import json
import time

STATE_FILE = "/home/azureuser/.agents/verification_state.json"
INCIDENT_LOG = "/home/azureuser/.agents/completion_gate_attempts.jsonl"

def log_gate_event(decision, reason, details):
    try:
        os.makedirs(os.path.dirname(INCIDENT_LOG), exist_ok=True)
        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "decision": decision,
            "reason": reason,
            "details": details
        }
        with open(INCIDENT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print(json.dumps({"decision": "allow"}))
            return
        payload = json.loads(raw)
    except Exception as e:
        # Fail closed on malformed input
        err = f"Failed to parse Stop hook payload: {e}"
        print(json.dumps({
            "decision": "continue",
            "reason": f"🛑 [STOP GATE FAIL-CLOSED]: {err}"
        }))
        return

    termination_reason = payload.get("terminationReason", "")
    final_output = payload.get("finalModelOutput", "") or payload.get("error", "")

    # Look for explicit claims of completion or success
    completion_markers = [
        "VERIFIED_SUCCESS",
        "TASK COMPLETED",
        "IMPLEMENTED_AND_VERIFIED",
        "ALL TESTS PASSED",
        "10/10 PASS",
        "TASK IS DONE",
        "ALL 10 TESTS PASSED"
    ]
    
    claims_completion = any(marker.lower() in final_output.lower() for marker in completion_markers)

    if not claims_completion:
        # Informational / conversational turns that do not claim completion are allowed
        print(json.dumps({"decision": "allow"}))
        return

    # If the model claims completion, check machine verification record
    if not os.path.exists(STATE_FILE):
        reason = "🛑 [STOP GATE DENIAL]: You claimed completion in your response, but NO machine verification record (/home/azureuser/.agents/verification_state.json) exists. You MUST execute the 10-level verification protocol (run verify_10_fold.py or unit tests) and produce empirical evidence before declaring success."
        log_gate_event("continue", reason, {"claimed_completion": True, "state_exists": False})
        print(json.dumps({"decision": "continue", "reason": reason}))
        return

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            v_state = json.load(f)
    except Exception as e:
        reason = f"🛑 [STOP GATE DENIAL]: Verification state file is unreadable or corrupted ({e}). Run verification again."
        log_gate_event("continue", reason, {"claimed_completion": True, "error": str(e)})
        print(json.dumps({"decision": "continue", "reason": reason}))
        return

    v10 = v_state.get("V10", "")
    ts = v_state.get("timestamp", 0)
    current_time = time.time()

    # Rule: V10 must be strictly VERIFIED_SUCCESS
    if v10 != "VERIFIED_SUCCESS":
        failed_vecs = v_state.get("failed_vectors", [])
        reason = f"🛑 [STOP GATE DENIAL]: Machine verification is NOT satisfied (V10 = '{v10}', failed: {failed_vecs}). All 10 verification vectors must evaluate to PASS before declaring task completion."
        log_gate_event("continue", reason, {"v10": v10, "failed_vectors": failed_vecs})
        print(json.dumps({"decision": "continue", "reason": reason}))
        return

    # Rule: Verification record must be fresh (within last 3600 seconds)
    if current_time - ts > 3600:
        reason = "🛑 [STOP GATE DENIAL]: Machine verification record is STALE (> 1 hour old). You must re-run verification for the current task."
        log_gate_event("continue", reason, {"age_seconds": current_time - ts})
        print(json.dumps({"decision": "continue", "reason": reason}))
        return

    # If all machine-authoritative conditions pass, allow the agent to stop
    log_gate_event("allow", "Verification confirmed", {"v10": v10, "timestamp": ts})
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
