import sys
import json
import os
import time

def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({}))
            return

        payload = json.loads(raw_input)
        workspace_paths = payload.get("workspacePaths", [])
        
        # Determine workspace directory
        workspace_dir = None
        if workspace_paths and len(workspace_paths) > 0:
            candidate = workspace_paths[0]
            if os.path.isdir(candidate):
                workspace_dir = candidate

        if workspace_dir:
            evidence_dir = os.path.join(workspace_dir, ".agy_evidence")
            os.makedirs(evidence_dir, exist_ok=True)
            
            edit_record = {
                "last_edit_time": time.time(),
                "pending_verification": True,
                "stepIdx": payload.get("stepIdx", 0)
            }
            
            edit_file = os.path.join(evidence_dir, "last_edit.json")
            with open(edit_file, "w", encoding="utf-8") as f:
                json.dump(edit_record, f, indent=2)

    except Exception:
        pass
    finally:
        # PostToolUse contract requires empty JSON object on stdout
        print(json.dumps({}))
        sys.exit(0)

if __name__ == "__main__":
    main()
