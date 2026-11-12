@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\compile_offline.ps1" %*
exit /b %ERRORLEVEL%
