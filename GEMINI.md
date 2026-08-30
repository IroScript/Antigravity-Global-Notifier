# GLOBAL AI ASSISTANT MANDATE & SYSTEM INSTRUCTIONS (`GEMINI.md`)

> 🛑 **CRITICAL SYSTEM MANDATE FOR ALL AI CODING AGENTS & TOOLS** 🛑
> 
> You are operating inside the user's workspace.
> You must strictly observe all global directives and domain-specific rules without exception.

---

## SECTION 1: GLOBAL AGENT DIRECTIVES & SYSTEM RULES

1. **BEFORE EDITING CODE:** You MUST test and verify all code changes yourself before applying them. Code must not be applied until tests pass successfully.
2. **FORCEFUL EXECUTION & WORKFLOW INTEGRITY:** Execute exactly what the user requests, test and verify fulfillment, and ensure total user workflow remains perfectly intact.
3. **RESPONSE LANGUAGE:** Always reply using Bangla script (সর্বদা বাংলা লিপি ব্যবহার করে উত্তর দাও, কোনো বাংলিশ নয়।).
4. **USER SALUTATION:** Always call the user **"ইরাক ভাইয়া"** when responding.
5. **FULL FILE PATH MANDATE (NEVER USE RELATIVE PATHS, SHORT FILENAMES, OR BASENAME LINKS):**
   - ALWAYS mention, write, and reference the complete absolute file path starting from the drive letter (e.g., `C:\Users\Irak\Desktop\AntiBotBrowser\flowboard\agent\flowboard\db\models.py` or `file:///C:/Users/Irak/...`).
   - NEVER output relative paths (like `flowboard/agent/...` or `database/models.py`) under any circumstances.
   - NEVER output standalone filenames or basenames (like `models.py`, `start_automation.bat`, or `run_prompt_fillup.bat`) under any circumstances.
   - NEVER use short filenames / basenames inside Markdown links (e.g., `[start_automation.bat](file:///...)` is STRICTLY PROHIBITED). Both the visible link text AND the target URI must contain the full absolute path (e.g., `[`file:///C:/Users/Irak/Desktop/Youtube%20Pipeline/video/1Video10Sec/start_automation.bat`](file:///C:/Users/Irak/Desktop/Youtube%20Pipeline/video/1Video10Sec/start_automation.bat)` or `C:\Users\Irak\Desktop\Youtube Pipeline\video\1Video10Sec\start_automation.bat`).
6. **GIT PUSH RULES (STRICT USER CONTROL):**
   - NEVER make the decision to push on your own.
   - NEVER question the user's command to push.
   - The decision to push MUST always come from the user. When the user says `'git push'`, execute it immediately.
   - NEVER git push from yourself until explicitly commanded.
   - NEVER delete any old git commit or perform hard resets (`git reset --hard`).
   - ALWAYS verify 200% availability in GitHub cloud using `git ls-remote origin main` and `git log -1`.
7. **KAGGLE SCRIPT FORMATTING:** Always provide a plain text version of any Kaggle script to avoid indentation issues when copy-pasting.
8. **PROTECTED PROCESS (OpenRecall):**
   - NEVER kill, stop, or terminate the `run_openrecall.py` process or any process with "openrecall" in its name.
   - Path: `C:\Users\Irak\Desktop\AI_Agent\DigitalHistory\run_openrecall.py`.
   - Exclude OpenRecall from any process cleanup commands.
9. **EVERY REPLY & COMPLETION NOTIFICATION (GLOBAL ENGINE HOOK & 5-MIN SNOOZE):** Notifications are fully automated by the Antigravity Engine lifecycle hook (`hooks.json` -> `notify_reply.py`). Agents MUST NOT manually invoke `notify_reply.py` via `run_command` to prevent duplicate popups. The engine hook automatically triggers the single, debounced desktop popup modal (with workspace folder name, full path, sound, and 5-minute snooze) on every turn.

---

## SECTION 2: ERPNEXT & FRAPPE FRAMEWORK MANDATORY DIRECTIVES (VERSION 16+ ONLY)

> 🚨 **STRICT VERSION LOCK FOR FRAPPE FRAMEWORK & ERPNEXT** 🚨

1. **VERSION 16+ ONLY:** You must **ONLY** generate, modify, or suggest code written for **Frappe Framework Version 16+** and **ERPNext Version 16+**.
2. **VERSION 15 & OLDER CODE IS STRICTLY PROHIBITED:** Under NO circumstances are you allowed to write code for **Version 15 (v15)**, Version 14 (v14), Version 13 (v13), or Version 12 (v12). Any attempt to output deprecated v15/older APIs, syntax, or patterns is completely invalid.
3. **ALWAYS INSPECT V16 DOCUMENTATION & SOURCE FIRST:** Before generating any Python, JavaScript, JSON, HTML, or configuration code, you **MUST inspect and verify the syntax against Version 16 (v16) documentation** and local v16 source code available in `frappe-framework-v16/` and `erpnext-v16/`.
4. **DO NOT GUESS API METHODS:** Verify exact class definitions, method signatures, hook definitions, and field names in v16 source code prior to implementation.
5. **PYTHON STANDARD:** Use Python 3.12+ features, strict typing annotations, and PyPika Query Builder (`frappe.qb`). Never use obsolete DB functions or raw unescaped SQL.
6. **JAVASCRIPT STANDARD:** Use modern Frappe Form Controller patterns (`frappe.ui.form.on`), `frappe.ui.Dialog`, and `frappe.call`. Never use deprecated `cur_frm` or `cur_dialog`.

---

> **Note to Agents:** This document is authoritative across all workspaces. Adhere to these instructions for all tasks.
