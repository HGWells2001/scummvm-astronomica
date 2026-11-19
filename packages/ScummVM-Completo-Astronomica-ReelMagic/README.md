# ScummVM completo: Astronomica + Return to Zork ReelMagic

Pacchetto autocompilante per Windows x64. Include i sorgenti aggiornati di Astronomica (indicatore dei puzzle e102 effetti/segnali sonori miscelati con la musica compresi) e la procedura di integrazione ReelMagic. Scarica la base ScummVM e le dipendenze ufficiali e compila **tutti gli engine disponibili nella versione fissata**, compresi quelli sperimentali.

## Avvio

1. Estrarre tutto lo ZIP, preferibilmente in un percorso breve, per esempio `D:\ScummVM-Builder`.
2. Installare **Git for Windows**, **Python 3.9 o successivo** e **Visual Studio 2022 o 2026**, con **Sviluppo di applicazioni desktop con C++** e Windows SDK.
3. Fare doppio clic su **BUILD.cmd**. Serve Internet; sono consigliati almeno 20 GB liberi. Il primo avvio puo richiedere molto tempo.
4. Al termine aprire `BUILD_OUTPUT/ScummVM-Completo-Astronomica-ReelMagic/scummvm.exe`. Usare **Aggiungi gioco** per scegliere i propri file originali.

Il pacchetto contiene i motori, non i dati commerciali di Astronomica o Return to Zork. Non contiene un eseguibile gia compilato. Non spegne il computer e non termina altri programmi.

## Cartelle e registri

I sorgenti e le dipendenze vengono preparati in `%LOCALAPPDATA%/ScummVM-Combined-Build-8fab4356b8b3`. I registri restano nella sottocartella `logs`; a compilazione riuscita viene copiata anche `BUILD.log` nell'output. Non vengono cancellati automaticamente sorgenti o output preesistenti.

Per scegliere altre cartelle, aprire PowerShell nella cartella del pacchetto:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1 -WorkRoot D:\ScummVM-Lavoro -OutputDir D:\ScummVM-Portatile
```

Se la cartella di output non e vuota, scegliere una nuova destinazione. Per una compilazione da zero scegliere anche un nuovo `WorkRoot`. Il builder verifica gli errori dei comandi e non presenta come riuscita una compilazione fallita.

La procedura usa vcpkg ufficiale e la sua integrazione MSBuild per l'utente corrente. Richiede strumenti gia installati, non installa Visual Studio automaticamente. Conserva i dati aggiuntivi degli engine, i temi, le traduzioni e le DLL necessarie nell'output portatile.

## Sorgenti e limiti

Le revisioni esatte sono elencate in `SOURCES.json`. La base comune e quella gia usata dal motore Astronomica. Le patch ReelMagic provengono dal progetto [HGWells2001/scummvm-return-to-zork-reelmagic](https://github.com/HGWells2001/scummvm-return-to-zork-reelmagic); vengono applicate anche le sue verifiche. La modifica condivisa di Astronomica viene accettata solo se i file video hanno gli hash previsti: un conflitto interrompe la preparazione.

Tutti gli engine significa quelli presenti e compilabili per Windows nella revisione fissata, non il supporto a ogni gioco esistente. Astronomica e ReelMagic rimangono supporti sperimentali. Le prove del singolo motore non equivalgono a una partita completa verificata sulla nuova build combinata. Vedere `VALIDAZIONE.md` per le verifiche effettivamente eseguite sul pacchetto.

Licenza GPL-3.0-or-later; vedere LICENSE e le intestazioni dei sorgenti. Credits: ScummVM, synacktic e i due progetti HGWells2001.

Questa revisione usa automaticamente una nuova cartella di lavoro,per conservare le compilazioni precedenti. Lo ZIP contiene solo sorgenti; gli output di vecchie compilazioni non vengono inclusi.
