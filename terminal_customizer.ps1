# ==============================================================================
# Antigravity Terminal Customizer
# 1. Auto-sets terminal/tab title to current folder name dynamically on launch & cd
# 2. Assigns a random aesthetic Windows Terminal tab color (different from previous)
# 3. Uses in-process C# TitleGuardian thread to permanently prevent 'cmd.exe' hijacking
# ==============================================================================

# 1. UTF-8 Support
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
} catch {}

# 2. In-Process Title Guardian Engine (Continuous protection across agy, auth, tools)
if (-not ([System.Management.Automation.PSTypeName]'TitleGuardian').Type) {
    $guardianSource = @'
using System;
using System.Threading;
using System.Threading.Tasks;

public class TitleGuardian {
    private static CancellationTokenSource _cts;
    public static string TargetTitle = string.Empty;

    public static void Start() {
        if (_cts != null) return;
        _cts = new CancellationTokenSource();
        var token = _cts.Token;
        Task.Run(async () => {
            while (!token.IsCancellationRequested) {
                try {
                    if (!string.IsNullOrEmpty(TargetTitle)) {
                        if (Console.Title != TargetTitle) {
                            Console.Title = TargetTitle;
                        }
                    }
                } catch {}
                try {
                    await Task.Delay(300, token);
                } catch {}
            }
        }, token);
    }

    public static void SetTitle(string title) {
        TargetTitle = title;
        try {
            Console.Title = title;
        } catch {}
    }
}
'@
    Add-Type -TypeDefinition $guardianSource -ErrorAction SilentlyContinue
}

# 3. Curated Aesthetic Tab Colors (Vibrant, Modern & Distinct)
$global:TabColors = @(
    '#3B82F6', # Electric Blue
    '#10B981', # Emerald Green
    '#F59E0B', # Amber
    '#EF4444', # Red
    '#8B5CF6', # Violet
    '#EC4899', # Pink
    '#06B6D4', # Cyan
    '#F97316', # Orange
    '#14B8A6', # Teal
    '#6366F1', # Indigo
    '#D946EF', # Fuchsia
    '#84CC16', # Lime
    '#E11D48', # Rose
    '#0EA5E9', # Sky Blue
    '#A855F7', # Purple
    '#22C55E', # Green
    '#F43F5E', # Crimson
    '#0284C7', # Light Blue
    '#7C3AED', # Deep Violet
    '#059669', # Mint Teal
    '#D97706', # Warm Gold
    '#EA580C', # Burnt Orange
    '#4F46E5', # Neon Indigo
    '#DB2777'  # Ruby
)

# 4. Function to Set Random Tab Color (different from previous terminal)
function Set-RandomTerminalTabColor {
    try {
        $trackerFile = Join-Path $env:TEMP '.wt_last_tab_color'
        $lastColor = if (Test-Path $trackerFile) { (Get-Content $trackerFile -Raw -ErrorAction SilentlyContinue).Trim() } else { '' }
        $availableColors = $global:TabColors | Where-Object { $_ -ne $lastColor }
        if (-not $availableColors -or $availableColors.Count -eq 0) { $availableColors = $global:TabColors }
        $chosenColor = $availableColors | Get-Random
        Set-Content -Path $trackerFile -Value $chosenColor -Force -ErrorAction SilentlyContinue
        
        $esc = [char]27
        $bel = [char]7
        [Console]::Write("$esc]9;4;3;$chosenColor$bel")
    } catch {}
}

# 5. Function to Update Terminal / Tab Title to Current Folder Name
function Update-TerminalTitle {
    try {
        $loc = $executionContext.SessionState.Path.CurrentLocation.Path
        $folderName = if ($loc -match '^[A-Za-z]:\\?$') { $loc } else { Split-Path -Leaf $loc }
        if (-not $folderName) { $folderName = $loc }
        
        $Host.UI.RawUI.WindowTitle = $folderName
        
        $esc = [char]27
        $bel = [char]7
        [Console]::Write("$esc]0;$folderName$bel")

        if (([System.Management.Automation.PSTypeName]'TitleGuardian').Type) {
            [TitleGuardian]::SetTitle($folderName)
            [TitleGuardian]::Start()
        }
    } catch {}
}

# 6. Hook into PowerShell Prompt for dynamic updates on 'cd'
function prompt {
    Update-TerminalTitle
    "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
}

# 7. Initialize immediately on terminal session launch
Set-RandomTerminalTabColor
Update-TerminalTitle
