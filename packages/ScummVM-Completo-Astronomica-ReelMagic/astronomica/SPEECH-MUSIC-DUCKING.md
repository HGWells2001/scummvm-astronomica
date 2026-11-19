# Parlato sopra la musica con volume ridotto

La musica di sottofondo continua dallo stesso punto durante le voci. Il suo volume di canale viene dimezzato,poi torna esattamente al livello precedente. Le impostazioni globali di volume e mute non vengono modificate. Gli effetti continuano a suonare sopra la musica al volume normale.

Il ripristino copre fine naturale della voce,interruzione con un effetto,stop esplicito e cambio scena. Le voci consecutive non dimezzano il volume piu volte. Anche l'introduzione reale P503 e verificata con musica in avanzamento. I cicli di attesa conservano il proprio riferimento alla voce,cosi un clip breve finito durante il caricamento della musica non lascia il gioco in attesa del brano in loop.

Le pause congelano entrambi i flussi. Due nuovi campi privati del motore conservano solo lo stato temporaneo del volume:non entrano nei salvataggi. Il salvataggio/caricamento pubblico attende che finisca il parlato o l'effetto sovrapposto;il formato dei file resta invariato.58 metodi di serializzazione sono identici;in altri due cambia solo il controllo d'ammissione.

Controlli:cinque brani,volume normale personalizzato170/171,pausa,due voci consecutive,file mancante,sostituzione con effetto,stop,cambi di regione,introduzione reale,fine naturale,salvataggio/ripristino e due casi di voce gia terminata. Passano anche632WAV,Windows,vecchiASVM29,indicatore212casi,navigazione306scene/760percorsi e suite generale. Non e un ascolto manuale completo. I filmati mantengono la loro gestione temporale.

Sono stati ricompilati tutti i sette file C++ del motore con il nuovo header;403oggetti del framework verificati riutilizzati. I tre file video del core e il catalogo102effetti non cambiano. Questa revisione sostituisce la precedente preferenza di voce esclusiva,su richiesta dell'utente. Percentuale complessiva del progetto non misurata;accettazione fissa7/10 non e una percentuale globale.
