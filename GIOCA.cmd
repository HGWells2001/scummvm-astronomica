@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\play_astronomica.ps1" %*
exit /b %ERRORLEVEL%
