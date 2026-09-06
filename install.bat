@echo off
echo ====================================================
echo Installing Antigravity Global Notifier, Verification Gate & Rules...
echo ====================================================

set TARGET_CONFIG=%USERPROFILE%\.gemini\config
set TARGET_GEMINI=%USERPROFILE%\.gemini
set TARGET_CLI=%USERPROFILE%\.gemini\antigravity-cli

if not exist "%TARGET_CONFIG%" mkdir "%TARGET_CONFIG%"
if not exist "%TARGET_GEMINI%" mkdir "%TARGET_GEMINI%"
if not exist "%TARGET_CLI%" mkdir "%TARGET_CLI%"

copy /Y "%~dp0notify_reply.py" "%TARGET_CONFIG%\notify_reply.py"
copy /Y "%~dp0force_verify.py" "%TARGET_CONFIG%\force_verify.py"
copy /Y "%~dp0record_tool_edit.py" "%TARGET_CONFIG%\record_tool_edit.py"

copy /Y "%~dp0hooks.json" "%TARGET_CONFIG%\hooks.json"
copy /Y "%~dp0hooks.json" "%TARGET_GEMINI%\hooks.json"
copy /Y "%~dp0hooks.json" "%TARGET_CLI%\hooks.json"

copy /Y "%~dp0AGENTS.md" "%TARGET_GEMINI%\AGENTS.md"
copy /Y "%~dp0GEMINI.md" "%TARGET_GEMINI%\GEMINI.md"

set PS7_DIR=%USERPROFILE%\Documents\PowerShell
set PS5_DIR=%USERPROFILE%\Documents\WindowsPowerShell
if not exist "%PS7_DIR%" mkdir "%PS7_DIR%"
if not exist "%PS5_DIR%" mkdir "%PS5_DIR%"

echo if (Test-Path '%~dp0terminal_customizer.ps1') { . '%~dp0terminal_customizer.ps1' } > "%PS7_DIR%\Microsoft.PowerShell_profile.ps1"
echo if (Test-Path '%~dp0terminal_customizer.ps1') { . '%~dp0terminal_customizer.ps1' } > "%PS5_DIR%\Microsoft.PowerShell_profile.ps1"

echo.
echo [SUCCESS] Antigravity Global Notifier, Verification Gate & Rules installed successfully!
echo Any running or future AGY terminals will now alert on every reply, enforce verification gates, and auto-rename tabs with random colors.
pause

