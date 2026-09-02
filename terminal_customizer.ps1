# ==============================================================================
# Antigravity Terminal Customizer & Per-Folder Permanent Theme Engine
# 1. Auto-sets terminal/tab title to current folder name dynamically on launch & cd
# 2. Generates a random aesthetic theme on 1st open and saves permanently in folder (.terminal_theme.json)
# 3. Loads the exact saved theme on 2nd+ open without external dependencies
# 4. Uses in-process C# TitleGuardian engine to permanently prevent 'cmd.exe' hijacking
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

# 3. Curated Ultra-Lightweight Pastel Themes (Near-White Backgrounds, High-Contrast Text)
$global:TerminalThemes = @(
    @{ Name = 'Pastel Soft Yellow';    Bg = '#FEFCE8'; Fg = '#1C1917'; Tab = '#EAB308' },
    @{ Name = 'Pastel Mint Green';     Bg = '#F0FDF4'; Fg = '#14532D'; Tab = '#22C55E' },
    @{ Name = 'Pastel Blush Rose';     Bg = '#FFF1F2'; Fg = '#881337'; Tab = '#F43F5E' },
    @{ Name = 'Pastel Sky Blue';       Bg = '#F0F9FF'; Fg = '#0C4A6E'; Tab = '#0EA5E9' },
    @{ Name = 'Pastel Peach Coral';    Bg = '#FFF7ED'; Fg = '#7C2D12'; Tab = '#F97316' },
    @{ Name = 'Pastel Lavender';       Bg = '#FAF5FF'; Fg = '#581C87'; Tab = '#A855F7' },
    @{ Name = 'Pastel Glacier Teal';   Bg = '#ECFEFF'; Fg = '#164E63'; Tab = '#06B6D4' },
    @{ Name = 'Pastel Warm Honey';     Bg = '#FFFBEB'; Fg = '#78350F'; Tab = '#F59E0B' },
    @{ Name = 'Pastel Matcha Lime';    Bg = '#F7FEE7'; Fg = '#365314'; Tab = '#84CC16' },
    @{ Name = 'Pastel Soft Pink';      Bg = '#FDF2F8'; Fg = '#831843'; Tab = '#EC4899' },
    @{ Name = 'Pastel Powder Violet';  Bg = '#F5F3FF'; Fg = '#4C1D95'; Tab = '#8B5CF6' },
    @{ Name = 'Pastel Clean Slate';    Bg = '#F8FAFC'; Fg = '#0F172A'; Tab = '#64748B' },
    @{ Name = 'Pastel Soft Crimson';   Bg = '#FEF2F2'; Fg = '#7F1D1D'; Tab = '#EF4444' },
    @{ Name = 'Pastel Ivory Sand';     Bg = '#FDFBF7'; Fg = '#1C1917'; Tab = '#D97706' },
    @{ Name = 'Pastel Aqua Marine';    Bg = '#F0FDFA'; Fg = '#134E4A'; Tab = '#14B8A6' }
)

# 4. Function to Apply or Save Permanent Folder Theme (.terminal_theme.json)
function Apply-FolderTerminalTheme {
    param([string]$FolderPath = $executionContext.SessionState.Path.CurrentLocation.Path)
    try {
        if (-not (Test-Path -LiteralPath $FolderPath)) { return }

        $themeFile = Join-Path $FolderPath ".terminal_theme.json"
        $chosen = $null

        # Check if this folder already has a permanent saved theme
        if (Test-Path -LiteralPath $themeFile) {
            try {
                $raw = Get-Content -LiteralPath $themeFile -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
                if ($raw) {
                    $saved = ConvertFrom-Json $raw -ErrorAction SilentlyContinue
                    if ($saved -and $saved.bg -and $saved.fg) {
                        $chosen = $saved
                    }
                }
            } catch {}
        }

        # If 1st time opening this folder, pick random theme (different from previous) & save in folder
        if (-not $chosen) {
            $trackerFile = Join-Path $env:TEMP '.terminal_last_theme'
            $lastTheme = if (Test-Path $trackerFile) { (Get-Content $trackerFile -Raw -ErrorAction SilentlyContinue).Trim() } else { '' }
            $availableThemes = $global:TerminalThemes | Where-Object { $_.Name -ne $lastTheme }
            if (-not $availableThemes -or $availableThemes.Count -eq 0) { $availableThemes = $global:TerminalThemes }
            $chosenTheme = $availableThemes | Get-Random
            Set-Content -Path $trackerFile -Value $chosenTheme.Name -Force -ErrorAction SilentlyContinue

            $chosen = [PSCustomObject]@{
                name = $chosenTheme.Name
                bg   = $chosenTheme.Bg
                fg   = $chosenTheme.Fg
                tab  = $chosenTheme.Tab
            }

            # Save permanently inside the folder
            try {
                $jsonStr = ConvertTo-Json $chosen -Depth 2
                [System.IO.File]::WriteAllText($themeFile, $jsonStr, [System.Text.Encoding]::UTF8)
            } catch {}
        }

        # Apply OSC sequences to Windows Terminal / Console
        $esc = [char]27
        $bel = [char]7

        # 1. Set Terminal Window Background Color (OSC 11)
        [Console]::Write("$esc]11;$($chosen.bg)$bel")
        # 2. Set Terminal Window Foreground Text Color (OSC 10)
        [Console]::Write("$esc]10;$($chosen.fg)$bel")
        # 3. Set Windows Terminal Tab Color (OSC 9;4;3)
        [Console]::Write("$esc]9;4;3;$($chosen.tab)$bel")
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
    Apply-FolderTerminalTheme
    "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
}

# 7. Initialize immediately on terminal session launch
Update-TerminalTitle
Apply-FolderTerminalTheme
