# Avvio locale corrente, 19 ottobre 2026

Aprire `Avvia-Astronomica.cmd` nella radice del workspace. Usa direttamente
`work/fresh-20260913/build/Releasex64/scummvm.exe`, la build del motore reale.
Servono i file originali in `D:/astro`. Il vecchio collegamento sotto `bin/`
rimanda allo stesso avvio corrente.

La prima apertura crea `userdata/astronomica/astronomica.ini` dal modello
`astronomica-play.ini`. Le aperture successive conservano le preferenze.
I salvataggi personali vanno in `userdata/astronomica/saves`, il registro in
`userdata/astronomica/astronomica.log`; sono separati dagli slot delle prove.

Il modello attiva audio, animazioni, interazione con gli sprite e programmi
originali di ingresso. Parte da P1, il menu iniziale, senza forzare un puzzle
o attivare prove automatiche. Non mostra la barra diagnostica. Il tema
incorporato e l'interfaccia inglese corrispondono alle risorse della build.

Il supporto resta in sviluppo. Le verifiche automatiche non sostituiscono
una partita audiovisiva integrale. Questo collegamento richiede la build
locale e non e un nuovo pacchetto del gioco. Non pubblicare `userdata/`,
eseguibili o file originali del gioco nel repository dei sorgenti.
