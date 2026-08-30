@echo off
echo ====================================================
echo Installing Antigravity Global Notifier & Rules...
echo ====================================================

set TARGET_CONFIG=%USERPROFILE%\.gemini\config
set TARGET_GEMINI=%USERPROFILE%\.gemini

if not exist "%TARGET_CONFIG%" mkdir "%TARGET_CONFIG%"
if not exist "%TARGET_GEMINI%" mkdir "%TARGET_GEMINI%"

copy /Y "%~dp0notify_reply.py" "%TARGET_CONFIG%\notify_reply.py"
copy /Y "%~dp0hooks.json" "%TARGET_CONFIG%\hooks.json"
copy /Y "%~dp0AGENTS.md" "%TARGET_GEMINI%\AGENTS.md"
copy /Y "%~dp0GEMINI.md" "%TARGET_GEMINI%\GEMINI.md"

echo.
echo [SUCCESS] Antigravity Global Notifier has been installed successfully!
echo Any running or future AGY terminals will now alert on every reply.
pause
