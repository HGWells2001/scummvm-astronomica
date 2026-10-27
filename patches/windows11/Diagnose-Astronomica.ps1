# SPDX-License-Identifier: GPL-3.0-or-later
<#
Read-only diagnosis of an Astronomica CD or installed game data.
Usage: powershell -NoProfile -ExecutionPolicy Bypass -File .\Diagnose-Astronomica.ps1 -SourceRoot "E:\"
Does not change any original game files.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $SourceRoot,
    [string] $ReportPath = (Join-Path $env:TEMP "Astronomica-ISO-Diagnostic.txt")
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-DetectorMd5 {
    param([Parameter(Mandatory = $true)][string] $FilePath)
    $stream = [System.IO.File]::OpenRead($FilePath)
    try {
        $bytesToRead = [int][Math]::Min([long]5000, $stream.Length)
        $buffer = New-Object byte[] $bytesToRead
        $done = 0
        while ($done -lt $bytesToRead) {
            $read = $stream.Read($buffer, $done, $bytesToRead - $done)
            if ($read -eq 0) { break }
            $done += $read
        }
        $md5 = [System.Security.Cryptography.MD5]::Create()
        try {
            return [BitConverter]::ToString($md5.ComputeHash($buffer, 0, $done)).Replace("-", "").ToLowerInvariant()
        } finally { $md5.Dispose() }
    } finally { $stream.Dispose() }
}


