# Riconoscimento della versione italiana

Il rilevatore identifica la lingua tramite la firma dei primi 5000 byte e la dimensione della scena PLACES/P1/MEGAFILE.HYP. GAMEDATA e ASTRO.EXE sono identici nelle due edizioni e non bastano a distinguere la lingua.

Inglese: MD5 dbad37cdf558f7687c98a66f38cc842d, 537831 byte.
Italiano: MD5 aa43748004160b8b2a33c3d21b1e2510, 498661 byte.

Entrambe le firme richiedono anche GAMEDATA (84099c2580e5c71beec97ca3e52a5967, 1604 byte) e ASTRO.EXE (14929fa8e52d7e3bc539244413703ecb, 418376 byte). Si usa il percorso completo della scena per evitare collisioni fra i molti MEGAFILE.HYP; i due file comuni possono trovarsi nelle sottocartelle originali oppure alla radice dell'installazione.

Prove con il rilevatore reale: D:/astroita viene aggiunto con language=it e D:/astro con language=en. Stesso risultato in due cartelle neutre, con ASTRO.EXE alla radice. I soli file comuni senza scena discriminante non vengono aggiunti come inglese. Nessun dato originale modificato. Il criterio non dipende da P503 e resta valido con la sua riparazione.

Cambia solo detection.cpp. Libreria del motore in esecuzione identica alla revisione audio qualificata; musica e parlato invariati. Non e una nuova verifica completa della giocabilita italiana. Per le partite gia aggiunte, rimuovere soltanto la voce dall'elenco e aggiungere di nuovo la cartella, oppure impostare Italiano nelle opzioni della voce esistente. I salvataggi e i file del gioco vanno conservati.
