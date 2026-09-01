import sys
import os
import json
import subprocess
import threading
import time
import ctypes
import tempfile

TEMP_DIR = os.environ.get("TEMP", r"C:\Windows\Temp")
DEBOUNCE_FILE = os.path.join(TEMP_DIR, "agy_beautiful_notify_debounce.txt")
WINDOW_TITLE = "⚡ AGY - রিপ্লাই নোটিফিকেশন"

def is_debounced(cooldown=3.0):
    now = time.time()
    if os.path.exists(DEBOUNCE_FILE):
        try:
            with open(DEBOUNCE_FILE, "r") as f:
                last_time = float(f.read().strip())
            if (now - last_time) < cooldown:
                return True
        except Exception:
            pass
    try:
        with open(DEBOUNCE_FILE, "w") as f:
            f.write(str(now))
    except Exception:
        pass
    return False

def show_beautiful_popup(workspace_path="C:\\Users\\Irak\\Desktop"):
    # Check if a window with this title is already open
    hwnd = ctypes.windll.user32.FindWindowW(None, WINDOW_TITLE)
    if hwnd:
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        return

    import tkinter as tk
    import winsound

    # Play alert sound
    def play_sound():
        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

    threading.Thread(target=play_sound, daemon=True).start()

    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry("540x260")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.configure(bg="#181825")

    # Center window on screen
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - 540) // 2
    y = (screen_h - 260) // 2
    root.geometry(f"+{x}+{y}")

    # Header frame
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
        text="পরবর্তী কমান্ড বা ইনপুটের জন্য টার্মিনাল অপেক্ষা করছে...",
        font=("Segoe UI", 9),
        fg="#cdd6f4",
        bg="#313244"
    )
    subtitle_label.pack(anchor="w", pady=(2, 0))

    # Content frame
    content_frame = tk.Frame(root, bg="#181825", padx=18, pady=14)
    content_frame.pack(fill="both", expand=True)

    norm_ws = os.path.normpath(workspace_path)
    clean_ws = norm_ws.rstrip(r"\/")
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
        text=f"📍 সম্পূর্ণ পাথ: {norm_ws}",
        font=("Consolas", 9),
        fg="#bac2de",
        bg="#181825",
        wraplength=500,
        justify="left"
    )
    path_label.pack(anchor="w", pady=(0, 6))

    # Button handlers
    def on_ok():
        root.destroy()

    def on_snooze():
        root.destroy()
        script_path = os.path.abspath(__file__)
        cmd = [sys.executable, script_path, "--snooze", "300", norm_ws]
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
        activeforeground="#11111b",
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
        font=("Segoe UI", 9, "bold"),
        bg="#fab387",
        fg="#11111b",
        activebackground="#f9e2af",
        activeforeground="#11111b",
        cursor="hand2",
        relief="flat",
        padx=10,
        pady=6,
        command=on_snooze
    )
    snooze_btn.pack(side="right")

    root.protocol("WM_DELETE_WINDOW", on_ok)
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
        show_beautiful_popup(workspace_path=ws_path)
        return

    if "--show-ui" in sys.argv:
        ws_path = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
        show_beautiful_popup(workspace_path=ws_path)
        return

    ws_path = os.getcwd()
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            if data.strip():
                payload = json.loads(data)
                ws_paths = payload.get("workspacePaths", [])
                if ws_paths:
                    ws_path = ws_paths[0]
    except Exception:
        pass

    # Satisfy hook contract immediately
    print(json.dumps({}))
    sys.stdout.flush()

    if is_debounced(3.0):
        return

    script_path = os.path.abspath(__file__)
    cmd = [sys.executable, script_path, "--show-ui", ws_path]
    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

if __name__ == "__main__":
    main()
