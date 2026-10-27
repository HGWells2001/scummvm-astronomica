# SPDX-License-Identifier: GPL-3.0-or-later
<#
Install the original 1994 English Astronomica CD data on Windows 11 for the
custom native ScummVM engine. Original game data is never modified.
Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-Astronomica.ps1 -IsoPath "C:\Games\Astronomica.iso"
Optional:
  -ScummVMExe "C:\Build\scummvm.exe"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $IsoPath,
    [string] $ScummVMExe = "",
    [string] $InstallRoot = (Join-Path $env:LOCALAPPDATA "Astronomica-Win11")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-DetectionMd5 {
    param([string] $FilePath)
    $stream = [System.IO.File]::OpenRead($FilePath)
    try {
        $count = [int][Math]::Min([long]5000, $stream.Length)
        $buffer = New-Object byte[] $count
        $readTotal = 0
        while ($readTotal -lt $count) {
            $n = $stream.Read($buffer, $readTotal, $count - $readTotal)
            if ($n -eq 0) { break }
            $readTotal += $n
        }
        $md5 = [System.Security.Cryptography.MD5]::Create()
        try {
            return [BitConverter]::ToString($md5.ComputeHash($buffer, 0, $readTotal)).Replace("-", "").ToLowerInvariant()
        }
        finally { $md5.Dispose() }
    }
    finally { $stream.Dispose() }
}

function Test-OriginalFile {
    param([string] $Path, [long] $ExpectedLength, [string] $ExpectedMd5)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    if ((Get-Item -LiteralPath $Path).Length -ne $ExpectedLength) { return $false }
    return (Get-DetectionMd5 -FilePath $Path) -eq $ExpectedMd5
}

function Find-Engine {
    param([string] $RequestedExe, [string] $ProjectRoot)
    $proposals = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($RequestedExe)) { $proposals.Add($RequestedExe) }
    if (-not [string]::IsNullOrWhiteSpace($env:ASTRONOMICA_SCUMMVM_EXE)) { $proposals.Add($env:ASTRONOMICA_SCUMMVM_EXE) }
    $proposals.Add((Join-Path $ProjectRoot "work\fresh-20260913\build\Releasex64\scummvm.exe"))
    $proposals.Add((Join-Path $ProjectRoot "work\fresh-20260913\build\Release\scummvm.exe"))
    foreach ($candidate in $proposals) {
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
        $resolved = (Resolve-Path -LiteralPath $candidate).ProviderPath
        $output = (& $resolved --list-engines 2>&1 | Out-String)
        if ($LASTEXITCODE -eq 0 -and $output -match '(?im)astronomica') {
            return $resolved
        }
    }
    return ""
}

$iso = (Resolve-Path -LiteralPath $IsoPath).ProviderPath
if ([IO.Path]::GetExtension($iso) -ine ".iso") {
    throw "Select the original .iso image."
}
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).ProviderPath
$root = [IO.Path]::GetFullPath($InstallRoot)
$dataRoot = Join-Path $root "Game"
$savesRoot = Join-Path $root "Saves"

$mountedHere = $false
Write-Host "Checking CD image: $iso"
$image = Get-DiskImage -ImagePath $iso -ErrorAction Stop
if (-not $image.Attached) {
    Mount-DiskImage -ImagePath $iso -ErrorAction Stop | Out-Null
    $mountedHere = $true
}

try {
    $letter = $null
    for ($attempt = 0; $attempt -lt 15; $attempt++) {
        $vol = Get-DiskImage -ImagePath $iso | Get-Volume | Where-Object { $_.DriveLetter } | Select-Object -First 1
        if ($null -ne $vol) { $letter = [string]$vol.DriveLetter; break }
        Start-Sleep -Seconds 1
    }
    if ([string]::IsNullOrWhiteSpace($letter)) {
        throw "The ISO was mounted but no drive letter was assigned."
    }

    $isoRoot = $letter + ':\'
    Write-Host "ISO mounted at $isoRoot"
    $exes = @(Get-ChildItem -LiteralPath $isoRoot -Filter "ASTRO.EXE" -Recurse -File -Force -ErrorAction Stop)
    $gameSource = $null
    foreach ($exe in $exes) {
        $base = $exe.DirectoryName
        $data = Join-Path $base "GAMEDATA"
        if ((Test-OriginalFile -Path $exe.FullName -ExpectedLength 418376 -ExpectedMd5 "14929fa8e52d7e3bc539244413703ecb") -and
            (Test-OriginalFile -Path $data -ExpectedLength 1604 -ExpectedMd5 "84099c2580e5c71beec97ca3e52a5967")) {
            $gameSource = $base
            break
        }
    }
    if ($null -eq $gameSource) {
        $discovered = if ($exes.Count -eq 0) { "No ASTRO.EXE exists on the CD." } else {
            "Found ASTRO.EXE, but not a same-directory ASTRO.EXE / GAMEDATA pair with the supported English signatures."
        }
        $diagnosticScript = Join-Path $PSScriptRoot "Diagnose-Astronomica.ps1"
        $diagnosticReport = Join-Path $env:TEMP "Astronomica-ISO-Diagnostic.txt"
        if (Test-Path -LiteralPath $diagnosticScript -PathType Leaf) {
            try {
                & $diagnosticScript -SourceRoot $isoRoot -ReportPath $diagnosticReport
                Write-Warning "Copy the diagnostic text report from: $diagnosticReport"
            } catch {
                Write-Warning "Automatic ISO diagnosis failed: $($_.Exception.Message)"
                Write-Warning "You can run Diagnose-Astronomica.ps1 -SourceRoot $isoRoot separately."
            }
        }
        throw "$discovered The engine supports only the checked game revision; changing the installer signatures alone cannot fix the native engine. No binaries were patched."
    }

    Write-Host "Verified supported English ASTRO.EXE and GAMEDATA."
    New-Item -ItemType Directory -Force -Path $dataRoot, $savesRoot | Out-Null
    Write-Host "Copying unchanged game data to $dataRoot"
    & robocopy.exe $gameSource $dataRoot /E /COPY:DAT /DCOPY:DAT /R:2 /W:1 /NFL /NDL /NP
    if ($LASTEXITCODE -ge 8) {
        throw "Robocopy failed with exit code $LASTEXITCODE."
    }
}
finally {
    if ($mountedHere) {
        Dismount-DiskImage -ImagePath $iso -ErrorAction SilentlyContinue | Out-Null
    }
}

