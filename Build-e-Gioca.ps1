# Build and play the original Astronomica English CD edition under Windows 11.
# Run from PowerShell: powershell -ExecutionPolicy Bypass -File .\Build-e-Gioca.ps1 -Archivio "C:\path\ASTROeng.zip"
[CmdletBinding()]
param(
  [string]$Archivio = "",
  [switch]$SoloCompila
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$msysCandidates = @("C:\msys64", "$env:LOCALAPPDATA\Programs\MSYS2")
$msys = $null
foreach ($candidate in $msysCandidates) {
  if (Test-Path (Join-Path $candidate 'usr\bin\bash.exe')) { $msys = $candidate; break }
}
if (-not $msys) {
  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if (-not $winget) { throw 'MSYS2 non trovato. Installa MSYS2 da https://www.msys2.org/ e ripeti.' }
  Write-Host 'Installazione MSYS2 tramite winget...'
  & winget install -e --id MSYS2.MSYS2 --accept-package-agreements --accept-source-agreements --silent
  if ($LASTEXITCODE -ne 0) { throw 'Installazione MSYS2 non riuscita. Installa da https://www.msys2.org/' }
  foreach ($candidate in $msysCandidates) {
    if (Test-Path (Join-Path $candidate 'usr\bin\bash.exe')) { $msys = $candidate; break }
  }
  if (-not $msys) { throw 'MSYS2 installato in una posizione non rilevata. Controlla il percorso di installazione.' }
}

$bash = Join-Path $msys 'usr\bin\bash.exe'
$env:MSYSTEM = 'MINGW64'
$env:CHERE_INVOKING = '1'
$env:ASTRO_PROJECT_ROOT = $root
Push-Location $root
try {
  Write-Host 'Compilazione ScummVM + Astronomica da sorgenti verificati...'
  & $bash -lc 'cd "$(cygpath -u "$ASTRO_PROJECT_ROOT")" && bash tools/build_msys2.sh'
  if ($LASTEXITCODE -ne 0) { throw 'Build non riuscita. Se MSYS2 e stato appena aggiornato, chiudi le finestre MSYS2 e riesegui lo script.' }
  $exe = Join-Path $root 'work\fresh-20260913\scummvm\scummvm.exe'
  if (-not (Test-Path $exe)) { throw "Motore compilato non trovato: $exe" }
  Write-Host "Motore ScummVM pronto: $exe"
  if ($SoloCompila) { return }

  $gameDir = Join-Path $root 'game_data'
  if (-not (Test-Path (Join-Path $gameDir 'PLACES\GAMEDATA'))) {
    if (-not $Archivio) {
      $searchFolders = @($root, (Join-Path $env:USERPROFILE 'Downloads'))
      $found = @($searchFolders | ForEach-Object {
        Get-ChildItem -LiteralPath $_ -Filter 'ASTROeng*.zip' -File -ErrorAction SilentlyContinue
      } | Sort-Object LastWriteTime -Descending)
      if ($found.Count -gt 0) { $Archivio = $found[0].FullName }
    }
    if ($Archivio) {
      if (-not (Test-Path -LiteralPath $Archivio)) { throw "Archivio non trovato: $Archivio" }
      if (Test-Path $gameDir) { throw "La cartella game_data esiste ma non contiene PLACES\GAMEDATA. Non verra sovrascritta: $gameDir" }
      $env:ASTRO_ARCHIVE_PATH = (Resolve-Path -LiteralPath $Archivio).Path
      Write-Host "Estrazione e verifica ZIP: $env:ASTRO_ARCHIVE_PATH"
      & $bash -lc 'cd "$(cygpath -u "$ASTRO_PROJECT_ROOT")" && python tools/game_archive.py "$(cygpath -u "$ASTRO_ARCHIVE_PATH")" --output game_data'
      if ($LASTEXITCODE -ne 0) { throw 'Archivio non riconosciuto o estrazione non riuscita.' }
    } elseif (-not (Test-Path 'D:\astro\PLACES\GAMEDATA')) {
      throw 'Dati gioco mancanti. Usa -Archivio "C:\percorso\ASTROeng.zip" oppure copia i file in game_data.'
    }
  }
  if (Test-Path (Join-Path $gameDir 'PLACES\GAMEDATA')) { $env:ASTRO_GAME_PATH = $gameDir }
  $env:ASTRO_SCUMMVM = $exe
  $env:PATH = "$(Join-Path $msys 'mingw64\bin');$env:PATH"
  Write-Host 'Avvio Astronomica...'
  & (Join-Path $root 'Avvia-Astronomica.cmd')
  if ($LASTEXITCODE -ne 0) { throw "Il motore Astronomica ha restituito codice $LASTEXITCODE. Controlla userdata\astronomica\astronomica.log" }
} finally {
  Pop-Location
}
