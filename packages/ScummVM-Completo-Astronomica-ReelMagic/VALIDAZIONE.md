# Verifiche effettive del pacchetto

- Preparazione da una cartella vuota con i commit fissati: riuscita.
- Tutti gli stadi e le verifiche finali del progetto ReelMagic: superati.
- Installazione dei 23 file del motore Astronomica e dei tre file video/audio condivisi: hash esatti della versione qualificata.
- Seconda installazione: idempotente. Core incompatibile: rifiutato senza modificare altri file.
- Compilazione reale dello strumento create_project con Visual Studio: riuscita.
- Generazione Visual Studio: **127 engine principali su 127**, nessun engine omesso; Astronomica e MADE presenti e abilitati.
- Controllo del pacchetto e della sintassi PowerShell: superato.

**Non e stata eseguita la compilazione completa dell'eseguibile con tutti i 127 engine e tutte le dipendenze.** Questo ZIP prepara ed esegue tale compilazione sul computer dell'utente. Le dipendenze e la fase finale restano da verificare con un avvio completo di BUILD.cmd. Non e una distribuzione binaria gia collaudata.

I controlli precedenti di Astronomica e ReelMagic non costituiscono un collaudo completo dei giochi su questo nuovo insieme di motori. Non sono inclusi file commerciali dei giochi.

Aggiornamento: il motore standalone con102 effetti/cue su308 percorsi WAV supera632 casi del mixer,Windows,suite generale e vecchi ASVM29. L'integrazione aggiornata ReelMagic e la generazione di tutti127 progetti sono state nuovamente verificate. La compilazione completa dell'eseguibile combinato resta da eseguire.

Parlato e musica:passano sul motore standalone la matrice5brani,volume normale170/171,pausa,due voci,file mancante,stop,cambio scena,introduzioneP503,voce gia terminata durante l'avvio musica,salvataggi e suite generale. Le due cache di volume sono transitorie e non cambiano il formato dei salvataggi. Il nuovo header richiede ricompilare tutti i file del motore. La build combinata127engine resta da compilare sul computer dell'utente.
