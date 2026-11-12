# Kit di compilazione completamente offline: Astronomica ASVM31 (Windows x64)

Il workflow GitHub Actions **Astronomica ASVM31 offline compilation kit** assembla un pacchetto portatile con sorgenti e compilatore MSYS2/MinGW. Il workflow scarica e predispone le dipendenze **prima** della creazione del pacchetto. Dopo l'estrazione, COMPILA.cmd non esegue git, pacman o download: ricompila il motore ScummVM personalizzato usando soltanto ciò che è incluso.

## Contenuto

- msys64/: ambiente MSYS2 MINGW64 di GCC, make, Python, librerie SDL2/zlib/png, cmp e rispettivi componenti già installati.
- scummvm/: ScummVM esattamente alla revisione richiesta da SCUMMVM_BASE.json, con **23 file del motore ASVM31** e **3 componenti video patchati**. La copia GCC riceve solo una qualificazione dei nomi QuickTime che evita ambiguità MinGW.
- tools/: script di compilazione e raccolta delle DLL di runtime.
- COMPILA.cmd: compila da zero senza rete; COMPILA.cmd -CheckOnly verifica i prerequisiti.
- GIOCA.cmd: avvio con cartella originale game_data, D:\astro o ASTRO_GAME_PATH.
- ORIGINE-BUILD.txt: identificazione del progetto, commit e versioni pacchetti MSYS2.

## Utilizzo in Windows 11

1. Da GitHub Actions scarica l'artifact **Astronomica-ASVM31-Offline-Kit** e decomprimi lo ZIP. Al suo interno trovi Astronomica-ASVM31-Offline-Kit.7z. Estrai anche il file 7z con 7-Zip (o un estrattore Windows compatibile).
2. **Estrai in un percorso breve senza spazi**, per esempio C:\AstronomicaOffline. La radice estratta deve contenere contemporaneamente msys64, scummvm, tools e COMPILA.cmd.
3. Scollega Internet, fai doppio clic su COMPILA.cmd. L'eseguibile compilato e le DLL raccolte saranno in bin.
4. Copia i **tuoi dati originali** in game_data, conservando il file game_data\PLACES\GAMEDATA, oppure usa D:\astro. Dal prompt nella cartella del kit, dopo la compilazione esegui:

    set "ASTRO_SCUMMVM=bin\scummvm.exe"
    GIOCA.cmd

Per la verifica senza compilazione e per scegliere il parallelismo:

    COMPILA.cmd -CheckOnly
    COMPILA.cmd -Jobs 2

L'ambiente di compilazione contiene tutto ciò che serve e non richiede Git, Python o Visual Studio installati nel sistema. È destinato a Windows x64, non Linux/macOS/ARM.

## Limiti

- Il pacchetto è molto più grande di un semplice archivio sorgenti. I componenti open source mantengono le rispettive licenze nelle directory MSYS2; ORIGINE-BUILD.txt conserva versioni di pacchetto.
- La compilazione non implica il completamento del gioco: una partita integrale naturale deve ancora essere verificata.
- Il kit **non contiene dati commerciali del gioco**, filmati, suoni, bitmap originali o salvataggi privati.
- Durante l'uso offline non eseguire aggiornamenti pacman; l'ambiente è già pronto. Non modificare la revisione ScummVM dopo la preparazione.
