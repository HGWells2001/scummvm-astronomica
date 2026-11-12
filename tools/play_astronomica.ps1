# SPDX-License-Identifier: GPL-3.0-or-later
# Portable launcher for the custom Astronomica ScummVM engine.
# -CheckOnly verifies the launcher prerequisites without starting the game.
param([switch]$CheckOnly)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Full-From-Root([string]$Candidate, [string]$Root) {
    if ([IO.Path]::IsPathRooted($Candidate)) {
        return [IO.Path]::GetFullPath($Candidate)
    }
    return [IO.Path]::GetFullPath((Join-Path $Root $Candidate))
}

try {
    $root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))

    if (-not [string]::IsNullOrWhiteSpace($env:ASTRO_SCUMMVM)) {
        $exe = Full-From-Root $env:ASTRO_SCUMMVM $root
        if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
            throw "ASTRO_SCUMMVM indica un eseguibile inesistente: $exe"
        }
    } else {
        $exe = $null
        foreach ($candidate in @('scummvm.exe', 'work\fresh-20260913\build\Releasex64\scummvm.exe')) {
            $path = Full-From-Root $candidate $root
            if (Test-Path -LiteralPath $path -PathType Leaf) {
                $exe = $path
                break
            }
        }
        if (-not $exe) {
            throw 'Non trovo scummvm.exe. Usa il pacchetto Windows ASVM31 o imposta ASTRO_SCUMMVM.'
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($env:ASTRO_GAME_PATH)) {
        $gameDir = Full-From-Root $env:ASTRO_GAME_PATH $root
        if (-not (Test-Path -LiteralPath (Join-Path $gameDir 'PLACES\GAMEDATA') -PathType Leaf)) {
            throw "ASTRO_GAME_PATH non contiene PLACES\GAMEDATA: $gameDir"
        }
    } else {
        $gameDir = $null
        foreach ($candidate in @('game_data', 'D:\astro')) {
            $path = Full-From-Root $candidate $root
            if (Test-Path -LiteralPath (Join-Path $path 'PLACES\GAMEDATA') -PathType Leaf) {
                $gameDir = $path
                break
            }
        }
        if (-not $gameDir) {
            throw 'File originali mancanti. Copia il gioco in game_data\ (con PLACES\GAMEDATA) oppure imposta ASTRO_GAME_PATH.'
        }
    }

    # A stock ScummVM executable cannot launch the custom Astronomica engine.
    $engineList = & $exe '--list-engines'
    if ($LASTEXITCODE -ne 0 -or (($engineList | Out-String) -notmatch '(?im)^\s*astronomica(?:\s|$)')) {
        throw "L'eseguibile non registra il motore Astronomica: $exe"
    }

    Write-Host "ScummVM Astronomica: $exe"
    Write-Host "Dati originali: $gameDir"
    if ($CheckOnly) {
        Write-Host 'Controlli preliminari PASS (nessun gioco eseguito).'
        exit 0
    }

    $userDir = Join-Path $root 'userdata\astronomica'
    $saveDir = Join-Path $userDir 'saves'
    [IO.Directory]::CreateDirectory($saveDir) | Out-Null
    $config = Join-Path $userDir 'astronomica.ini'
    if (-not (Test-Path -LiteralPath $config -PathType Leaf)) {
        # BOM-free UTF-8: compatible with ScummVM's INI parser.
        $gamePathIni = $gameDir.Replace('\', '/')
        $lines = @(
            '[scummvm]'
            'gui_theme=builtin'
            'gui_language=en'
            'lastselectedgame=astronomica'
            'enable_unsupported_game_warning=false'
            ''
            '[astronomica]'
            'gameid=astronomica'
            'engineid=astronomica'
            'description=Astronomica: The Quest for the Edge of the Universe'
            "path=$gamePathIni"
            'astronomica_audio=true'
            'astronomica_animation=true'
            'astronomica_sprite_input=true'
            'astronomica_entry_scripts=true'
            'astronomica_debug_overlay=false'
        )
        [IO.File]::WriteAllText($config, (($lines -join [Environment]::NewLine) + [Environment]::NewLine), (New-Object Text.UTF8Encoding($false)))
    }

    $saveLog = Join-Path $userDir 'astronomica.log'
    # --path overrides the saved path without touching the user's preferences.
    $parameters = @("--config=$config", "--savepath=$saveDir", "--logfile=$saveLog", "--path=$gameDir")
    $fontPath = Join-Path $root 'work\fresh-20260913\fonts'
    if (Test-Path -LiteralPath $fontPath -PathType Container) {
        $parameters += "--extrapath=$fontPath"
    }
    $parameters += 'astronomica'
    Write-Host "Salvataggi: $saveDir"
    & $exe @parameters
    exit [int]$LASTEXITCODE
} catch {
    [Console]::Error.WriteLine('ERRORE Astronomica: ' + $_.Exception.Message)
    exit 1
}
