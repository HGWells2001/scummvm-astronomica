# Sprite statici: revisione 5

L'analisi usa l'eseguibile e le bitmap originali. `_SWStdDrawProc`, segmento 7 offset 055a, esegue tre chiamate alla funzione importata GDI ordinale 34. I codici raster sono 0x00660046, 0x008800c6, 0x00660046: XOR con l'immagine, AND con la maschera, XOR con l'immagine. Per una maschera binaria il risultato è il pixel sorgente dove la maschera è nera, il pixel di destinazione dove è bianca.

`_SWSetSpriteLocation` (7:0ad4) aggiorna le coordinate iniziali del rettangolo mantenendone le dimensioni. Il PLACEDEF originale di P29 conferma la posizione (318,294) dello sprite visibile del display del videoregistratore. Gli altri due sprite della scena sono inizialmente invisibili.

`sprites.cpp` implementa composizione e ritaglio ai bordi della superficie. Rifiuta maschere non binarie o dimensioni/formati incompatibili prima di modificare la destinazione. Le immagini vengono decodificate dal modulo BMP di ScummVM; per le maschere a 1 bit, non supportate da quel modulo nella build usata, è stato aggiunto un lettore dedicato. Gestisce header da 40 byte, palette a due colori, righe allineate a quattro byte e orientamento verticale, con verifica dei limiti. Vengono disegnati solo gli sprite visibili, non clonati, con un solo fotogramma e layer=1 nelle scene che dichiarano un unico livello. L'ordine è quello del file, coerente con l'accodamento osservato in `_SWAddSprite`; il confronto dinamico dell'ordine di sovrapposizione resta da completare.

La prova indipendente `verify_sprite_reference.py` legge il MEGAFILE di P29, decodifica i BMP con Pillow e compone il display sullo sfondo. Il risultato RGB sui primi 456 pixel verticali (esclusa la barra del prototipo) ha FNV-1a `ca004a3b`. La verifica nativa confronta questo valore con i pixel effettivamente prodotti da ScummVM nel backend SDL dummy RGB565 a 16 bit, quantizzando prima il riferimento allo stesso formato (hash `97802e24`). Non è un confronto con una cattura dell'eseguibile originale.

## Visibilità comandata: revisione 6

L'opcode 16 entra in 15:05b2, passa 1 e chiama `_SWSetSpriteVisible` attraverso 15:0be5; l'opcode 17 entra in 15:05b7 e passa 0 attraverso 15:0be3. Il lettore conserva l'identificatore a base 1. La sequenza originale di P29 usa entrambi con argomento 2, corrispondente al display del videoregistratore.

L'interprete valida l'intera sequenza e gli identificatori prima di accodarla. Sono ammessi solo bersagli appartenenti al sottoinsieme grafico già supportato: un livello, nessun clone, un fotogramma. Le azioni aggiornano la visibilità; il ridisegno riparte dallo sfondo conservato e ricompone gli sprite ancora visibili. Non ricarica lo stato della scena e non lascia il vecchio sprite sullo schermo.

Il test esegue una singola istruzione HIDE originale di P29, verifica che l'effetto sia differito fino al passaggio della coda e confronta il risultato con lo sfondo indipendente: hash RGB565 `f46c822e` (RGB888 `a8aa76a9`). Poi esegue SHOW e verifica il ritorno all'immagine precedente. Una sequenza con un'assegnazione seguita da un identificatore sprite non valido viene rifiutata senza modificare la variabile. In P29 il tasto V permette di ripetere la prova; non equivale all'esecuzione completa dello script temporizzato originale.

## Posizionamento comandato: revisione 7

L'opcode 7 entra in 15:03bb, passa le parti basse a 16 bit dei due argomenti a `_SWMoveSprite` (7:0a32), poi conserva gli argomenti completi a 32 bit nei campi logici dello sprite. La routine aggiorna una posizione assoluta, non uno spostamento relativo. Se entrambe le coordinate a 16 bit sono zero, lascia invariata la posizione visiva, ma il chiamante aggiorna comunque i campi logici. Il modulo mantiene perciò separate posizione logica e posizione di rendering. Sono verificati il caso (0,0) e la conversione di 65535/65537 a -1/1.

P517 contiene le istruzioni originali per lo sprite 7 nelle posizioni (447,361) e (477,361). La prova esegue tali comandi singolarmente tramite la coda, verifica l'assenza di esecuzione anticipata, ricompone lo schermo sullo sfondo conservato e confronta i pixel con `verify_move_reference.py`. Per il sottoinsieme statico supportato, con due sprite disegnati, gli hash RGB565 sono `2239ec62` prima e `c411be61` dopo lo spostamento; in RGB888 sono `402586ef` e `cb1d5ec4`. Il ritorno alla posizione iniziale deve ripristinare esattamente l'immagine precedente.

