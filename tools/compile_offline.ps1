# SPDX-License-Identifier: GPL-3.0-or-later
# Fully offline Windows build after unpacking the MSYS2 + pinned ScummVM bundle.
param(
    [switch]$CheckOnly,
    [ValidateRange(1, 32)][int]$Jobs = 2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
try {
    $root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
    if ($root -match "[^\x20-\x7E]" -or $root.Contains(" ")) {
        throw "Estrai il pacchetto in un percorso ASCII senza spazi, per esempio C:\AstronomicaOffline"
    }
    $bash = Join-Path $root "msys64\usr\bin\bash.exe"
    $sh = Join-Path $root "tools\build_offline.sh"
    $engine = Join-Path $root "scummvm\engines\astronomica\astronomica.cpp"
    if (-not (Test-Path -LiteralPath $bash -PathType Leaf)) { throw "Ambiente MSYS2 offline assente: $bash" }
    if (-not (Test-Path -LiteralPath $sh -PathType Leaf)) { throw "Script di compilazione assente: $sh" }
    if (-not (Test-Path -LiteralPath $engine -PathType Leaf)) { throw "Sorgenti del motore assenti: $engine" }

    $env:MSYSTEM = "MINGW64"
    $env:CHERE_INVOKING = "1"
    $env:MSYS2_PATH_TYPE = "strict"
    $env:ASTRO_OFFLINE_ROOT = $root
    $env:ASTRO_OFFLINE_JOBS = "$Jobs"
    $env:ASTRO_OFFLINE_CHECK = if ($CheckOnly) { "1" } else { "0" }

    # Use bundled bash (not an external Git Bash). No pacman or network calls.
    & $bash --login -c 'bash "$(cygpath -u "$ASTRO_OFFLINE_ROOT")/tools/build_offline.sh"'
    if ($LASTEXITCODE -ne 0) { throw "Compilazione offline fallita (codice $LASTEXITCODE)" }
    if (-not $CheckOnly) {
        Write-Host "Compilazione terminata: $(Join-Path $root 'bin\scummvm.exe')"
        Write-Host "Per giocare, usa GIOCA.cmd con i dati originali in game_data o D:\astro."
    }
    exit 0
} catch {
    [Console]::Error.WriteLine("ERRORE: " + $_.Exception.Message)
    exit 1
}
