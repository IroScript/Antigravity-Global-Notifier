# Master Dynamic Project Launcher for Irak Bhaiya
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) { $scriptDir = "C:\Users\Irak\Desktop\Project_Launcher" }
$configFile = Join-Path $scriptDir "projects_config.json"
$notifyScript = Join-Path $scriptDir "notify.ps1"

function Load-Projects {
    if (Test-Path $configFile) {
        $json = Get-Content -Path $configFile -Raw -Encoding UTF8
        if ([string]::IsNullOrWhiteSpace($json)) { return @() }
        $data = ConvertFrom-Json $json
        $rawList = @()
        if ($data -is [System.Array]) {
            $rawList = $data
        } elseif ($data.PSObject.Properties['value']) {
            $rawList = $data.value
        } else {
            $rawList = @($data)
        }
        $validProjects = @()
        foreach ($item in $rawList) {
            if ($item -and $item.Id -and $item.Name) {
                $validProjects += $item
            }
        }
        return $validProjects
    }
    return @()
}

function Save-Projects($list) {
    $cleanList = @()
    foreach ($item in $list) {
        if ($item -and $item.Id -and $item.Name) {
            $cleanList += [PSCustomObject]@{
                Id = $item.Id.ToString()
                Name = $item.Name.ToString()
                Folder = $item.Folder.ToString()
                BgColor = if ($item.BgColor) { $item.BgColor.ToString() } else { "DarkBlue" }
                FgColor = if ($item.FgColor) { $item.FgColor.ToString() } else { "White" }
                Tag = if ($item.Tag) { $item.Tag.ToString() } else { "ACTIVE PROJECT" }
            }
        }
    }
    $json = ConvertTo-Json @($cleanList) -Depth 5
    [System.IO.File]::WriteAllText($configFile, $json, [System.Text.Encoding]::UTF8)
}

function Show-Menu($projects) {
    Clear-Host
    Write-Host "`n==========================================================================" -ForegroundColor Cyan
    Write-Host "             🚀 IRAK BHAIYA - MASTER WORK ORCHESTRATOR 🚀                " -ForegroundColor Yellow
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host "Select a project to launch in dedicated Color-Themed AGY Terminal:`n" -ForegroundColor White

    foreach ($p in $projects) {
        if (-not $p -or -not $p.Id -or -not $p.Name) { continue }
        $colorBadge = switch ($p.BgColor) {
            "DarkRed"     { "[ RED ]" }
            "DarkBlue"    { "[ BLUE ]" }
            "DarkGreen"   { "[ GREEN ]" }
            "DarkMagenta" { "[ PURPLE ]" }
            "DarkCyan"    { "[ CYAN ]" }
            "DarkYellow"  { "[ YELLOW ]" }
            "DarkGray"    { "[ GRAY ]" }
            default       { "[ DEFAULT ]" }
        }
        Write-Host "  $($p.Id.ToString().PadLeft(2)) " -NoNewline -ForegroundColor Yellow
        Write-Host "$colorBadge " -NoNewline -ForegroundColor Cyan
        Write-Host "$($p.Name.ToString().PadRight(30))" -NoNewline -ForegroundColor White
        Write-Host " → $($p.Tag)" -ForegroundColor Gray
    }
    Write-Host "`n--------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "  [A] ➕ Add New Project / Folder      [Q] ❌ Exit Launcher`n" -ForegroundColor Green
}

function Add-New-Project {
    Write-Host "`n--- ➕ Add New Project / Folder ---" -ForegroundColor Cyan
    $name = Read-Host "Project Name (e.g. Quantum Video)"
    if (-not $name) { return }

    $folder = Read-Host "Folder Path (e.g. C:\Users\Irak\Desktop\Quantum_Video)"
    if (-not $folder) { return }

    $tag = Read-Host "Tag/Description (e.g. AI VIDEO WORKSPACE)"
    if (-not $tag) { $tag = "ACTIVE PROJECT" }

    Write-Host "`nSelect Color Theme:" -ForegroundColor Yellow
    Write-Host "1: DarkRed  2: DarkBlue  3: DarkGreen  4: DarkMagenta  5: DarkCyan  6: DarkYellow  7: Black" -ForegroundColor Gray
    $cChoice = Read-Host "Color Number (1-7, Default 2)"
    
    $bgColor = switch ($cChoice) {
        "1" { "DarkRed" }
        "2" { "DarkBlue" }
        "3" { "DarkGreen" }
        "4" { "DarkMagenta" }
        "5" { "DarkCyan" }
        "6" { "DarkYellow" }
        "7" { "Black" }
        default { "DarkBlue" }
    }
    $fgColor = if ($bgColor -eq "DarkYellow") { "Black" } else { "White" }

    $current = @(Load-Projects)
    $maxId = 0
    foreach ($p in $current) {
        $num = 0
        if ([int]::TryParse($p.Id, [ref]$num)) {
            if ($num -gt $maxId) { $maxId = $num }
        }
    }
    $newId = ($maxId + 1).ToString()

    $newProject = [PSCustomObject]@{
        Id = $newId
        Name = $name
        Folder = $folder
        BgColor = $bgColor
        FgColor = $fgColor
        Tag = $tag
    }

    $current += $newProject
    Save-Projects $current
    Write-Host "`n✅ প্রজেক্ট '$name' সফলভাবে যুক্ত করা হয়েছে!`n" -ForegroundColor Green
    Start-Sleep -Seconds 1
}

