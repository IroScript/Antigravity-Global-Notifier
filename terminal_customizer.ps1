# ==============================================================================
# Antigravity Terminal Customizer & Theme Randomizer
# 1. Auto-sets terminal/tab title to current folder name dynamically on launch & cd
# 2. Assigns a random aesthetic terminal background & tab theme (different from previous)
# 3. Uses in-process C# TitleGuardian engine to permanently prevent 'cmd.exe' hijacking
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

# 3. Curated Aesthetic Terminal Themes (Vibrant, Distinct Backgrounds & Tabs)
$global:TerminalThemes = @(
    @{ Name = 'Deep Ocean Blue';    Bg = '#0B192C'; Fg = '#F8FAFC'; Tab = '#38BDF8' },
    @{ Name = 'Forest Emerald';     Bg = '#062E25'; Fg = '#ECFDF5'; Tab = '#34D399' },
    @{ Name = 'Velvet Purple';      Bg = '#1E1035'; Fg = '#FAF5FF'; Tab = '#C084FC' },
    @{ Name = 'Cyber Mocha Dark';   Bg = '#181825'; Fg = '#CDD6F4'; Tab = '#89B4FA' },
    @{ Name = 'Crimson Maroon';     Bg = '#2A0808'; Fg = '#FEF2F2'; Tab = '#F87171' },
    @{ Name = 'Deep Abyss Teal';    Bg = '#042F2E'; Fg = '#F0FDFA'; Tab = '#2DD4BF' },
    @{ Name = 'Warm Espresso Dark'; Bg = '#27180B'; Fg = '#FFFBEB'; Tab = '#FBBF24' },
    @{ Name = 'Synthwave Violet';   Bg = '#1F0B38'; Fg = '#FDF4FF'; Tab = '#F472B6' },
    @{ Name = 'Dark Sapphire';      Bg = '#0C1838'; Fg = '#EFF6FF'; Tab = '#60A5FA' },
    @{ Name = 'Obsidian Matrix';    Bg = '#0A0A0A'; Fg = '#4ADE80'; Tab = '#22C55E' },
    @{ Name = 'Charcoal Slate';     Bg = '#1E293B'; Fg = '#F1F5F9'; Tab = '#94A3B8' },
    @{ Name = 'Royal Indigo';       Bg = '#1E1B4B'; Fg = '#EEF2FF'; Tab = '#818CF8' },
    @{ Name = 'Nord Dark Arctic';   Bg = '#2E3440'; Fg = '#ECEFF4'; Tab = '#88C0D0' },
    @{ Name = 'Dracula Night';      Bg = '#282A36'; Fg = '#F8F8F2'; Tab = '#BD93F9' },
    @{ Name = 'Tokyo Night Dark';   Bg = '#1A1B26'; Fg = '#C0CAF5'; Tab = '#7AA2F7' }
)

# 4. Function to Set Random Terminal Background & Tab Color (different from previous)
function Set-RandomTerminalTheme {
    try {
        $trackerFile = Join-Path $env:TEMP '.terminal_last_theme'
        $lastTheme = if (Test-Path $trackerFile) { (Get-Content $trackerFile -Raw -ErrorAction SilentlyContinue).Trim() } else { '' }
        $availableThemes = $global:TerminalThemes | Where-Object { $_.Name -ne $lastTheme }
        if (-not $availableThemes -or $availableThemes.Count -eq 0) { $availableThemes = $global:TerminalThemes }
        $chosen = $availableThemes | Get-Random
        Set-Content -Path $trackerFile -Value $chosen.Name -Force -ErrorAction SilentlyContinue

        $esc = [char]27
        $bel = [char]7

        # 1. Set Terminal Window Background Color (OSC 11)
        [Console]::Write("$esc]11;$($chosen.Bg)$bel")
        # 2. Set Terminal Window Foreground Text Color (OSC 10)
        [Console]::Write("$esc]10;$($chosen.Fg)$bel")
        # 3. Set Windows Terminal Tab Color (OSC 9;4;3)
        [Console]::Write("$esc]9;4;3;$($chosen.Tab)$bel")
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
Set-RandomTerminalTheme
Update-TerminalTitle
