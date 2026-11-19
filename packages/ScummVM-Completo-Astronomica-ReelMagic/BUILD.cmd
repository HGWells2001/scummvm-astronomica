@echo off
setlocal
cd /d "%~dp0"
echo ScummVM completo: Astronomica + Return to Zork ReelMagic + tutti gli engine
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0build.ps1" %*
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" echo Compilazione fallita. Leggere il registro indicato sopra.
if "%RC%"=="0" echo Output: %~dp0BUILD_OUTPUT\ScummVM-Completo-Astronomica-ReelMagic
pause
exit /b %RC%
