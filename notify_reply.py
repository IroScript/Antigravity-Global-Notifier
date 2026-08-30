import sys
import json
import os
import subprocess
import threading
import time
import hashlib
import tempfile

LOCK_DIR = os.path.join(tempfile.gettempdir(), "agy_notifier_locks")
os.makedirs(LOCK_DIR, exist_ok=True)

def get_lock_path(workspace_path):
    h = hashlib.md5(workspace_path.encode('utf-8', errors='ignore')).hexdigest()
    return os.path.join(LOCK_DIR, f"lock_{h}.txt")

def is_debounced(workspace_path, cooldown_sec=5.0):
    lock_file = get_lock_path(workspace_path)
    now = time.time()
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                last_time = float(f.read().strip())
            if (now - last_time) < cooldown_sec:
                return True
        except Exception:
            pass
    try:
        with open(lock_file, "w") as f:
            f.write(str(now))
    except Exception:
        pass
    return False

def show_popup(workspace_path="অজানা ওয়ার্কস্পেস"):
    import tkinter as tk
    import winsound

    def play_sound():
        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

    threading.Thread(target=play_sound, daemon=True).start()

    root = tk.Tk()
    root.title("⚡ AGY - রিপ্লাই নোটিফিকেশন")
    root.geometry("540x260")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.configure(bg="#181825")

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 540) // 2
    y = (root.winfo_screenheight() - 260) // 2
    root.geometry(f"+{x}+{y}")

    # Header
    header_frame = tk.Frame(root, bg="#313244", padx=18, pady=12)
    header_frame.pack(fill="x")

    title_label = tk.Label(
        header_frame,
        text="🔔 ইরাক ভাইয়া, এজেন্টের রিপ্লাই শেষ হয়েছে!",
        font=("Segoe UI", 12, "bold"),
        fg="#a6e3a1",
        bg="#313244"
    )
    title_label.pack(anchor="w")

    subtitle_label = tk.Label(
        header_frame,
        text="পরবর্তী কমান্ড বা ইনপুটের জন্য অপেক্ষা করছে...",
        font=("Segoe UI", 9),
        fg="#cdd6f4",
        bg="#313244"
    )
    subtitle_label.pack(anchor="w")

    # Content
    content_frame = tk.Frame(root, bg="#181825", padx=18, pady=14)
    content_frame.pack(fill="both", expand=True)

    clean_ws = workspace_path.rstrip(r"\/")
    folder_name = os.path.basename(clean_ws) or clean_ws
    ws_label = tk.Label(
        content_frame,
        text=f"📁 প্রজেক্ট / ফোল্ডার: [{folder_name}]",
        font=("Segoe UI", 10, "bold"),
        fg="#89b4fa",
        bg="#181825"
    )
    ws_label.pack(anchor="w", pady=(0, 4))

    path_label = tk.Label(
        content_frame,
        text=f"📍 সম্পূর্ণ পাথ: {workspace_path}",
        font=("Consolas", 8),
        fg="#bac2de",
        bg="#181825",
        wraplength=500,
        justify="left"
    )
    path_label.pack(anchor="w", pady=(0, 8))

    # Button actions
    def on_ok():
        root.destroy()

    def on_snooze():
        root.destroy()
        snooze_script = os.path.abspath(__file__)
        cmd = [sys.executable, snooze_script, "--snooze", "300", workspace_path]
        subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

    btn_frame = tk.Frame(root, bg="#181825", padx=18, pady=12)
    btn_frame.pack(fill="x", side="bottom")

    ok_btn = tk.Button(
        btn_frame,
        text="  ✅ ঠিক আছে (OK)  ",
        font=("Segoe UI", 10, "bold"),
        bg="#a6e3a1",
        fg="#11111b",
        activebackground="#94e2d5",
        cursor="hand2",
        relief="flat",
        padx=12,
        pady=6,
        command=on_ok
    )
    ok_btn.pack(side="right", padx=(10, 0))

    snooze_btn = tk.Button(
        btn_frame,
        text="  ⏰ ৫ মিনিট স্নুজ (Snooze 5m)  ",
        font=("Segoe UI", 9),
        bg="#fab387",
        fg="#11111b",
        activebackground="#f9e2af",
        cursor="hand2",
        relief="flat",
        padx=10,
        pady=6,
        command=on_snooze
    )
    snooze_btn.pack(side="right")

    root.lift()
    root.focus_force()
    root.mainloop()

def main():
    if "--snooze" in sys.argv:
        try:
            snooze_sec = int(sys.argv[2])
            ws_path = sys.argv[3] if len(sys.argv) > 3 else "ওয়ার্কস্পেস"
        except Exception:
            snooze_sec = 300
            ws_path = "ওয়ার্কস্পেস"
        time.sleep(snooze_sec)
        show_popup(workspace_path=ws_path)
        return

    if "--show-ui" in sys.argv:
        ws_path = sys.argv[2] if len(sys.argv) > 2 else "ওয়ার্কস্পেস"
        show_popup(workspace_path=ws_path)
        return

    ws_path = os.getcwd()
    should_notify = True

    try:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                payload = json.loads(stdin_data)
                
                # Check termination reason: only trigger if model finished
                term_reason = payload.get("terminationReason", "")
                if term_reason and term_reason != "model_stop":
                    should_notify = False

                ws_paths = payload.get("workspacePaths", [])
                if ws_paths:
                    ws_path = ws_paths[0]
    except Exception:
        pass

    # Satisfy hook contract immediately so AGY is not blocked
    print(json.dumps({}))
    sys.stdout.flush()

    if not should_notify:
        return

    # Check 5-second debounce so double calls from hooks are ignored
    if is_debounced(ws_path, cooldown_sec=5.0):
        return

    script_path = os.path.abspath(__file__)
    cmd = [sys.executable, script_path, "--show-ui", ws_path]
    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

if __name__ == "__main__":
    main()