Il tasto M in P517 ripete questa prova diagnostica. I comandi riferiti a sprite fuori dal sottoinsieme grafico supportato vengono rifiutati prima dell'esecuzione della sequenza.

## Spostamento relativo: revisione 8

L'opcode 47 entra in 15:0430 e chiama `_SWOffsetSprite` (7:0a93). Somma le parti basse dei due argomenti alle coordinate del rettangolo a 16 bit, mentre il chiamante somma separatamente i valori completi ai campi logici a 32 bit (15:045e–049c). Il modulo riproduce i due riporti separati senza overflow con segno nel codice C++; i test includono incremento e decremento agli estremi.

P510 contiene `47 [8,0,1]`: lo sprite 8 parte da (427,360). La verifica esegue due volte la singola istruzione originale tramite la coda e confronta i pixel nelle posizioni y=360,361,362 con tre composizioni Pillow indipendenti. Gli hash RGB565 sono rispettivamente `5dfc8e99`, `7140f4d5`, `67f0c10d`. La stessa scena contiene un comando per lo sprite 9, che è un clone: la catena contenente entrambi viene rifiutata prima di muovere lo sprite 8, poiché i cloni non sono ancora supportati. Il tasto M ripete lo spostamento diagnostico e R ricarica la scena.

## Cloni statici: revisione 9

`_load_place` passa lo sprite sorgente identificato dal campo clone a `_CloneGameSprite` (12:012f), che richiama `_SWCloneSprite` (7:02d8). Il clone condivide i riferimenti ai fotogrammi, mentre il caricatore legge successivamente posizione, visibilità e comandi propri. Il nuovo risolutore conserva il campo clone originale e segue riferimenti a base 1 verso sprite precedenti, senza copiare lo stato mutabile della sorgente. Accetta catene finite con un solo fotogramma finale e rifiuta riferimenti in avanti, a se stessi, nulli o non validi. I cloni di sprite con più fotogrammi restano esclusi.

Questa revisione supera l'esclusione dei cloni descritta per le revisioni precedenti. P510 disegna ora tre sprite nel sottoinsieme statico, incluso il 9 che deriva dall'8. Le nuove composizioni indipendenti sono in `evidence/clones`: gli hash RGB565 dei cinque stati sono `a3902005`, `457e9af5`, `b9c36ac5`, `725673d5`, `fdea7131`. Il test esegue due incrementi sulla sorgente, quindi la coppia di istruzioni originali per sorgente e clone: il primo passaggio muove solo la sorgente, il secondo solo il clone, mantenendo entrambe le posizioni corrette.

In P510 M sposta la sorgente e C il clone; R ricarica la scena. Si tratta di istruzioni originali isolate per verifica, non dello script completo dell'enigma.

## Selezione dei fotogrammi: revisione 10

L'opcode 15 passa il secondo argomento a `_SWSetCurrentFrameIndex` (7:0891) attraverso 15:0516 e 15:0b0d. Il lettore non sottrae uno: gli indici sono a base zero. La routine seleziona il riferimento al fotogramma e aggiorna le dimensioni del rettangolo mantenendo l'origine. Il prototipo usa le dimensioni della bitmap selezionata e conserva la posizione. Rifiuta indici negativi, superiori a 32767 o esterni ai fotogrammi disponibili prima di accodare la sequenza.

I cloni risolvono la stessa raccolta di fotogrammi, conservando una selezione propria. La verifica nativa include sorgente e clone su fotogrammi diversi. Per mantenere distinta questa funzione dall'avvio delle animazioni, gli sprite con più immagini restano non disegnati fino a una selezione esplicita: il ciclo completo di inizializzazione e avanzamento non viene simulato.

P510 contiene istruzioni originali per selezionare 0 e 1 sullo sprite 10. Il test le esegue singolarmente nella sequenza 0/1/0, verifica il rinvio dell'effetto fino al passaggio della coda e confronta i pixel con `verify_frame_reference.py`. Gli hash RGB565 sono `a3902005`, `518eade8`, `a3902005`; i corrispondenti RGB888 sono `3579528c`, `f9c9f648`, `3579528c`. Gli indici 2 e -1 vengono rifiutati. In P510 F alterna le due immagini come dimostrazione diagnostica.

Restano mancanti avanzamento automatico dei fotogrammi, movimenti automatici, composizione su più livelli e hit testing. Le scene con sprite continuano a non eseguire eventi mouse.



## Clic: revisione 12

Il nuovo test originale `_SWIsPointInSprite` dimostra che le maschere non
servono per i clic: viene usato il rettangolo, con tutti i bordi inclusi,
indipendentemente dalla visibilit�. La ricerca sceglie il primo sprite
abilitato in ordine di file. Dettagli, limiti della modalit� sperimentale e
verifiche dei pulsanti P510 sono in `INTERPRETER.md`.
