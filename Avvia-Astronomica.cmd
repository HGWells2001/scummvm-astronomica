@echo off
setlocal
set "ASTRO_ROOT=%~dp0"
if defined ASTRO_SCUMMVM (
 set "ASTRO_EXE=%ASTRO_SCUMMVM%"
) else if exist "%ASTRO_ROOT%scummvm.exe" (
 set "ASTRO_EXE=%ASTRO_ROOT%scummvm.exe"
) else if exist "%ASTRO_ROOT%work\fresh-20260913\scummvm\scummvm.exe" (
 set "ASTRO_EXE=%ASTRO_ROOT%work\fresh-20260913\scummvm\scummvm.exe"
) else (
 set "ASTRO_EXE=%ASTRO_ROOT%work\fresh-20260913\build\Releasex64\scummvm.exe"
)
set "ASTRO_USER=%ASTRO_ROOT%userdata\astronomica"
if not exist "%ASTRO_EXE%" (
 echo Eseguibile con motore Astronomica non trovato: "%ASTRO_EXE%"
 exit /b 1
)
if defined ASTRO_GAME_PATH (
 set "ASTRO_DATA=%ASTRO_GAME_PATH%"
) else if exist "%ASTRO_ROOT%game_data\PLACES\GAMEDATA" (
 set "ASTRO_DATA=%ASTRO_ROOT%game_data"
) else (
 set "ASTRO_DATA=D:\astro"
)
if not exist "%ASTRO_DATA%\PLACES\GAMEDATA" (
 echo Dati Astronomica mancanti: "%ASTRO_DATA%"
 echo Estrarre il proprio archivio originale in game_data oppure impostare ASTRO_GAME_PATH.
 exit /b 1
)
if not exist "%ASTRO_USER%\saves\" mkdir "%ASTRO_USER%\saves"
if not exist "%ASTRO_USER%\saves\" exit /b 1
if not exist "%ASTRO_USER%\astronomica.ini" copy /y "%ASTRO_ROOT%outputs\astronomica-cleanroom\astronomica-play.ini" "%ASTRO_USER%\astronomica.ini" >nul
if not exist "%ASTRO_USER%\astronomica.ini" exit /b 1
set "ASTRO_TRACE_ARGS="
if /i "%ASTRO_TRACE%"=="1" set "ASTRO_TRACE_ARGS=--debuglevel=1"
pushd "%ASTRO_ROOT%"
if exist "%ASTRO_ROOT%work\fresh-20260913\fonts\" (
 "%ASTRO_EXE%" %ASTRO_TRACE_ARGS% --config="%ASTRO_USER%\astronomica.ini" --savepath="%ASTRO_USER%\saves" --logfile="%ASTRO_USER%\astronomica.log" --path="%ASTRO_DATA%" --extrapath="%ASTRO_ROOT%work\fresh-20260913\fonts" astronomica
) else (
 "%ASTRO_EXE%" %ASTRO_TRACE_ARGS% --config="%ASTRO_USER%\astronomica.ini" --savepath="%ASTRO_USER%\saves" --logfile="%ASTRO_USER%\astronomica.log" --path="%ASTRO_DATA%" astronomica
)
set "ASTRO_RESULT=%ERRORLEVEL%"
popd
exit /b %ASTRO_RESULT%
