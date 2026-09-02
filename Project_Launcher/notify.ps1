param(
    [string]$Message = "কাজ সফলভাবে শেষ হয়েছে!",
    [string]$Title = "⚡ Antigravity AGY Alert",
    [string]$ProjectFolder = ""
)

# 1. Detect Mother Folder
if (-not $ProjectFolder -or $ProjectFolder -eq "") {
    $ProjectFolder = (Get-Location).Path
}
$folderName = Split-Path -Leaf $ProjectFolder

# 2. Play Audible Chime
try {
    [Console]::Beep(1200, 150)
    [Console]::Beep(1600, 250)
} catch {
    [System.Media.SystemSounds]::Exclamation.Play()
}

# 3. Load UI Assemblies
Add-Type -AssemblyName System.Windows.Forms, System.Drawing

# 4. Safe Win32 Helper
try {
    Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    public class FocusMover {
        [DllImport("user32.dll")]
        public static extern void SwitchToThisWindow(IntPtr hWnd, bool fAltTab);

        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("user32.dll")]
        public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

        [StructLayout(LayoutKind.Sequential)]
        public struct RECT {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;
        }
    }
"@ -ErrorAction SilentlyContinue
} catch {}

# 5. Identify Target Terminal Window
$targetHwnd = [IntPtr]::Zero
try {
    $myPid = [System.Diagnostics.Process]::GetCurrentProcess().Id
    $parentPid = (Get-CimInstance Win32_Process -Filter "ProcessId = $myPid").ParentProcessId
    if ($parentPid) {
        $pProc = Get-Process -Id $parentPid -ErrorAction SilentlyContinue
        if ($pProc -and $pProc.MainWindowHandle -ne [IntPtr]::Zero) {
            $targetHwnd = $pProc.MainWindowHandle
        }
    }
} catch {}

if ($targetHwnd -eq [IntPtr]::Zero) {
    try {
        $t = Get-Process -Name "WindowsTerminal", "pwsh", "powershell", "cmd" -ErrorAction SilentlyContinue | 
             Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero } | 
             Sort-Object StartTime -Descending | 
             Select-Object -First 1
        if ($t) { $targetHwnd = $t.MainWindowHandle }
    } catch {}
}

# 6. Format Dialog Box Message
$formattedMsg = @"
📁 প্রজেক্ট / ফোল্ডার: [$folderName]
📍 পাথ: $ProjectFolder

--------------------------------------------------
$Message
--------------------------------------------------
OK বাটনে ক্লিক করলে কার্সর ও ফোকাস সরাসরি এই ফোল্ডারের টার্মিনালে চলে যাবে।
"@

$popupTitle = "⚡ AGY: [$folderName]"

# 7. Show Interactive TopMost Dialog with OK button
[System.Windows.Forms.MessageBox]::Show(
    $formattedMsg,
    $popupTitle,
    [System.Windows.Forms.MessageBoxButtons]::OK,
    [System.Windows.Forms.MessageBoxIcon]::Information,
    [System.Windows.Forms.MessageBoxDefaultButton]::Button1,
    [System.Windows.Forms.MessageBoxOptions]::ServiceNotification
) | Out-Null

# 8. Unblockable Window Switch and Mouse Cursor Snap
if ($targetHwnd -ne [IntPtr]::Zero) {
    try {
        [FocusMover]::ShowWindow($targetHwnd, 9) # SW_RESTORE
        [FocusMover]::SwitchToThisWindow($targetHwnd, $true)
        [FocusMover]::SetForegroundWindow($targetHwnd) | Out-Null

        $rect = New-Object FocusMover+RECT
        if ([FocusMover]::GetWindowRect($targetHwnd, [ref]$rect)) {
            $cx = [int](($rect.Left + $rect.Right) / 2)
            $cy = [int](($rect.Top + $rect.Bottom) / 2)
            [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($cx, $cy)
        }
    } catch {}
}
