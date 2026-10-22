@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0scummvm.exe" (
 echo Eseguibile ScummVM non trovato nella cartella del programma.
 exit /b 1
)
if not exist "%~dp0game_data\PLACES\GAMEDATA" (
 echo Dati originali non trovati in game_data. Esegui prima tools\game_archive.py.
 exit /b 1
)
where py >nul 2>nul
if errorlevel 1 (
 echo Python 3 non trovato. Installa Python 3, poi ripeti.
 exit /b 1
)
py -3 "%~dp0tools\verify_gameplay.py" --exe "%~dp0scummvm.exe" --game-dir "%~dp0game_data" --suite core %*
set "VERIFY_EXIT=%ERRORLEVEL%"
echo.
if "%VERIFY_EXIT%"=="0" (
 echo Controlli automatici riusciti. Una partita completa resta da verificare manualmente.
) else (
 echo Controlli incompleti. Apri la cartella astronomica-diagnostics-* e il file summary.json.
)
exit /b %VERIFY_EXIT%
