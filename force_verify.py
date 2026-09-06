import sys
import json
import os
import time
import subprocess

TEST_KEYWORDS = [
    "pytest", "unittest", "npm test", "npm run test", "cargo test",
    "go test", "vitest", "jest", "py_compile", "test_", "_test",
    "verify", "ctest", "rake test"
]

def check_workspace_custom_script(workspace_dir):
    if not workspace_dir or not os.path.isdir(workspace_dir):
        return None
    
    scripts_dir = os.path.join(workspace_dir, ".agents", "scripts")
    if not os.path.isdir(scripts_dir):
        return None

    # Check for python script, batch script, or powershell script
    candidates = [
        ("python", os.path.join(scripts_dir, "force_verify.py")),
        ("cmd", os.path.join(scripts_dir, "force_verify.bat")),
        ("powershell", os.path.join(scripts_dir, "force_verify.ps1"))
    ]

    for runner, script_path in candidates:
        if os.path.isfile(script_path):
            try:
                if runner == "python":
                    cmd = [sys.executable, script_path]
                elif runner == "cmd":
                    cmd = [script_path]
                else:
                    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]

                res = subprocess.run(cmd, cwd=workspace_dir, capture_output=True, text=True, timeout=30)
                if res.returncode != 0:
                    err_msg = res.stderr.strip() or res.stdout.strip() or f"Script exited with code {res.returncode}"
                    return False, err_msg
                else:
                    return True, "Workspace verification script passed."
            except Exception as e:
                return False, f"Error running {script_path}: {str(e)}"

    return None

def analyze_transcript(transcript_path):
    if not transcript_path or not os.path.isfile(transcript_path):
        return False, False, "No transcript"

    had_code_edit = False
    last_edit_idx = -1
    had_test_after_edit = False
    current_turn_steps = []

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        # Find the last USER_INPUT index
        last_user_idx = 0
        for i, line in enumerate(lines):
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    last_user_idx = i
            except Exception:
                continue

        turn_lines = lines[last_user_idx:]
        
        step_counter = 0
        for line in turn_lines:
            try:
                data = json.loads(line)
            except Exception:
                continue

            tool_calls = data.get("tool_calls", [])
            for tc in tool_calls:
                name = tc.get("name", "")
                args = tc.get("args", {})
                
                # Check for edits
                if name in ["write_to_file", "replace_file_content", "edit_file", "apply_diff"]:
                    had_code_edit = True
                    last_edit_idx = step_counter

                # Check for test / verification command
                if name == "run_command":
                    cmd_line = args.get("CommandLine", "").lower()
                    if any(kw in cmd_line for kw in TEST_KEYWORDS):
                        if had_code_edit and step_counter >= last_edit_idx:
                            had_test_after_edit = True

                step_counter += 1

        return had_code_edit, had_test_after_edit, "Analyzed"
    except Exception as e:
        return False, False, f"Transcript parse error: {str(e)}"

def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    termination_reason = payload.get("terminationReason", "model_stop")
    execution_num = payload.get("executionNum", 1)
    workspace_paths = payload.get("workspacePaths", [])
    transcript_path = payload.get("transcriptPath", "")

    # Rule 1: Only intercept clean stops (model_stop). Do not block errors or cancellations.
    if termination_reason != "model_stop":
        print(json.dumps({"decision": "allow"}))
        return

    # Rule 2: Anti-deadlock guard (if blocked 3 times already, allow stop)
    if execution_num >= 4:
        print(json.dumps({"decision": "allow"}))
        return

    workspace_dir = workspace_paths[0] if (workspace_paths and os.path.isdir(workspace_paths[0])) else None

    # Rule 3: Check workspace custom verification script if present
    if workspace_dir:
        custom_res = check_workspace_custom_script(workspace_dir)
        if custom_res is not None:
            passed, msg = custom_res
            if not passed:
                print(json.dumps({
                    "decision": "continue",
                    "reason": f"🛑 ওয়ার্কস্পেস ভেরিফিকেশন স্ক্রিপ্ট (.agents/scripts/force_verify) ব্যর্থ হয়েছে:\n{msg}"
                }))
                return
            else:
                print(json.dumps({"decision": "allow"}))
                return

    # Rule 4: Check .agy_evidence/last_test_run.json and .agy_evidence/last_edit.json
    evidence_dir = os.path.join(workspace_dir, ".agy_evidence") if workspace_dir else None
    pending_edit_flag = False
    last_edit_time = 0

    if evidence_dir and os.path.isdir(evidence_dir):
        last_edit_file = os.path.join(evidence_dir, "last_edit.json")
        if os.path.isfile(last_edit_file):
            try:
                with open(last_edit_file, "r", encoding="utf-8") as f:
                    edit_data = json.load(f)
                    pending_edit_flag = edit_data.get("pending_verification", False)
                    last_edit_time = edit_data.get("last_edit_time", 0)
            except Exception:
                pass

        last_test_file = os.path.join(evidence_dir, "last_test_run.json")
        if os.path.isfile(last_test_file):
            try:
                with open(last_test_file, "r", encoding="utf-8") as f:
                    test_data = json.load(f)
                    exit_code = test_data.get("exit_code")
                    test_time = test_data.get("timestamp", 0)
                    
                    # If test ran after last edit
                    if test_time >= last_edit_time:
                        if exit_code == 0:
                            # Test passed, clear pending flag
                            if pending_edit_flag:
                                edit_data["pending_verification"] = False
                                with open(last_edit_file, "w", encoding="utf-8") as wf:
                                    json.dump(edit_data, wf)
                            print(json.dumps({"decision": "allow"}))
                            return
                        else:
                            print(json.dumps({
                                "decision": "continue",
                                "reason": f"🛑 টেস্ট প্রমাণ ব্যর্থ (Exit Code {exit_code})। ত্রুটি ঠিক না করে এবং টেস্ট সফল না করে কাজ শেষ ঘোষণা করা যাবে না।"
                            }))
                            return
            except Exception:
                pass

    # Rule 5: Inspect transcript for code edits vs tests in current turn
    had_code_edit, had_test_after_edit, _ = analyze_transcript(transcript_path)

    # If code was edited, but no test was run
    if (had_code_edit or pending_edit_flag) and not had_test_after_edit:
        print(json.dumps({
            "decision": "continue",
            "reason": "🛑 কঠোর ভেরিফিকেশন প্রোটোকল: এই টার্নে কোড পরিবর্তন করা হয়েছে কিন্তু কোনো টেস্ট বা ভেরিফিকেশন কমান্ড চালানো হয়নি। 'কাজ শেষ' বলার পূর্বে সংশ্লিষ্ট টেস্ট চালান এবং ফলাফল প্রমাণ করুন।"
        }))
        return

    # If test passed in transcript or no edits occurred, allow
    if pending_edit_flag and had_test_after_edit and evidence_dir:
        try:
            last_edit_file = os.path.join(evidence_dir, "last_edit.json")
            if os.path.isfile(last_edit_file):
                edit_data["pending_verification"] = False
                with open(last_edit_file, "w", encoding="utf-8") as wf:
                    json.dump(edit_data, wf)
        except Exception:
            pass

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