function Launch-Project($p) {
    if (-not (Test-Path $p.Folder)) {
        New-Item -ItemType Directory -Path $p.Folder -Force | Out-Null
    }

    $scriptBlock = @"
    `$Host.UI.RawUI.BackgroundColor = '$($p.BgColor)'
    `$Host.UI.RawUI.ForegroundColor = '$($p.FgColor)'
    Clear-Host
    [Console]::Title = '$($p.Name) [AGY Worker]'
    
    Write-Host '╔════════════════════════════════════════════════════════════════════════╗' -ForegroundColor $($p.FgColor)
    Write-Host '║  PROJECT: $($p.Name.ToUpper().PadRight(60)) ║' -ForegroundColor $($p.FgColor)
    Write-Host '║  TAG    : $($p.Tag.PadRight(60)) ║' -ForegroundColor $($p.FgColor)
    Write-Host '║  PATH   : $($p.Folder.PadRight(60)) ║' -ForegroundColor $($p.FgColor)
    Write-Host '╚════════════════════════════════════════════════════════════════════════╝' -ForegroundColor $($p.FgColor)
    Write-Host '`n⚡ Launching Antigravity CLI (agy)...`n' -ForegroundColor $($p.FgColor)
    
    Set-Location '$($p.Folder)'
    agy
    
    # Universal Mother-Folder Popup Alert on AGY completion
    powershell.exe -ExecutionPolicy Bypass -File '$notifyScript' -Message 'সেশন বা টাস্ক সফলভাবে শেষ হয়েছে!' -ProjectFolder '$($p.Folder)'
"@

    $encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($scriptBlock))
    Start-Process powershell -ArgumentList "-NoExit", "-EncodedCommand", $encoded
}

while ($true) {
    $projects = Load-Projects
    Show-Menu $projects
    $choice = Read-Host "Enter Project Number or [A] to Add, [Q] to Quit"

    if ($choice -match "^[Qq]$") {
        Write-Host "`nবিদায় ইরাক ভাইয়া! মাস্টার লঞ্চার বন্ধ করা হলো।`n" -ForegroundColor Cyan
        break
    }
    elseif ($choice -match "^[Aa]$") {
        Add-New-Project
    }
    else {
        $selected = $projects | Where-Object { $_.Id.ToString() -eq $choice.Trim() }
        if ($selected) {
            Write-Host "`nLaunching $($selected.Name) in $($selected.BgColor) background...`n" -ForegroundColor Green
            Launch-Project $selected
        } else {
            Write-Host "`n[Error] Invalid selection! Please enter a valid number from the menu.`n" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}