if (-not (Test-OriginalFile -Path (Join-Path $dataRoot "ASTRO.EXE") -ExpectedLength 418376 -ExpectedMd5 "14929fa8e52d7e3bc539244413703ecb") -or
    -not (Test-OriginalFile -Path (Join-Path $dataRoot "GAMEDATA") -ExpectedLength 1604 -ExpectedMd5 "84099c2580e5c71beec97ca3e52a5967")) {
    throw "Game files failed post-copy integrity verification."
}

$gamePathForIni = $dataRoot.Replace('\', '/')
$ini = @"
[scummvm]
gui_theme=builtin
gui_language=en
lastselectedgame=astronomica
enable_unsupported_game_warning=false

[astronomica]
gameid=astronomica
engineid=astronomica
description=Astronomica: The Quest for the Edge of the Universe
path=$gamePathForIni
astronomica_audio=true
astronomica_animation=true
astronomica_sprite_input=true
astronomica_entry_scripts=true
astronomica_debug_overlay=false
"@
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$configFile = Join-Path $root "astronomica.ini"
[IO.File]::WriteAllText($configFile, $ini, $utf8NoBom)

$engine = Find-Engine -RequestedExe $ScummVMExe -ProjectRoot $projectRoot
$fontDir = Join-Path $projectRoot "work\fresh-20260913\fonts"
$configuration = [ordered]@{
    gameDir = $dataRoot
    engineExecutable = $engine
    extraPath = $(if (Test-Path -LiteralPath $fontDir -PathType Container) { $fontDir } else { "" })
}
[IO.File]::WriteAllText((Join-Path $root "install.json"),
    ($configuration | ConvertTo-Json -Depth 3), $utf8NoBom)

$launcher = @'
$ErrorActionPreference = "Stop"
$settings = Get-Content -LiteralPath (Join-Path $PSScriptRoot "install.json") -Raw | ConvertFrom-Json
$exe = [string]$settings.engineExecutable
if ([string]::IsNullOrWhiteSpace($exe) -or -not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "Astronomica-enabled ScummVM executable missing. Re-run Install-Astronomica.ps1 with -ScummVMExe pointing to it."
}
$saveDir = Join-Path $PSScriptRoot "Saves"
New-Item -ItemType Directory -Force -Path $saveDir | Out-Null
$launchArgs = @(
    "--config=$(Join-Path $PSScriptRoot 'astronomica.ini')",
    "--savepath=$saveDir",
    "--logfile=$(Join-Path $PSScriptRoot 'astronomica.log')"
)
if ($settings.extraPath -and (Test-Path -LiteralPath $settings.extraPath)) {
    $launchArgs += "--extrapath=$($settings.extraPath)"
}
$launchArgs += "astronomica"
& $exe @launchArgs
exit $LASTEXITCODE
'@
[IO.File]::WriteAllText((Join-Path $root "Launch-Astronomica.ps1"), $launcher, $utf8NoBom)
$cmd = @'
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Launch-Astronomica.ps1"
'@
[IO.File]::WriteAllText((Join-Path $root "Launch-Astronomica.cmd"), $cmd, $utf8NoBom)

Write-Host ""
Write-Host "Original game files verified and installed: $dataRoot"
if ([string]::IsNullOrWhiteSpace($engine)) {
    Write-Warning "An Astronomica-enabled custom ScummVM executable was NOT found. Build it first, then re-run this installer with -ScummVMExe."
    exit 2
}
Write-Host "Native engine found: $engine"
$detected = (& $engine "--detect" "--path=$dataRoot" 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0 -or $detected -notmatch '(?im)astronomica') {
    Write-Warning "The game-data folder was not detected by the custom ScummVM engine. Inspect the displayed diagnostic output."
    Write-Host $detected
    exit 3
}
Write-Host "Native detection succeeded. Double-click:"
Write-Host (Join-Path $root "Launch-Astronomica.cmd")