function Get-Fnv1a32 {
    param([Parameter(Mandatory = $true)][string] $FilePath)
    $stream = [IO.File]::OpenRead($FilePath)
    try {
        [long]$hash = 2166136261
        $buffer = New-Object byte[] 65536
        while (($n = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {
            for ($i = 0; $i -lt $n; $i++) {
                $hash = ((($hash -bxor [long]$buffer[$i]) * [long]16777619) % [long]4294967296)
            }
        }
        return [uint32]$hash
    }
    finally { $stream.Dispose() }
}

$root = (Resolve-Path -LiteralPath $SourceRoot).ProviderPath
if (-not (Test-Path -LiteralPath $root -PathType Container)) {
    throw "SourceRoot must be a mounted CD or a directory."
}
$expected = @{
    "ASTRO.EXE" = @{ Length = 418376L; MD5 = "14929fa8e52d7e3bc539244413703ecb" }
    "GAMEDATA" = @{ Length = 1604L; MD5 = "84099c2580e5c71beec97ca3e52a5967" }
}
$items = @(Get-ChildItem -LiteralPath $root -Recurse -Force -ErrorAction Stop)
$files = @($items | Where-Object { -not $_.PSIsContainer })
$dirs = @($items | Where-Object { $_.PSIsContainer })
$lines = New-Object 'System.Collections.Generic.List[string]'
$lines.Add("Astronomica CD / game directory diagnostic (read-only)")
$lines.Add("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')")
$lines.Add("Source: $root")
$lines.Add("Total files: $($files.Count); total folders: $($dirs.Count)")
$lines.Add("Expected ASTRO.EXE 418376 / 14929fa8e52d7e3bc539244413703ecb")
$lines.Add("Expected GAMEDATA 1604 / 84099c2580e5c71beec97ca3e52a5967")
$lines.Add("")
$lines.Add("TOP-LEVEL CONTENTS")
foreach ($item in @(Get-ChildItem -LiteralPath $root -Force | Sort-Object Name | Select-Object -First 100)) {
    $kind = if ($item.PSIsContainer) { "<DIR>" } else { [string]$item.Length }
    $lines.Add("$kind  $($item.Name)")
}
$lines.Add("")
$lines.Add("DETECTION CANDIDATES (MD5 of first 5000 bytes)")
$matchedExe = @()
$matchedData = @()
$candidates = @($items | Where-Object { $_.Name -ieq "ASTRO.EXE" -or $_.Name -ieq "GAMEDATA" } | Sort-Object FullName)
if ($candidates.Count -eq 0) {
    $lines.Add("None: data may require installing or unpacking.")
} else {
    foreach ($item in $candidates) {
        $relative = $item.FullName.Substring($root.TrimEnd('\').Length).TrimStart('\')
        if ($item.PSIsContainer) {
            $lines.Add("<DIR>  $relative [directory, not detector file]")
            continue
        }
        try {
            $hash = Get-DetectorMd5 -FilePath $item.FullName
            $known = $expected[$item.Name.ToUpperInvariant()]
            $status = if ($item.Length -eq $known.Length -and $hash -eq $known.MD5) { "SUPPORTED_SIGNATURE" } else { "DIFFERENT_SIGNATURE" }
            if ($status -eq "SUPPORTED_SIGNATURE") {
                if ($item.Name -ieq "ASTRO.EXE") { $matchedExe += $item.FullName }
                if ($item.Name -ieq "GAMEDATA") { $matchedData += $item.FullName }
            }
            $lines.Add("$status  $relative  bytes=$($item.Length)  md5first5000=$hash")
        } catch {
            $lines.Add("READ_ERROR  $relative  $($_.Exception.Message)")
        }
    }
}
$lines.Add("")
$lines.Add("ARCHIVE / SETUP CANDIDATES (first 150)")
$archives = @($files | Where-Object {
    $_.Name -match '(?i)(\.(cab|zip|arj|lha|lzh|rar|7z|ex_|dl_|in_|z)$|^setup(\.|$)|^install(\.|$)|^data[0-9.]|^disk[0-9.])'
} | Sort-Object FullName | Select-Object -First 150)
if ($archives.Count -eq 0) { $lines.Add("No common installer/archive filenames found.") }
foreach ($item in $archives) {
    $relative = $item.FullName.Substring($root.TrimEnd('\').Length).TrimStart('\')
    $lines.Add("$relative  bytes=$($item.Length)")
}

$lines.Add("")
$lines.Add("CD ROOT PLACES LAYOUT (FNV-1a 32-bit is full-file)")
$placesDirs = @($dirs | Where-Object { $_.Name -ieq "PLACES" } | Sort-Object FullName)
if ($placesDirs.Count -eq 0) { $lines.Add("No PLACES directory found.") }
foreach ($places in $placesDirs) {
    $game = $places.Parent.FullName
    $lines.Add("PLACES folder: $($places.FullName)")
    $startScene = Join-Path $game "PLACES\P1\MEGAFILE.HYP"
    $lines.Add("Startup scene P1: $(if (Test-Path -LiteralPath $startScene -PathType Leaf) { 'PRESENT' } else { 'MISSING' })")
    foreach ($record in @(
        @("PLACES\P502\MEGAFILE.HYP", [long]669631, [uint32]2443827672),
        @("PLACES\P503\MEGAFILE.HYP", [long]782595, [uint32]231093171),
        @("PLACES\P527\MEGAFILE.HYP", [long]348102, [uint32]3684137004)
    )) {
        $candidate = Join-Path $game ([string]$record[0])
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            try {
                $size = (Get-Item -LiteralPath $candidate).Length
                $fnv = Get-Fnv1a32 -FilePath $candidate
                $ok = $size -eq [long]$record[1] -and $fnv -eq [uint32]$record[2]
                $label = if ($ok) { "MATCH" } else { "DIFFERENT" }
                $lines.Add("$label $candidate size=$size fnv32=$fnv expected_size=$($record[1]) expected_fnv32=$($record[2])")
            } catch {
                $lines.Add("READ_ERROR $candidate $($_.Exception.Message)")
            }
        } else {
            $lines.Add("MISSING $candidate")
        }
    }
}

$lines.Add("")
$lines.Add("SUPPORTED SAME-DIRECTORY FILE PAIRS")
$pairs = 0
foreach ($exe in $matchedExe) {
    foreach ($data in $matchedData) {
        if ([IO.Path]::GetDirectoryName($exe) -ieq [IO.Path]::GetDirectoryName($data)) {
            $lines.Add("Pair: $([IO.Path]::GetDirectoryName($exe))")
            $pairs++
        }
    }
}
if ($pairs -eq 0) {
    $lines.Add("None. May be an uninstalled CD, split folders or unsupported revision.")
}
$lines.Add("")
$lines.Add("Do not bypass signatures. Other revisions require engine validation.")
$dest = [IO.Path]::GetFullPath($ReportPath)
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($dest)) | Out-Null
[IO.File]::WriteAllLines($dest, $lines.ToArray(), (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Astronomica diagnostic saved: $dest"
Write-Host "Found $($candidates.Count) detector candidates; $pairs supported pair(s); $($archives.Count) archive/setup candidates."
if ($pairs -eq 0) { Write-Warning "The custom engine cannot yet identify these files. Check the report." }
