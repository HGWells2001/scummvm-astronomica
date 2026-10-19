@echo off
setlocal
set "ASTRO_ROOT=%~dp0"
set "ASTRO_EXE=%ASTRO_ROOT%work\fresh-20260913\build\Releasex64\scummvm.exe"
set "ASTRO_USER=%ASTRO_ROOT%userdata\astronomica"
if not exist "%ASTRO_EXE%" (
  echo Eseguibile corrente non trovato: %ASTRO_EXE%
  exit /b 1
)
if not exist "D:\astro\" (
  echo Cartella dei file originali non trovata: D:\astro
  exit /b 1
)
if not exist "%ASTRO_USER%\saves\" mkdir "%ASTRO_USER%\saves"
if not exist "%ASTRO_USER%\saves\" exit /b 1
if not exist "%ASTRO_USER%\astronomica.ini" copy /y "%ASTRO_ROOT%outputs\astronomica-cleanroom\astronomica-play.ini" "%ASTRO_USER%\astronomica.ini" >nul
if not exist "%ASTRO_USER%\astronomica.ini" exit /b 1
pushd "%ASTRO_ROOT%"
"%ASTRO_EXE%" --config="%ASTRO_USER%\astronomica.ini" --savepath="%ASTRO_USER%\saves" --logfile="%ASTRO_USER%\astronomica.log" --extrapath="%ASTRO_ROOT%work\fresh-20260913\fonts" astronomica
set "ASTRO_RESULT=%ERRORLEVEL%"
popd
exit /b %ASTRO_RESULT%
