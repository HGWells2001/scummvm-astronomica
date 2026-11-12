# Astronomica ASVM31 su Windows 11: avvio portatile

Questa procedura riguarda **il motore ScummVM personalizzato ASVM31**, non il vecchio eseguibile originale a 16 bit. I dati originali restano necessari e non vengono distribuiti.

## Avvio

1. Scarica il pacchetto **Astronomica-ASVM31-Windows-x64** dagli artifact del workflow GitHub Actions relativo a questa revisione, dopo che la compilazione risulta riuscita. Estrailo in una cartella dove puoi scrivere.
2. Copia **i tuoi dati originali** nella sottocartella game_data del pacchetto, mantenendo la struttura originale. Il file game_data\PLACES\GAMEDATA deve esistere. La variante del CD verificata dal detector corrente include ASTRO.EXE (418.376 byte), oltre a GAMEDATA (1.604 byte). Altre varianti non sono garantite.
3. Fai doppio clic su GIOCA.cmd. Per controllare il percorso e il motore senza eseguire il gioco: GIOCA.cmd -CheckOnly.

Se possiedi già il gioco in D:\astro, non serve copiarlo: il launcher lo trova automaticamente dopo aver controllato game_data. Per usare un percorso diverso, dalla finestra del prompt:

    set "ASTRO_GAME_PATH=E:\Giochi\Astronomica"
    GIOCA.cmd

Per usare una compilazione personale già pronta:

    set "ASTRO_SCUMMVM=C:\Percorso\scummvm.exe"
    GIOCA.cmd

I percorsi relativi impostati tramite queste variabili sono interpretati dalla cartella del launcher. I percorsi con spazi sono supportati. Una variabile esplicita non valida produce un errore chiaro, senza passare silenziosamente ad altri file.

## Dati e preferenze

- I salvataggi personali sono in userdata\astronomica\saves.
- La configurazione è in userdata\astronomica\astronomica.ini. Il launcher la crea solo se non esiste, così preserva le preferenze ai successivi avvii.
- Il registro è userdata\astronomica\astronomica.log.
- --path sceglie la cartella originale a ogni avvio anche se quella salvata nel file INI è precedente.
- F5 apre il menu ScummVM; Spazio mette in pausa durante le scene supportate. Il salvataggio può essere temporaneamente disabilitato durante script/filmati, secondo le restrizioni effettive del motore.

## Come interpretare i risultati

GIOCA.cmd -CheckOnly verifica solo che esistano l'eseguibile con il motore Astronomica e la struttura minima della cartella dati. **Non prova** la leggibilità integrale dei file, la risoluzione degli enigmi o il completamento della storia.

Il build automatico verifica che il codice sia compilabile e che il motore sia registrato. Non si possono eseguire prove complete di gioco nel CI senza i dati originali. Astronomica resta sperimentale finché una partita continua, con mouse, audio, salvataggi e sequenze finali, non viene verificata manualmente. Il repository non contiene gli asset commerciali del gioco.
