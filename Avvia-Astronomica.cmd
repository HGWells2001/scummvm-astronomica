@echo off
setlocal
title Astronomica - avvio del progetto
set "ASTRO_ROOT=%~dp0"
set "ASTRO_EXE=%ASTRO_ROOT%work\fresh-20260913\build\Releasex64\scummvm.exe"
set "ASTRO_USER=%ASTRO_ROOT%userdata\astronomica"
set "ASTRO_RESULT=1"
echo Avvio di Astronomica dalla compilazione del progetto.
if not exist "%ASTRO_EXE%" (
  echo Eseguibile corrente non trovato: "%ASTRO_EXE%"
  goto :errore
)
if not exist "D:\astro\" (
  echo Cartella dei file originali non trovata: D:\astro
  goto :errore
)
if not exist "%ASTRO_USER%\saves\" mkdir "%ASTRO_USER%\saves" 2>nul
if not exist "%ASTRO_USER%\saves\" (
  echo Impossibile accedere alla cartella dei salvataggi: "%ASTRO_USER%\saves"
  goto :errore
)
if not exist "%ASTRO_USER%\astronomica.ini" copy /y "%ASTRO_ROOT%outputs\astronomica-cleanroom\astronomica-play.ini" "%ASTRO_USER%\astronomica.ini" >nul 2>&1
if not exist "%ASTRO_USER%\astronomica.ini" (
  echo Impossibile creare la configurazione: "%ASTRO_USER%\astronomica.ini"
  goto :errore
)
pushd "%ASTRO_ROOT%"
if errorlevel 1 goto :errore
>"%ASTRO_USER%\avvio-console.log" echo Avvio: %date% %time%
>>"%ASTRO_USER%\avvio-console.log" echo Eseguibile: "%ASTRO_EXE%"
echo Eseguibile: "%ASTRO_EXE%"
start "" /wait "%ASTRO_EXE%" --config="%ASTRO_USER%\astronomica.ini" --savepath="%ASTRO_USER%\saves" --logfile="%ASTRO_USER%\astronomica.log" --extrapath="%ASTRO_ROOT%work\fresh-20260913\fonts" astronomica >>"%ASTRO_USER%\avvio-console.log" 2>&1
set "ASTRO_RESULT=%ERRORLEVEL%"
popd
>>"%ASTRO_USER%\avvio-console.log" echo Codice di uscita: %ASTRO_RESULT%
if "%ASTRO_RESULT%"=="0" exit /b 0
echo.
echo ScummVM si e' chiuso con codice %ASTRO_RESULT%.
type "%ASTRO_USER%\avvio-console.log"
:errore
echo.
echo L'avvio non e' riuscito. Questa finestra resta aperta per leggere l'errore.
echo Registro di avvio: "%ASTRO_USER%\avvio-console.log"
pause
exit /b %ASTRO_RESULT%
