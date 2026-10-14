> Correzione revisione 29: le vecchie associazioni dirette fra argomenti
> serializzati audio e nomi dei file nelle sezioni storiche 14-28 sono
> superate dalla conversione descritta sotto. Non esiste piu l'eccezione
> per il presunto S9.WAV mancante di P508.

# Interprete: seconda fase della nuova analisi

Queste conclusioni derivano dall'ASTRO.EXE originale già identificato con SHA-256, non da implementazioni precedenti. Le disassemblature con risoluzione delle chiamate sono in `evidence/interpreter`.

## Evidenze

| Routine originale | Indirizzo segmento:offset | Risultato osservato |
|---|---|---|
| `_do_command` | 15:0025 | Esegue il comando corrente e segue il puntatore restituito finché l'esecutore restituisce 1. |
| `_execute_command` | 15:0060 | Opcode 1/2 senza effetti; 5 imposta la nuova scena; 6 richiede uscita; 51 usa la scena precedente. |
| `_pend_command` | 15:199a | Copia il comando e lo accoda alla coda FIFO. |
| `_handle_pending` | 15:1b2b | Visita solo il numero di elementi presenti all'ingresso; esegue delay=0 o tempo trascorso sufficiente. |
| `_do_mouse` | 9:114c | Gli sprite hanno precedenza sulle aree rettangolari. I comandi di clic delle aree sono accodati. |
| `_fxm_PtInRect` | 9:3d8a | Inoltra coordinate e rettangolo alla funzione importata USER, ordinale 76. |

Il comando successivo con delay=-1 viene eseguito immediatamente; delay=0 comporta un passaggio in coda. Dalla revisione 11 il timer usa millisecondi e ammette continuazioni temporizzate negli script di ingresso riconosciuti. I clic conservano il sottoinsieme senza ritardi positivi. Dalla revisione 4 accetta -1 e 0 anche all'ingresso degli eventi: entrambi attendono un passaggio della coda quando sono il primo comando.

## Parte implementata

`script.cpp` implementa la coda, le continuazioni immediate e le azioni 5, 6, 51. Accetta 1 e 2 come operazioni senza effetti. Dalla revisione 3 implementa anche 31 (confronto), 32 (assegnazione), 46 (addizione), 42 e 45 (diramazioni). La revisione 6 aggiunge 16 e 17 per la visibilità degli sprite supportati (vedere `SPRITES.md`). Valida l'intera sequenza prima di avviarla; le azioni che cambiano scena o escono avevano inizialmente il vincolo di essere l�ultimo comando; la revisione 15 estende il caso 5 come descritto sotto. Questo è un sottoinsieme intenzionale, non l'interprete completo.

I clic sono abilitati soltanto nelle scene prive di sprite, poiché la precedenza e le maschere degli sprite non sono implementate. Sono considerate tutte le aree corrispondenti, nell'ordine del file. Il prototipo usa rettangoli con bordo destro e inferiore esclusi. Un cambio scena riuscito cancella le continuazioni della scena precedente. Questa politica dell'esploratore non costituisce ancora una ricostruzione completa del ciclo di caricamento originale.

P103 fornisce un caso verificabile anche nel PLACEDEF originale: rettangolo (311,61)-(552,155), `new_place(126,0)`. Il test C++ carica il MEGAFILE originale, verifica due clic esterni, accoda il clic interno, controlla che il cambio non avvenga prima del passaggio in coda e verifica il caricamento di P126.

Altri test nativi verificano: delay=0 su più cicli; delay=-1 immediato; scadenza prima/al limite; rollover del contatore; rifiuto di sequenze non supportate senza effetti parziali; annullamento della coda; ordine FIFO rispetto alle nuove continuazioni.

## Condizioni: revisione 3

La nuova estrazione riproducibile `analyze_conditions.py` legge direttamente dall'eseguibile le tabelle di selezione. Scope 0 seleziona lo stato globale, scope 1 lo stato locale. Il quinto argomento del comando 31 seleziona: 0 uguaglianza, 1 minore, 2 maggiore, 3 intervallo inclusivo. I confronti sono tra interi con segno. L'addizione dell'opcode 46 riproduce il riporto modulo 2^32 dell'originale senza overflow con segno nel codice C++.

Il caricatore originale 9:2beb–2c39 legge il quarto campo delle dichiarazioni locali e lo memorizza nello stato. Il terzo campo è metadato: non è il valore iniziale. Le dichiarazioni globali lette da una scena aggiornano metadati e non inizializzano lo stato globale. Il prototipo conserva una distinzione tra valori conosciuti e sconosciuti: rifiuta l'intera sequenza se uno dei valori utilizzati non è ancora disponibile. L'inizializzazione globale è stata risolta nella revisione 4, descritta sotto.

I collegamenti seguono la logica del lettore 9:3289–34f8: un solo puntatore all'ultima condizione, aggiornato dall'opcode 31; 45 collega quella condizione al comando corrente, mentre 42 la collega al comando successivo, quando presente. Non viene inventata una pila di blocchi annidati. All'esecuzione, una condizione falsa segue il proprio collegamento; un ELSE da saltare segue il collegamento del comando successivo. Il flag dell'ultimo confronto è condiviso tra le sequenze come nell'eseguibile originale.

La verifica nativa comprende 64 combinazioni di confronto (entrambi gli scope, quattro operatori, otto valori inclusi gli estremi con segno), tre esiti della catena IF/ELSE/CONDITION, overflow dell'addizione, separazione degli scope, ritardo della destinazione, stato sconosciuto e caricamento delle dichiarazioni locali. Inoltre usa direttamente i comandi originali di P505: un confronto falso esegue un comando, quello vero tre. La sequenza originale 9 di P530 azzera i valori 0,2,3,4,5,6,7,8,10, conservando il valore 9.

L'analisi dei 416 file rigorosamente decodificati rileva 1.296 confronti e 738 assegnazioni; questi sono conteggi di istruzioni lette, **non di istruzioni già eseguibili in contesto di gioco**. Molte sequenze contengono ancora comandi non supportati. Il rapporto conserva esplicitamente le cinque scene escluse.

## Ciclo delle scene: revisione 4

La precedente ipotesi di cercare i valori iniziali globali in GAMEDATA è stata sostituita da evidenze dirette: `_CreateGame` (13:0025) alloca 0x7e3 byte con `_calloc` (1:17b2, nome confermato dai simboli originali), quindi lo stato globale parte a zero. `_clear_globals` (9:408c–40c8) azzera esplicitamente 100 valori, indici 0–99, all'offset 0x0a della struttura. `_do_place` (9:019a–01a7) invoca questa funzione entrando in P1, prima di liberare i comandi pendenti e caricare la scena.

Il modulo riproduce l'inizializzazione e l'azzeramento in P1, conserva i globali negli altri cambi scena e continua a rifiutare le variabili locali non dichiarate. Il test reale di caricamento imposta il globale 99, passa a P103 verificandone la conservazione e poi entra in P1 verificando che tutti i 100 valori siano zero.

`_load_place` (9:2796–27a8) accoda gli script di ingresso nell'ordine serializzato. `_place_loop` (9:086a–0872) elabora i comandi pendenti. Quindi anche il primo comando con delay=-1 attende il primo passaggio della coda: non va eseguito subito durante il caricamento. I test verificano questo caso e il ritardo iniziale positivo con un orologio astratto.

L'opzione `astronomica_entry_scripts=true` abilita l'accodamento degli script interamente supportati al caricamento. Ogni sequenza non supportata viene scartata per intero, con avviso nel log. Le sequenze ammesse vengono accodate nell'ordine del file, dopo la disponibilità dello stato locale. Questa è una modalità sperimentale parziale, disattivata per impostazione predefinita: fino alla revisione 10 nessuna scena con script aveva tutte le sequenze di ingresso coperte; la revisione 11 esegue integralmente quella di P29. Non si presume che le sequenze omesse siano irrilevanti.

P505 accoda esattamente due sequenze ammesse; il test verifica che nessun comando venga eseguito durante l'accodamento e che il primo passaggio esegua due istruzioni nello stato iniziale originale. Restano escluse le altre sequenze della scena.

## Ancora da ricostruire

La revisione 7 aggiunge l'opcode 7 per il posizionamento assoluto degli sprite grafici supportati, preservando la conversione a 16 bit e il caso speciale (0,0). Evidenze e prove su P517 sono descritte in `SPRITES.md`.

La revisione 8 aggiunge l'opcode 47 per lo spostamento relativo, verificato con due incrementi consecutivi sui dati originali di P510; vedere `SPRITES.md`.

La revisione 9 estende i bersagli dei comandi grafici ai cloni statici risolti correttamente, conservando posizione e visibilità indipendenti. Non aggiunge opcode e non abilita l'interazione mouse degli sprite.

La revisione 10 aggiunge l'opcode 15 per la scelta esplicita del fotogramma. Gli indici vengono verificati usando il numero di fotogrammi della sorgente risolta; il comando non abilita l'avanzamento temporizzato.

La tabella dell'esecutore contiene 48 voci, mentre il lettore riconosce 49 layout: non sono elenchi intercambiabili. Restano da verificare il ciclo completo degli script e l'interazione delle condizioni con le azioni specifiche del gioco, oltre al confronto dinamico con l'eseguibile originale.

Restano mancanti esecuzione completa degli script delle scene, sprite, enigmi, filmati, audio, inventario e salvataggi. Le regole specifiche di transizione presenti in `_do_place` non sono ancora riprodotte. Nessuna percentuale di completabilità del gioco è stata misurata.


## Timer e richiami: revisione 11

Il modulo 3 della tabella import NE originale � MMSYSTEM. `_handle_pending`
15:1b48 richiama il suo ordinal 607: `timeGetTime`, identificato dalla
[tabella ABI Win16 mantenuta da Wine](https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/mmsystem.dll16/mmsystem.dll16.spec).
La [documentazione Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timegettime)
specifica millisecondi e rollover a 32 bit. `analyze_timing.py` riestrae i nomi
dei moduli dal solo ASTRO.EXE originale, verificandone SHA-256; le chiamate
sono visibili nei disassemblati riproducibili gi� inclusi.

L'opcode 41, handler 15:118b, legge l'indice zero-based dalla tabella a
DS:0cd8 e chiama `_pend_command`. Non chiama `_do_command`: il programma
richiamato attende un altro passaggio della coda. Il motore usa getMillis()
in esecuzione normale e un orologio controllato nelle verifiche native.

Prima di avviare una catena si verifica tutto il grafo dei programmi
raggiungibili, gestendo anche i cicli senza ricorsione. Indici inesistenti,
programmi vuoti, comandi sconosciuti o bersagli non disponibili causano il
rifiuto prima di qualsiasi effetto. Un richiamo aggiunge lavoro alla coda,
senza ricorsione nell'esecuzione.

Limite esplicito: `_pend_command` copia il timestamp del template, non lo
reinizializza. Finch� non � ricostruito il suo intero ciclo di vita, vengono
rifiutati i programmi richiamati e gli ingressi con primo ritardo positivo.
Le continuazioni positive, il cui timestamp � aggiornato in 15:1679, sono
supportate. L'API di test mantiene separatamente i ritardi iniziali astratti.

Il test carica P29 originale ed esegue l'intero script flash_light: condizioni,
show/hide, assegnazione dello stato e autorichiamo dopo 600 ms. Controlla
assenza di esecuzione anticipata, rinvio del richiamo al passaggio successivo,
ritorno allo stato iniziale e hash RGB degli stati. Include inoltre test
sintetici per richiamo ciclico, indice errato e rifiuto atomico di una catena
che richiama codice non supportato. Tutti i test precedenti restano attivi.

Questo verifica un'animazione guidata dallo script originale, non il supporto
generale dell'avanzamento automatico dei fotogrammi o della scena TV/VCR.


## Input sugli sprite: revisione 12

`_do_mouse` 9:1181�11eb cerca gli sprite in ordine crescente, dal primo.
Sono candidati quelli con flag click (+2d5) o drag (+2d9) uguale a 1.
`_SWIsPointInSprite` 7:0ec1 confronta coordinate signed 16 bit con il
rettangolo +17/+19/+1b/+1d: **tutti i bordi sono inclusi**. Non legge
visibilit� o maschera. Il primo candidato colpito impedisce la ricerca delle
aree rettangolari sottostanti. Le aree non-sprite conservano i bordi destro
e inferiore esclusi. Il tipo 0 usa il normale accodamento; il tipo 2 esegue
anche una sequenza aggiuntiva, esclusa nella revisione 12. La revisione 13 ne identifica la funzione come pressione/rilascio del pulsante, non trascinamento.

Il caricatore conserva ora distintamente flag click, drag, auto-frame e
auto-move. La modalit� `astronomica_sprite_input=true` accetta geometrie
statiche a un livello. Quando il fotogramma di anteprima non � selezionato,
richiede che tutti i fotogrammi abbiano dimensioni identiche; quindi non
presume quale fotogramma sia attivo. Una geometria sconosciuta impedisce
di proseguire la ricerca; uno script sconosciuto consuma il clic senza
eseguirlo o trasferirlo agli oggetti sottostanti. � una modalit� parziale.

Opcode 28/29: gli handler 15:0c08/0c3c impostano/azzerano DS:06a5 quando
l'argomento � negativo. Gli argomenti non negativi modificano l'abilitazione
di un singolo sprite e sono tuttora rifiutati. Il flag globale blocca nuovi
clic ma non ferma la coda. `_do_place` 9:01e0 lo azzera al cambio scena;
il motore riproduce questo azzeramento.

P510, sprite 10 e 11: la verifica usa gli script di clic completi originali,
non singole istruzioni estratte. Controlla accodamento, scelta esclusiva dei
cinque fotogrammi, variabile locale 4 uguale a 1/2, blocco a 149 ms e
riabilitazione a 150 ms. Al cambio scena verifica pulizia della coda e del
blocco. Verifica anche bordi inclusivi e la precedenza di uno sprite
invisibile con script rifiutato. Quest'ultimo caso � una variazione di test
in memoria, non una modifica dei file originali.

`verify_mouse_reference.py` genera indipendentemente con Pillow le due
immagini attese usando bitmap e maschere originali. Hash FNV-1a RGB565:
`fb10a99b`, `966034ff`; RGB888: `3f2d859f`, `655cfed9`.
Le immagini sono in `evidence/mouse/`. Il test nativo confronta l'intero
schermo utile 640�456, oltre allo stato interno.

Questo aggiunge interazioni complete di singoli pulsanti; mancano ancora
inizializzazione completa degli enigmi, trascinamento, hover, audio, filmati
e confronto interattivo con l'eseguibile originale.


## Fotogrammi iniziali, animazione e pulsanti tipo 2: revisione 13

Nuove estrazioni dall'eseguibile originale:
`_SWAddFrame` (7:0678) seleziona il primo elemento dell'array dopo ogni
aggiunta; `_CreateSpriteFromBmpMem` (11:00b4) imposta l'intervallo 0..n-1.
`_SWCreateSprite` inizializza indice 0, avanzamento +1 e timestamp 0.
La modalit� sperimentale inizializza quindi a 0 il fotogramma degli sprite
non clonati a un livello, senza dedurlo dall'aspetto dello sfondo.

`_load_place` 9:2e88�2eaa converte il primo campo del blocco auto-frame
attraverso AX signed 16 bit e lo passa a `_SWSetSpriteFrameTime` (7:09a9).
`_SWProcessSpriteWorld` (6:07c8) legge timeGetTime; quando la differenza
con segno raggiunge il periodo, salva il tempo attuale e avanza di uno,
ripartendo dall'inizio oltre l'ultimo indice. Non recupera pi� fotogrammi
per un ritardo lungo e non verifica la visibilit� prima di avanzare.

La modalit� `astronomica_animation=true` supporta per ora sprite non
clonati, senza movimento automatico, a un livello, con blocco originale
[periodo,1,0]. I periodi negativi vengono esclusi, 0 avanza a ogni passaggio.
I valori diversi dei due campi finali restano conservativamente esclusi;
non viene attribuito loro un significato non dimostrato.
Il timer parte da zero nel dominio getMillis di ScummVM: non si rivendica
la stessa fase iniziale dell'orologio globale di una sessione Windows 3.x.

Correzione della precedente interpretazione del clickType 2:
il simbolo originale DS:0bf0 � `_button_click`. `_do_place` 9:0071�00d5
inizializza una coppia di comandi 15: fotogramma 1 immediato, fotogramma 0
dopo 500 ms. `_do_mouse` sostituisce l'id dello sprite in entrambi i nodi,
esegue questa coppia e poi accoda lo script di clic. Il motore valida
preventivamente lo script utente e la coppia grafica, applica il primo
fotogramma subito e mantiene l'ordine delle continuazioni. Il trascinamento
rimane non implementato; gli sprite con quel flag continuano a essere esclusi.

La prova nativa usa integralmente il clic dello sprite 7 di P510: blocco,
show dello sprite 2, sblocco dopo 400 ms, hide dopo ulteriori 10000 ms.
Controlla 399/400 ms per il fotogramma, 499/500 per il rilascio del pulsante,
10399/10400 per la scomparsa, avanzamento nascosto e un salto temporale
senza recupero dei fotogrammi. I test isolati includono rollover a 32 bit,
periodo zero e periodo negativo.

`verify_animation_reference.py` verifica la sequenza nel file originale e
genera con Pillow le immagini attese: RGB565 `bddce235`/`db506b77`, RGB888
`74ec5203`/`cbf46977`. Il motore confronta questi hash sullo schermo 640�456.
Il secondo riferimento include il pulsante ancora premuto a 400 ms.
Le immagini sono in `evidence/animation/`. Restano attive tutte le verifiche
precedenti; non � ancora possibile completare l'enigma P510.


## Suoni locali: revisione 14

L'opcode 9 entra in 15:04a8, chiama `_in_custom` (18:18ba, qui senza
effetti) e passa il primo argomento a 16 bit a `_playSound` (9:3b07).
Quest'ultima usa direttamente l'id nel nome del file: il ramo locale
costruisce `%s/PLACES/P%ld/S%d.WAV`, stringa originale DS:04ad.
La tabella delle dichiarazioni sonore della scena non viene consultata
da questo ramo. L'argomento 3 in P510 riproduce quindi P510/S3.WAV.

La chiamata MMSYSTEM ordinal 2 usa flag 3 nel ramo normale, riproduzione
asincrona senza suono predefinito. Il precedente suono viene interrotto.
Il motore utilizza un solo handle del mixer ScummVM; un nuovo avvio ferma
quell'handle, mentre caricamento di una nuova scena e distruzione del
motore liberano il suono. `_do_place` invoca `_stop_sounds` in 9:06a6.

La modalit� opt-in `astronomica_audio=true` ammette solo WAV PCM locali
riconosciuti dal lettore ScummVM e argomenti 0..899. La disponibilit� viene
registrata al caricamento e controllata prima di eseguire una sequenza:
un file mancante fa rifiutare l'intero script. Restano esclusi gli id globali
900+, i casi sincroni P505/S2..S10 e P512/S14, e la pausa/ripresa del filmato
presente nell'originale. Non viene rivendicato il supporto audio completo,
del suono d'ingresso o dell'audio di fondo. I filmati non sono ancora attivi.

Il test nativo legge P510/S2, S3 e S6 con il decoder ScummVM e confronta
numero dei campioni, frequenza 11025 Hz, mono, e hash dei campioni PCM16LE.
`verify_audio_reference.py` genera gli stessi riferimenti indipendentemente
con il modulo Python wave, partendo dai WAV originali PCM8 unsigned:
3627/4272/23808 campioni, hash `1c898683`/`eed1c407`/`01fbde02`.
Il rapporto `evidence/audio.json` contiene anche SHA-256 dei file originali.

La prova dei clic usa i programmi originali completi degli sprite 3 e 5:
S3 viene avviato dopo il passaggio in coda; S6 viene sostituito da S2
soltanto dopo 150 ms di attesa per lo sblocco e altri 1300 ms. Si verificano
handle attivo, numero degli avvii, rifiuto di S899 mancante e arresto al
cambio scena. Il backend di verifica � SDL dummy: questi controlli
verificano decodifica e consegna al mixer, non un ascolto dagli altoparlanti.


## Uscite ritardate: revisione 15

L'opcode 5 (15:0363�038f) aggiorna DS:0c8c con la destinazione e imposta
DS:0c98, poi raggiunge la gestione comune della continuazione. Non carica
direttamente il file della nuova scena. Il ciclo `_do_place` controlla
il flag in 9:0258; prima del successivo caricamento chiama
`_free_pending_commands` in 9:01a7. Lo sblocco dei clic viene azzerato
esplicitamente in 9:01e0.

Viene rimosso il vincolo che imponeva a new_place di essere l'ultima
istruzione, limitatamente alle catene il cui successore passa dalla coda
(delay >= 0). La verifica preventiva continua a validare tutta la catena.
I successori immediati con delay=-1 restano esclusi: potrebbero ancora
produrre effetti nella vecchia scena prima del cambio, comportamento non
ancora interamente riprodotto. Restano inoltre incomplete le regole
specifiche di accesso e le combinazioni di pi� cambi scena nello stesso
passaggio. Non si rivendica equivalenza generale di tutte le transizioni.

P510 sprite 4, programma originale completo: blocco clic, S4,
new_place(136,500), sblocco dopo altri 150 ms. L'ultimo comando viene
accodato ma eliminato dal cambio scena. Il test verifica permanenza a
499 ms, arrivo a 500 ms, coda vuota, input sbloccato, conservazione del
globale 95 e assenza di altre istruzioni eseguite a 650 ms.
Controlla inoltre che l'immagine della destinazione non cambi a 650 ms.

La seconda prova usa P510 sprite 6: S5, new_place(408,700). Verifica
permanenza a 699 ms e arrivo a 700 ms. Entrambe passano dall'effettivo
gestore dei clic, comprendendo la pressione del pulsante tipo 2.
Le destinazioni vengono caricate e renderizzate dai MEGAFILE originali.
Audio, grafica, condizioni e prove precedenti continuano a passare.

Precisazione sull'audio della revisione 14: il riferimento 9:06a6 dimostra
lo stop all'uscita dal ciclo principale, non prova da solo lo stop a ogni
transizione. Fermare l'handle al caricamento rimane per ora una politica
conservativa del prototipo; la continuit� sonora tra scene va ricostruita.


## Indicatori nelle condizioni: revisione 16

L'opcode 33 non copia condizioni: modifica un bit del valore selezionato.
Gli argomenti sono scope, id, posizione del bit, azione. Lo scope 0 sceglie
i globali, 1 i locali; scope 2 resta escluso. La tabella originale in
15:180e contiene 0/1/2 e destinazioni 0f34/105b/1186.

L'eseguibile carica la costante float 2.0 da DS:0726 e chiama l'ordinal 632
di BC40RTL.DLL. Il nome esportato nella libreria originale � `_pow`,
confermato leggendo la sua tabella NE. `analyze_bits.py` riproduce questa
estrazione, riporta SHA-256 della libreria e verifica quello di ASTRO.EXE;
il rapporto � `evidence/bits.json`. Non � stato utilizzato codice di
implementazioni precedenti del gioco.

Con azione 1 il risultato 2^bit viene combinato con OR. Nel ramo di
disattivazione l'originale verifica prima che il bit sia presente, poi
sottrae 2^bit; quindi una seconda disattivazione non altera altri bit.
Il modulo ammette azioni 0/1 e posizioni 0..30, per le quali la potenza e
la conversione all'intero signed originale sono esatte. Bit 31, posizioni
negative, scope non supportati e id fuori intervallo vengono rifiutati
prima di qualsiasi effetto. Il codice usa unsigned 32 bit per conservare
gli altri indicatori, incluso un bit di segno gi� presente.

Le prove isolate verificano entrambi gli scope, bit 0/30, ripetizione delle
operazioni, conservazione del bit 31 gi� presente, separazione tra scope,
accodamento e rifiuto atomico dopo un'assegnazione valida.
La prova sul corpus carica P511 e usa quattro istruzioni originali 33
della sequenza 3, una per volta. Il valore locale 5 viene preparato a 6
nel test: i risultati attesi sono 7,6,6,6, mentre il globale 5 resta 123.
Questa preparazione verifica i bit estranei; non � lo stato iniziale del
gioco, che rimane inalterato nei file originali. Non viene eseguita tutta
la sequenza P511, che contiene ancora operazioni non supportate.

Compilazione e verifiche native precedenti continuano a passare.
L'avanzamento percentuale resta una stima del lavoro di sviluppo, non
una misura del gioco completabile.


## Scelta casuale delle varianti: revisione 17

La routine originale `_rand` (1:0b6b) usa uno stato unsigned a 32 bit:
state = state * 0x015a4e35 + 1, con riporto modulo 2^32. Restituisce
(state >> 16) & 0x7fff. Il moltiplicatore proviene dalle istruzioni MOV
in 1:0b75 e 0b78; l'helper 1:0b3c esegue la moltiplicazione a 32 bit.
`_srand` (1:0b54) inizializza lo stato con un seme a 16 bit, azzerando
la parte alta. `probe_random.py` riestrae i tre disassemblati dal solo
ASTRO.EXE originale verificandone SHA-256; richiede Capstone.

`_RangedRdm` (15:1d20) calcola low + rand * (high-low+1) / 32768,
con operazioni intermedie a 16/32 bit. L'opcode 40 usa questa routine
e memorizza il risultato zero-extended nel valore globale o locale.
Sono supportati scope 0/1, id 0..99, estremi non negativi <=32767 e
ampiezza <=32767. Intervalli invertiti, negativi o con overflow della
larghezza signed 16 bit vengono rifiutati prima di consumare casualit�.
Lo scope 2 rimane escluso.

Il seme iniziale in esecuzione normale proviene da ScummVM e viene
ridotto a 16 bit; l'originale usa il tempo del sistema nella chiamata
iniziale a srand. Si riproduce la sequenza a parit� di seme, non la stessa
partita partendo da due orologi diversi. Il generatore non viene
reinizializzato al cambio scena.

`analyze_random.py` estrae il moltiplicatore dal file e genera vettori
indipendenti per semi 0,1,65535 in `evidence/random.json`. La verifica
nativa confronta dodici numeri grezzi per seme 1 e dodici risultati
nell'intervallo 1..3 in entrambi gli scope. Controlla anche intervallo
singolo 32767..32767, rifiuti senza consumo del generatore e persistenza
tra scene.

Il test sui dati carica P510, estrae il suo comando 40 originale
[1,0,1,3] e verifica la sequenza 1,1,2,1,2,1,2,1,3,3,1,2 con seme 1.
� una prova dell'istruzione originale, non dell'intera catena d'ingresso
P510, che contiene ancora filmato e comandi personalizzati non supportati.
Compilazione e tutte le verifiche precedenti restano superate.


## Varianti senza ripetizioni: revisione 18

L'opcode 39 (15:11a8) usa quattro argomenti: scope/id della maschera
delle varianti usate e scope/id del risultato. Legge anche la larghezza
della maschera dai metadati: +19a per i globali, +588 per i locali.
Il caricatore 9:2b53 e 9:2beb dimostra che si tratta del terzo campo
serializzato della dichiarazione. Il modulo ora conserva queste larghezze;
quelle globali persistono, quelle locali vengono ricaricate con la scena.

La routine conta i bit non impostati entro la larghezza, estrae il rango
1..numero_disponibile, cerca il bit corrispondente, lo imposta e scrive
la posizione +1 nel risultato. Si conservano eventuali bit fuori dalla
larghezza. Se non resta alcuna variante, RangedRdm(1,0) consuma comunque
un'estrazione; nessun risultato viene scritto. Non si inventa un reset.

Il sottoinsieme ammesso comprende scope 0/1, id noti e larghezze 1..31.
Le altre dichiarazioni vengono rifiutate preventivamente. Le operazioni
calcolano la disponibilit� al momento dell'esecuzione, anche se lo stato
� cambiato dopo l'accodamento. Lo stato sorgente viene aggiornato prima
del risultato, nell'ordine originale.

La verifica usa il comando [1,1,1,0] originale di P505, con le dichiarazioni
originali (larghezza 8, maschera iniziale 0). Con seme 1 l'ordine �
1,2,5,3,6,4,8,7. Dopo otto estrazioni la maschera � 255; la nona lascia
invariato il risultato ma consuma il generatore. Il successivo numero
grezzo deve essere 31126. `verify_variant_reference.py` ricava un riferimento
indipendente usando una lista di candidati, nei dati `evidence/variants.json`.

I test isolati verificano tutte le quattro combinazioni globale/locale,
una maschera parzialmente usata, bit esterni preservati, esaurimento e
rifiuto di larghezza 32 senza consumare casualit�. Le verifiche precedenti
continuano a passare. L'intera sequenza d'ingresso P505 resta incompleta:
non � ancora una prova giocabile dell'enigma.


## Arresto audio: revisione 19

L'opcode 10, handler 15:04bd, passa il proprio argomento a `_stop_sounds`
(9:3abe). La funzione non legge tale argomento: chiama MMSYSTEM ordinal 2
con puntatore nullo e flag 1. Non seleziona quindi un canale numerato.
Il motore interrompe l'unico handle audio locale gestito finora; non ferma
gli altri canali di ScummVM. L'operazione resta valida anche senza un suono
attivo. Il parametro viene letto ma non usato, come nell'originale.

Il nuovo test carica il comando 10 originale da P501, con argomento -1
e ritardo 3500 ms. Lo esegue isolatamente su P510/S1.WAV: il mixer deve
essere attivo a 3499 ms e fermo a 3500 ms. Ripete lo stop a canale fermo,
verifica un parametro diverso e verifica il rifiuto atomico di una catena
che contiene un comando sconosciuto dopo lo stop. In quel caso il suono
deve restare attivo. Si tratta di una combinazione di test dei dati
originali, non dell'intera sequenza o dell'enigma P501.

La build e le verifiche native passano, inclusa la selezione senza ripetizioni
della revisione 18. La verifica audio usa ancora il backend SDL dummy;
non costituisce una prova di ascolto o di sincronizzazione con i filmati.

## Intervalli dei fotogrammi: revisione 20

Opcode 48 [sprite, primo, ultimo], handler originale 15:0520-05af.
Il limite inferiore negativo viene portato a zero, quello superiore
oltre il numero dei fotogrammi viene ridotto a numero-1. La chiamata
_SWSetSpriteFrameRange (7:0981) passa due interi con segno a 16 bit;
il setter scrive soltanto i campi +5f e +63. Il fotogramma corrente e
il timestamp restano invariati. _SWProcessSpriteWorld (6:0848-0899)
aggiunge il passo; sotto il primo limite passa all'ultimo, sopra
l'ultimo passa al primo. Per il sottoinsieme gia ammesso il passo e +1.

Il motore ammette intervalli risultanti validi, non vuoti, entro 0..32767.
Rifiuta preventivamente intervalli invertiti, sorgenti sconosciute e
catene con istruzioni non supportate. Gli intervalli sono per istanza;
l'animazione automatica dei cloni rimane esclusa dal sottoinsieme attuale.
Non viene forzato il fotogramma corrente quando cambia l'intervallo.

I quattro comandi originali nello script 1 di P511 sono [5,0,1],
[5,1,2], [5,2,3], [5,2,3], tutti con ritardo -1. Lo sprite 5 ha quattro
fotogrammi e temporizzazione [500,1,0]. La verifica nativa esegue ciascun
comando isolatamente e verifica quattro passi, il limite 499/500 ms,
la conservazione di frame/timer, il clamp e il rifiuto atomico.
verify_range_reference.py ricostruisce quattro immagini con Pillow dai
file originali: evidence/range contiene PNG e hash RGB888/RGB565.
Il test nativo confronta la composizione con questi hash mantenendo gli
altri sprite ai fotogrammi iniziali; non esegue l'intero enigma P511.

## Sottofondo locale: revisione 21

La disassemblatura originale distingue tre comandi:
- 25, 15:04d0: disabilita il ripristino del sottofondo e ferma il suono.
- 26, 15:04e1: riabilita il ripristino senza avviare immediatamente audio.
- 27, 15:04ea: ferma il suono, seleziona il nuovo identificatore e azzera
  il timestamp dell'ultimo suono principale.

_playLoop (9:3c29) verifica la disponibilita del canale senza interromperlo;
nelle scene 500..550 attende un intervallo strettamente maggiore di
5000 ms dal timestamp aggiornato da _playSound (9:3b2c). Quindi richiede
riproduzione asincrona ripetuta con flag 0x1b. Il ripristino del loop non
aggiorna quel timestamp. Il prototipo usa il wrapper di ripetizione di
ScummVM sull'unico handle audio, controllando il canale nel ciclo eventi.
Il tempo degli effetti accodati ora viene passato fino all'audio.

Il sottoinsieme ammette solo file PCM locali validati, con audio abilitato;
identificatori globali >=900 e file mancanti restano esclusi. Le eccezioni
sincrone gia escluse dall'audio principale restano escluse anche qui.
Il caricamento di una scena azzera la selezione esplicita e riabilita il
loop. Non si ricostruiscono ancora la selezione implicita dei sottofondi
globali, i controlli originali relativi ai filmati e ai dialoghi o tutta
la continuita audio fra scene. I filmati non sono eseguiti dal prototipo.

Il test usa 27 [12] originale di P511 e 25/26 originali di P509,
isolatamente. S12 e PCM mono 11025 Hz, 1834 campioni, hash PCM16LE
ad03e6da (riferimento indipendente verify_loop_reference.py). Verifica
due cicli completi e 37 campioni del terzo, il limite 5000/5001 ms,
assenza di riavvii mentre il canale e attivo, priorita di S2, pausa,
riattivazione, rifiuto del file mancante e pulizia al cambio scena.
La fine del suono principale viene simulata fermando l'handle, evitando
attese reali: la verifica del mixer usa SDL dummy e non prova l'ascolto.

Analisi per il prossimo sviluppo: lo script 0 di P511 usa anche il
comando personalizzato 23 [25,0,0,0,0,0]. _do_custom 4:56b5 seleziona
il comportamento in base alla scena e richiama _puzzle_successful.
Questa logica non e implementata: l'intero grafo resta rifiutato.

## Completamento P511: revisione 22

La tabella a 4:6c94 seleziona per P511 l'handler 4:57c6. Questo controlla
il DWORD +0x76 della struttura puntata da DS:07a8, richiama
_puzzle_successful soltanto quando vale zero, quindi scrive 1. Lo stesso
puntatore viene usato da _clear_globals (9:408c), che azzera 100 DWORD
a partire da +0x0a: +0x76 corrisponde quindi alla variabile globale 27,
non a uno stato separato. Anche valori negativi/nonzero vengono portati
a 1, senza ripetere il suono o incrementare il contatore.

_puzzle_successful (3:39ae) chiama _playSound(912), poi incrementa DS:0153.
Il percorso originale per id>=900 usa SOUNDS/S%d.WAV sottraendo 900.
Il suono 912 rientra nell'eccezione sincrona di _playSound: dura circa
2,206 secondi. Il riferimento indipendente e evidence/success.json:
24320 campioni mono 11025 Hz, hash PCM16LE 3dcde548.

L'interprete ammette soltanto 23 [25,0,0,0,0,0] quando il motore fornisce
il gestore P511 e ha validato il WAV PCM globale con audio abilitato.
Gli altri contesti e sottocomandi personalizzati restano esclusi. Il
callback applica prima gli effetti gia accodati, attende il mixer senza
eseguire altri script, incrementa il contatore e restituisce il tempo
successivo al suono. Solo dopo viene scritto il flag globale; eventuali
continuazioni temporizzate partono da quel tempo. Durante l'attesa resta
possibile chiudere l'applicazione; gli altri input non vengono eseguiti.
Il contatore e per la sessione e non esistono ancora salvataggi.

La verifica usa il comando originale isolato: rifiuto atomico di una
catena sconosciuta, prima esecuzione, ripetizione senza nuovo suono,
normalizzazione di -2, successore a 999/1000 ms dopo la fine del suono,
persistenza della globale cambiando scena, reset P1 e rifiuto senza audio.
Il test usa SDL dummy: prova l'attesa del mixer, non l'ascolto. La suite
precedente passa. Il grafo completo P511 resta escluso: include ancora
una transizione seguita da opcode 45 immediato e comandi di immagini non
supportati. Nessun enigma completo viene dichiarato giocabile.

## Transizioni con chiusura della diramazione: revisione 23

Opcode 5 (15:0363) scrive la destinazione in DS:0c8c e imposta DS:0c98;
_execute_command continua a elaborare i collegamenti immediati e
_do_command li percorre prima di restituire. _do_place verifica la
richiesta dopo _place_loop e ripulisce i comandi in attesa prima del
caricamento. La transizione puo quindi precedere un opcode 45 immediato.

La validazione ora permette nel suffisso della transizione soltanto
istruzioni immediate 1,2,31,42,45. Controlla tutto il suffisso, anche oltre
ritardi intermedi, perche i collegamenti condizionali possono saltarli.
Gli effetti immediati sulla vecchia scena restano rifiutati. Il caricamento
avviene dopo il controllo del flusso; le continuazioni accodate vengono
eliminate al cambio scena come prima. Il controllo dell'indice viene
ripetuto DOPO aver seguito il collegamento condizionale: un salto alla
fine dello script termina senza leggere oltre l'array.

La prova nativa usa tutto lo script 0 originale P511 senza modificarlo,
impostando local[5]=7 e global[27]=0 soltanto come condizione iniziale.
Verifica le otto posizioni dello sprite 20 ogni 300 ms, la mancata
esecuzione anticipata del successo, il suono sincrono e il cambio P388
a 1000 ms dalla fine del suono. Verifica la pulizia delle continuazioni,
lo sblocco input e la persistenza del successo. Nel ramo non risolto,
local[5]=0, verifica che i clic restino bloccati a 74 ms e si sblocchino
a 75 ms, senza successo o transizione. Una variante di test con un
nascondimento immediato dopo la diramazione resta rifiutata atomicamente.
verify_ending_reference.py conferma le 21 istruzioni dai file originali,
con risultato riproducibile in evidence/ending.json.

Questa revisione supera il limite dello script 0 citato nella revisione
22. Non dimostra che il giocatore possa risolvere l'intero P511: lo stato
risolto e preparato dal test, e immagini/interazioni restano incomplete.

## Successo condiviso e ricognizione: revisione 24

La mappa delle scene e derivata dalla tabella originale a 4:6c94 nel
sottocomando 25 di _do_custom. probe_success_map.py controlla l'impronta
dell'eseguibile, legge le destinazioni e verifica nei blocchi disassemblati
lo stesso offset globale nel confronto e nell'assegnazione, oltre alla
chiamata _puzzle_successful. evidence/success-map.json contiene le 29
associazioni comuni. Il motore passa all'interprete la scena verificata;
la variabile del successo non e piu fissata a 27.

Eccezioni lasciate escluse: P513 incrementa DS:0153 senza suono; P529
scrive anche il DWORD +0xfa (globale 60); P530 suona ma non incrementa
il contatore. P352/P359 non fanno nulla in questo ramo. P506 e le cinque
varianti P531-P535 puntano allo stesso handler e quindi alla globale 23.
Le associazioni non vengono dedotte dal numero della scena.

La verifica nativa normalizza un valore nonzero per tutte le 29 scene,
controllando tutte le 100 globali dopo ogni operazione e l'assenza di suoni
o conteggi ripetuti. Esegue inoltre il comando originale del clic dello
sprite 6 di P517 partendo da globale 33 zero, con suono e conteggio reali
nel mixer dummy; verifica condivisione P506/P533 ed esclusione dei tre
casi speciali. Tutte le precedenti verifiche restano attive.

survey_puzzles.py legge nuovamente i file originali P500-P537. Per i file
con coda extra valida il prefisso e registra la coda. La ricognizione
nativa misura separatamente canRun sui template di ingresso: non esegue
le sequenze, non misura tutti gli input e non dimostra completabilita.
I risultati riproducibili sono in puzzle-survey.json e in
 evidence/puzzle-coverage.json. Non viene assegnata una nuova percentuale
globale di completamento: la precedente era orientativa.

## Bitmap esterni 20/49: revisione 25

Opcode 20 (15:05ba) costruisce il percorso PLACES/P<scena>/<nome>, porta
il nome a maiuscole, legge un bitmap e conserva le coordinate attraverso
registri a 16 bit con segno. Non visualizza ancora nulla. Opcode 49
(15:068a) usa SRCCOPY (0x00cc0020) sul buffer di sfondo del mondo (+0x0c),
rilascia il bitmap temporaneo e chiama _UpdateGame (13:0eba).
_SWUpdateSpriteWorld (6:069d) copia lo sfondo e ricompone gli sprite.
Le nuove disassemblature sono incluse in evidence/interpreter.

Il sottoinsieme ammesso richiede 20 seguito da 49 con delay=-1, senza
istruzioni intermedie. Ogni 49 deve avere quel predecessore. Il motore
puo quindi applicare la coppia in una singola azione, senza conservare
un bitmap in attesa. Il controllo preventivo verifica il file nella
scena corrente e rifiuta la catena intera se non supportata. Sono ammesse
scene a un livello, nomi locali semplici e immagini fino a 640x480;
la superficie viene convertita nel formato del backend e ritagliata
ai bordi. I BMP esterni a 1 bit restano esclusi. Le coordinate vengono
convertite a int16 come nell'handler originale.

Il disegno modifica _background: un ridisegno successivo degli sprite
conserva l'immagine. Il caricamento della scena ripristina lo sfondo
originale. Le forme con staging attraverso rami o attese restano escluse,
compreso lo script 1 di P508. Anche il supporto dei livelli multipli
resta incompleto.

verify_background_reference.py costruisce con Pillow sei composizioni
indipendenti dai file originali: APOLLO/CAVE in P505, SKY1/SKY2 in P509,
CLOUD3/CLOUD2 in P511. La suite nativa esegue le rispettive coppie
originali e confronta gli hash RGB888/RGB565, la persistenza al ridisegno
e il ripristino al caricamento. Verifica rifiuto di file assente, percorso
non locale, visualizzazione ritardata e comando sconosciuto successivo.
Sono prove di singole coppie, non di soluzione integrale degli enigmi.

## Caricamento separato dalla visualizzazione: revisione 26

Gli handler originali 15:05ba e 15:068a conservano un bitmap intermedio
con coordinate globali: il comando 20 non deve alterare lo sfondo. Il
motore ora mantiene una superficie temporanea separata e coordinate;
49 la copia nello sfondo, libera la superficie e ridisegna gli sprite.
La superficie sopravvive ai passaggi della coda, alle diramazioni e alle
attese. Caricamenti successivi sostituiscono la superficie senza disegno.
Il cambio scena la libera; una visualizzazione senza immagine in attesa
ridisegna soltanto la scena, senza usare puntatori gia liberati.

Il controllo preventivo continua a validare file e catene intere, ma
non impone piu l'adiacenza di 20/49. Rimangono le restrizioni sui bitmap
esterni monocromatici e sulle scene a piu livelli. Non si riproducono
perdite di risorse o eventuali riusi di handle GDI gia liberati presenti
nell'eseguibile originale.

La prova nativa esegue lo script 1 P508 senza modificarne le istruzioni,
18 volte con seme casuale fissato. Verifica 18 scelte distinte, tutti
gli hash dei riferimenti Pillow, l'assenza di disegno durante lo staging,
la completa consumazione della coda e l'assenza di transizioni inattese.
Ulteriori prove isolano due caricamenti prima di una visualizzazione,
la pulizia al reload e un display temporizzato a 0/1 ms. Il vecchio test
di rifiuto del display ritardato e sostituito dal controllo dell'attesa.
verify_staged_reference.py e evidence/staged/choices.json rendono
riproducibili i 18 riferimenti dalle risorse originali.

Questa verifica copre la selezione/visualizzazione delle varianti di
P508, non le risposte del giocatore o la risoluzione completa del puzzle.

## P508: risposte e conclusione, revisione 27

La restrizione sui comandi immediati dopo una transizione controllava
l'intero suffisso e rifiutava anche effetti raggiungibili solo in un
passaggio futuro della coda. Ora la validazione segue i collegamenti
di confronto/else/end, esplorando entrambi gli esiti possibili, e si
ferma quando raggiunge una continuazione con delay diverso da -1.
Restano rifiutati effetti immediati realmente raggiungibili prima del
ricaricamento. Il test della coda non sicura di P511 continua a passare.

Questo ammette i grafi degli script 0 e 2 di P508 e i clic degli sprite
5 e 7. La diagnosi successiva di un S9.WAV mancante era errata: mancava
la conversione dell'indice nel prototipo. L'eccezione per un file assente
introdotta nella revisione 27 e stata rimossa nella revisione 29.


clickAt richiama ora clickAtTime con il tempo corrente; i test possono
fornire un orologio deterministico senza modificare gli script. La nuova
prova carica P508, accoda tutti e tre i programmi di ingresso originali
e usa gli hit test e i clic sui pulsanti. Non forza i contatori di
risposte o la variabile di successo. Un percorso risponde correttamente
otto volte, segue animazioni e script fino a P388 e controlla globale
24=1 e un incremento del contatore. L'altro sbaglia tre volte e verifica
P388 con globale 24=0 e nessun incremento. Gli stati intermedi verificano
conteggi, sblocco input e coda esaurita; esistono limiti alle iterazioni
per evitare che un ciclo errato faccia passare il test.

La prova usa tempo simulato e SDL dummy, non input fisico o ascolto.
L'avvio Prova-enigma-P508.cmd rende disponibile la stessa configurazione
per la prova interattiva. E il primo percorso di soluzione di un enigma
verificato in questo prototipo; non e una verifica dell'intera avventura.

## Indici audio: revisione 29

La tabella di dispatch di `_read_command_mem` a 9:3528 porta opcode 9
a 9:306d (salto breve verso 9:30b0) e opcode 27 direttamente a 9:30b0.
Il lettore comune esegue `DEC EAX` a 9:30d3 e memorizza il primo argomento
decrementato. Il successivo `_playSound` riceve quindi gia l'indice del
file, non il valore serializzato. Evidenza riproducibile:
`probe_sound_index.py`, `evidence/sound-index.json`.

Il nostro ResourceReader conserva i dati grezzi. ScriptRunner converte
il primo argomento di 9/27 sia nella validazione del bersaglio sia
nell'azione emessa. Gli indici locali serializzati ammessi sono 1..900;
0 e 901 vengono rifiutati. Le chiamate interne dirette, incluso il suono
globale 912 di `_puzzle_successful`, non subiscono questa conversione.

P508: comando 9 [9] -> S8.WAV, 9 [8] -> S7.WAV, 27 [7] -> S6.WAV.
I riferimenti PCM aggiornati sono P510 S1/S2/S5 e P511 S11 per il loop.
I test controllano la conversione per entrambi gli opcode agli indici
1, 2, 9, 900, il rifiuto di 0/901, campioni e hash PCM, ripetizione
del loop, priorita del suono e i percorsi completi di P508. Compilazione
Release x64 e suite nativa superate. Nessuna prova di ascolto manuale.

## Audio automatico della scena: revisione 30

ResourceReader ora conserva flag e ID dell'introduzione, prima scartati.
Nell'originale _load_place 9:156b assegna 0 al sottofondo per il modo 0;
9:1c45-1c4b passa direttamente l'ID dell'introduzione a _playSound.
9:2f22-2fa5 attende il termine del suono nelle scene senza filmati.
La provenienza da P408 esclude l'introduzione (9:1c26). Il contatore
relativo al caricamento salvato non e ancora modellato dal prototipo.

Il ramo implementato e limitato alle scene modo 0, con entry_scripts
e audio abilitati. L'attesa aggiorna lo schermo e gestisce la chiusura;
gli input di gioco non vengono accodati durante la spiegazione. Poi
avvia gli script e applica il criterio esistente del loop: canale libero
e oltre 5000 ms per le scene degli enigmi. Non viene creato un secondo
canale musicale, assente nel comportamento originale sndPlaySound.

P508 dichiara ID diretto 302: S302.WAV e S1.WAV hanno lo stesso SHA256.
probe_entry_audio.py riproduce questa verifica e controlla le istruzioni
originali; evidence/entry-audio.json conserva riferimenti e dati PCM.
La prova nativa entry audio attraversa loadPlace con le opzioni reali,
attende tutta l'introduzione e controlla script, S0, precedenza degli
effetti, ripresa, pulizia al cambio scena e audio disabilitato.

## P511 dal primo clic alla conclusione: revisione 31

La verifica precedente della sequenza finale rimane come controllo
temporale separato. La nuova prova carica invece tutte le condizioni
originali e accoda i cinque template di ingresso. Usa clickAtTime e
spriteAt, senza scritture nelle variabili locali o nella globale 27.
Ogni interazione attraversa input, scheduler, grafi degli script e azioni.

Due ordini di soluzione raggiungono P388 con globale 27=1 e incremento
singolo del contatore; OFF raggiunge P388 senza successo. I casi intermedi
coprono quattro posizioni della Luna, vento 0..15, barometro 52..0 a passi
di 4, limiti superiori/inferiori e inversioni. Le attese hanno un limite
di iterazioni, cosi una coda bloccata fallisce la prova.

Questa revisione aggiunge l'avvio dedicato e le prove complete: non richiede
nuovi opcode. L'avvio distribuito viene eseguito separatamente con SDL
dummy fino al termine dell'introduzione, verificando cinque template
accodati senza esclusioni e la ripresa della musica S0.WAV.

## Timestamp dei template: revisione 32

Superato il rifiuto dei primi delay positivi descritto nelle revisioni
precedenti. _read_command_mem 9:340f-341b inizializza command+0x30 con
il tempo di lettura; _copy_command 15:1ad4-1adf lo copia invariato.
Opcode 41 (15:118b-11a5) accoda il template senza aggiornare tale campo.
_handle_pending 15:1b89-1b9d confronta now-timestamp con il delay.
Evidenza verificabile: probe_template_timing.py e evidence/template-timing.json.

ScriptRunner registra un'epoca comune al caricamento dei template della
scena, prima dell'introduzione, e la conserva nei primi comandi accodati
all'ingresso o richiamati da 41. Questa risoluzione per scena non riproduce
le piccole differenze temporali fra letture di singoli comandi sul PC
originale. Le continuazioni restano relative all'istante di esecuzione.

La suite controlla la soglia esatta, due richiami dopo la scadenza,
nuova epoca al ricaricamento, attesa trascorsa durante il caricamento,
wrap dell'orologio e rifiuto delle attese se la modalita temporizzata
non e abilitata. Il test nativo P509 esegue il primo programma originale,
che abilita la variabile locale 15 dopo 3500 ms; non forza tale variabile.

## Zone cliccabili e transizioni di P509: revisione 33

_do_mouse 9:12ba-1309 accoda i comandi delle zone rettangolari con la
stessa coda dei pulsanti. Ora l'opzione sprite_input abilita anche le
attese dei clic rettangolari. La modalita esploratore conserva il
sottoinsieme senza attese. La precedenza degli sprite resta invariata.

_execute_command 15:0385-0389 memorizza la destinazione e il flag di
cambio scena, poi continua nel percorso comune 15:1636. Il prototipo
esegue gia le modifiche alle variabili prima di applicare le azioni:
sono quindi sicuri dopo opcode 5 anche 32/33/39/40/46 e 41. Il richiamo
41 accoda soltanto lavoro, cancellato dal caricamento della scena nuova.
Restano respinti effetti immediati grafici o sonori che richiederebbero
un contesto di scena diverso; il test negativo P511 resta valido.

P509 ha una prova completa di selezione pulsante e clic rettangolare,
su sei bersagli e due fasi, senza assegnare lo stato risolto. La fine
raggiunge P304, globale 25=1 e un solo incremento del contatore. Tre
scelte sbagliate raggiungono P304 con globale 25=0 e nessun incremento.
La coda del suono ambientale e ciclica: la prova usa finestre temporali
limitate e controlla stato/input anziche attendere che la coda si svuoti.

## Audio sincrono locale e P505: revisione 34

_playSound 9:3bb5-3bf8 seleziona flags 2 per P505 file 2..10 e P512 file
14; negli altri casi locali ordinari seleziona flags 3. Gli ID sono gia
convertiti dal lettore del comando. probe_blocking_audio.py verifica
l'intervallo di istruzioni e registra durata/hash dei file originali.

ScriptRunner richiama un gestore sincrono per quelle eccezioni anziche
emettere l'azione audio differita. Prima vengono applicate le azioni gia
prodotte, poi si riproduce e attende la voce; il nuovo tempo restituito
include l'attesa effettiva. La continuazione immediata segue il suono,
quella ritardata parte dalla sua fine. La procedura condivisa serve anche
al suono di successo globale 912, mantenendo contatore e flag separati.

La prova della coda usa un gestore deterministico e controlla attesa,
soglia esatta, continuazione immediata e assenza di un'azione audio
aggiuntiva. La prova P505 percorre otto richieste originali e tre errori,
con audio reale decodificato sul mixer SDL dummy. Verifica globale 22 e
contatore: P520 con successo, P321 senza successo. Il filmato di P520
non viene eseguito e non e incluso nella dichiarazione di copertura.

## Video P520: sviluppo successivo alla revisione 34

Dati verificati da probe_p520_video.py ed evidence/p520-video.json.
_load_place 9:2651-266f usa P408 per il percorso del filmato di P520;
la stringa DS:03de conferma tale directory. Il comando 37 richiama
_SetMovieActiveSegment (17:05a2), che passa inizio e durata al controller.
Il comando 3 richiama _PlayMovie (17:0209), con posizione e avvio asincrono.

ScriptRunner ammette questi comandi solo con un filmato registrato e
intervalli validi. Il motore registra soltanto il contesto P520/mentors.mov,
usa il decoder QuickTime di ScummVM, converte i fotogrammi nel formato
dello schermo e aggiorna la riproduzione nel ciclo principale. I suoni
locali vengono fermati all'avvio e il loop locale non copre il filmato.
Il comando 5 temporizzato originale rimane responsabile della transizione.

La suite nativa verifica tre posizioni decodificate, collocazione, tempo
finale del segmento, soglia 43999/44000 ms per P537, salto mediante il
rettangolo originale e distruzione del decoder/coda. Le prove complete
P505/P508/P509/P511 restano superate. Il controllo separato in tempo reale
usa video SDL dummy e audio WASAPI con volume azzerato: 425 fotogrammi,
fine segmento a circa 42,5 secondi, transizione P537 a 44 secondi.
Non e una prova di ascolto o visione manuale. Il backend audio dummy su
questo host rallenta il clock audio (33,4 secondi su 44 di parete), quindi
non viene usato per certificare la sincronizzazione in tempo reale.

## P537: eredita del fotogramma e selettore

_SWCloneSprite 7:0349-0358 copia 0x9d byte dello sprite sorgente, compreso
il frame corrente. L'inizializzazione precedente selezionava il frame 0
solo negli originali e lasciava i cloni multiframe senza frame selezionato.
Il caricamento ora propaga la selezione dai sorgenti gia caricati; rifiuta
riferimenti in avanti e conserva lo stato indipendente delle copie.
La modifica si applica quando astronomica_animation e attivo.

probe_p537_selector.py rilegge MEGAFILE.HYP e controlla i 20 cloni dello
sprite 9, la condizione locale iniziale 0, i due script dei pulsanti e
i limiti 0..15. La suite nativa esegue i clic senza impostare la condizione
e verifica tutti i valori, la visibilita dell'indicatore e i due limiti.
La routine 23/14 resta esclusa: _do_custom 4:2e22-3048 imposta posizione,
velocita e callback _fxm_move_rocket_slow/rocket/rocket_fast. Richiede
ancora ricostruzione delle callback; il lancio non viene simulato.

## P537: lancio del razzo implementato

La limitazione indicata nella sezione precedente e superata. probe_rocket.py
controlla l'EXE originale, il dispatch 23/14 a 4:2e22, le impronte delle tre
callback e il flag globale 36 (game+0x9a). Il comune 23/25 non ha un caso
P537: in questo contesto resta un no-op, come nell'originale.

Riprodotte _fxm_move_rocket_slow (3:1631), _fxm_move_rocket (3:195b) e
_fxm_move_rocket_fast (3:1cd8). Le impostazioni 1..10, 11..12 e 13..15
selezionano rispettivamente le tre traiettorie. Il timer avanza un solo
passo ogni 10 ms, senza recuperare intervalli perduti. Il cambiamento della
velocita nel callback vale dal passo successivo. Coordinate e movimento
degli indicatori rispettano i rettangoli a 16 bit originali; le coordinate
GameSprite memorizzate non vengono modificate dalle callback SpriteWorld.

Le cifre 9..29 scorrono durante il lancio e assumono i fotogrammi finali
ricavati dalle tre routine. Solo la traiettoria centrale assegna successo,
a x=450; quelle errate terminano a x=500 e x=632 nascondendo il razzo.
La suite verifica tutti i 15 valori, coordinate e fotogramma finali,
intervallo 9/10 ms, overflow dell'orologio e mancato recupero dei passi.
Le prove integrate usano i clic originali per 0,1,10,11,12,13,15, verificano
l'uscita P321, il globale 36 e il conteggio: ripetere un successo non lo
aumenta di nuovo.

## P527: selezioni QuickTime e voce

probe_p527_video.py verifica FLATRING.MOV (scala 30, durata 3618 tick) e
le quattro selezioni originali: (1800,599), (2568,959), (900,899), (0,899).
La posizione e (10,10), il fotogramma e 320x240. I file sono caricati dalla
directory ordinaria della scena; P520 conserva la deviazione originale P408.
Il fotogramma decodificato viene conservato anche quando un pulsante causa
un ridisegno, e liberato insieme al decoder al cambio scena.

_playSound 9:3b1a/3bda/3c14 mette in pausa il QuickTime attivo, riproduce
il WAV sincrono e richiama _StartActiveMovie. Il motore ora sospende e
riprende il clock video intorno a questa voce. La prova dedicata controlla
che il tempo video rimanga fermo durante il suono e riprenda dopo.

Le prove P527 selezionano tutti i quattro filmati tramite clic centrali
(i rettangoli dei pulsanti si sovrappongono sui bordi), controllano le
selezioni e i bit accumulati, decodificano fotogrammi e verificano il ritorno
a P174 con globale 43. Sono verificate anche l'uscita dopo la sola seconda
selezione (successo originale) e dopo la sola prima (senza successo).
La suite usa clock accelerato e seek per P527: non certifica una visione
continua dei quattro filmati. P520 mantiene il controllo separato in tempo
reale con audio WASAPI muto. Nessuna di queste prove e una verifica manuale
dell'ascolto o della finestra del gioco.

## Arresto e occultamento degli sprite

Opcode 30, handler 15:0b2d-0bfd: imposta a -1 i periodi del movimento
e dei fotogrammi, chiama entrambi i setter SpriteWorld e nasconde lo sprite.
Non cambia il fotogramma corrente, la posizione o i timestamp. Il motore
ora riproduce questa operazione; la prova usa un comando letto da P517,
controlla entrambi i timer e rifiuta un indice fuori limite. L'aggiunta non
rende automaticamente completabili gli altri enigmi che usano il comando.


## Aggiornamento 24 settembre 2026

Opcode 19, handler 15:0827-08b8: scrive i tre campi frame a GameSprite
0xc9/0xcd/0xd1 e imposta il periodo tramite word con segno. Il sottoinsieme
ricostruito ammette periodo -1..32767, ciclo normale (1,0). Non azzera il
timestamp precedente: _SWSetSpriteFrameTime 7:09a9 cambia solo il periodo.
P517 usa sprite 9/10 con periodo 100 ms e sprite 11 con periodo 300 ms.

Opcode 30, handler 15:0b2d-0bfd: periodi movimento/frame a -1 e sprite
nascosto; conserva posizione, fotogramma e timestamp. Il test ora prende
il comando dal template originale di P517, dove e realmente memorizzato.

Opcode 21 richiama _flash_white 18:1652-1729. Riempie di bianco 640x480
sia l'immagine di lavoro del mondo (offset +8) sia il DC anteriore; poi
esegue il blit. Non sostituisce lo sfondo del mondo (+4) e non introduce
attese. Il motore aggiorna lo schermo bianco immediatamente e conserva lo
sfondo per il ridisegno successivo. Tre occorrenze in P519, nei casi errati
del Sole. Verifica nativa dei pixel bianchi e del ripristino dell'hash RGB.

Opcode 24, handler 15:0a94-0b2a: _SWMoveSprite, memorizzazione delle
coordinate complete a GameSprite +0xa5/+0xa9, _SWSetCurrentFrameIndex.
Implementato tramite due azioni consecutive (7 e 15) prima del ridisegno.
Il frame viene validato prima di ammettere lo script. Non modifica visibilita,
periodi o timestamp. Le sette occorrenze originali di P525 sullo sprite 21
forniscono coordinate e fotogrammi indipendenti per la verifica nativa.


## P525/P529 e aggiornamento completo dello schermo (24 settembre, sera)

Aggiunti i contesti video P525/FSUN.MOV e P529/FUNIV.MOV. Le durate,
scale e selezioni sono riproducibili con probe_p525_video.py e
probe_p529_video.py, direttamente dai file originali.

Opcode 49 a 15:070e chiama _UpdateGame (13:0eba), che richiama
_SWUpdateSpriteWorld (6:069d). Questo copia l'intero sfondo nel buffer
intermedio, disegna gli sprite e copia il risultato alla destinazione.
_SWStdWorldDrawProc 6:0641 usa BitBlt SRCCOPY (0xcc0020). Il fotogramma
video conservato viene quindi rimosso quando si esegue 49. Il decoder
puo disegnare il fotogramma successivo se ancora attivo. Il semplice
ridisegno incrementale dei pulsanti continua invece a conservarlo.

_load_place 9:1c51-1c8f, scene con movie count nonzero: costruisce
%s/PLACES/P%ld/S%ld.WAV usando l'ID introduttivo diretto; chiama sndPlaySound
con flags 0, quindi sincronamente. Rimossa l'esclusione delle scene con
filmati dal percorso della voce introduttiva. Verificata P529: voce
originale di 20154 ms, attesa misurata 20187 ms, handle terminato.

Comando personalizzato 25 in P529 (4:5a34-5a62): controlla game+0xbe,
chiama _puzzle_successful solo se zero, quindi imposta game+0xbe e game+0xfa
entrambi a 1. Sono global45 e global60. Il secondo viene impostato anche
se il primo era gia nonzero; non si deve ripetere suono o conteggio.
La prova dedicata controlla anche questa ripetizione e il reset delle
condizioni del runner fra scene.

P530 e diverso: 4:5a64 chiama direttamente _playSound(912), non
_puzzle_successful. Global46 viene impostato ma il contatore dei puzzle
non aumenta. Questa evidenza e in probe_p530_success.py; il caso P530
rimane escluso dal motore in attesa della sua implementazione completa.


## Sviluppo del 25 settembre: P528 e P530

P528: implementate le 48 posizioni originali della Luna e il riconoscimento
dei due tipi di eclissi, con suoni diretti S8/S9/S10. Prove tramite clic:
allineamento errato, due ordini di soluzione, ripetizione e uscita non
risolta. Successo verso P526, global44=1, contatore incrementato una volta.
P526 resta incompleto. Posizioni estratte da ASTRO.EXE dalla sonda
probe_p528_eclipses.py e confrontate con hash indipendente 0x51a72785.

P530: due soluzioni complete con tre turni senza ripetizioni, entrambi gli
ordini dei componenti, errore e uscita non risolta. Destinazione P228.
Come nel caso speciale originale, il primo successo riproduce S12 globale
e imposta global46, ma NON incrementa il contatore dei puzzle.

Compilazione e suite nativa completa passate. Dodici scene con percorsi
completi verificati automaticamente: P505, P508, P509, P511, P517, P519,
P525, P527, P528, P529, P530, P537. Unica conferma manuale: P508.
Validazione statica: 92/121 template (76.0%); non e una percentuale di
completamento del gioco. Manifesto: evidence/development-validation.json.
Nessun nuovo pacchetto, ZIP, launcher o prototipo; v34 resta invariata.


## 25 settembre: movimento originale e P521 verificati

Opcode18 implementato per rimbalzo e wrap: controllo sul rettangolo
precedente, correzione dopo il superamento, timer senza recuperare passi
saltati, coordinate memorizzate invariate. Le velocita runtime sono separate
dai parametri originali. Frame e movimento possono avanzare insieme.
Sonda probe_sprite_motion.py: dispatch originale e relocation dei callback.
Prove native dei quattro bordi, uguaglianza al bordo, timer e wrap temporale.

P521: cinque scelte attraverso clic originali, successo solo con la terza
(global37, contatore +1), dieci frammenti mobili e animati nella quinta,
arresto e ripristino, uscita verso P388. Tredici scene con percorsi completi
verificati automaticamente. Compilazione e suite integrale PASS alle 15:10.
Il movimento iniziale caricato dai file e gli altri callback personalizzati
restano da ricostruire; P501 non viene dichiarato completabile.
Il gioco intero e ancora incompleto. Nessun nuovo prototipo o pacchetto.


## 25 settembre, sera: P518 e gruppo P506/P531-P535

P518 implementato: caricamento del movimento ordinario del lanciatore,
aggancio e rilascio dei nove pianeti, rimbalzo e arresto alle soglie originali.
Due soluzioni complete (entrambe le direzioni), errore e recupero, limiti del
selettore, zero e uscita non risolta verificati attraverso clic. Suoni diretti
S9/S10, global34 e contatore verificati. Il timer runtime resta separato dal
parametro riutilizzato dal gioco. Prove aggiuntive sui bordi delle soglie e
sul cambio di velocita del lanciatore.

Custom17 implementato per P506 e P531-P535. Dopo la scena iniziale seleziona
tre varianti senza ripetizioni fra sei. La scena iniziale puo ricomparire.
Contatore e maschera sono variabili persistenti fra scene, inizializzate a
zero e azzerate al termine della sequenza originale. Successo global23,
S12 solo al primo completamento, poi sempre S22 globale sincrono e passaggio
a P519 dopo 3000 ms. La voce introduttiva e soppressa quando il contatore
e maggiore di uno. Sette percorsi di quattro scene, sei partenze diverse,
successo ripetuto e uscita normale superati nella suite nativa.

Compilazione e suite integrale PASS. Venti scene hanno percorsi completi
verificati automaticamente, non venti puzzle distinti: sei sono varianti
dello stesso gruppo. Conferma manuale solo P508. Copertura statica 98/121
(81.0%), misurata con audio abilitato e animazione disabilitata. P518 valida
3/3 template nella prova interattiva con animazione. Nessuna percentuale
globale di completamento affidabile. Nessun nuovo pacchetto o prototipo.

P526 resta da implementare: probe_p526_answers.py interpreta direttamente
588 combinazioni della logica originale e salva la tabella di accettazione.
Il movimento orbitale resta necessario prima di poterla dichiarare giocabile.


## 26 settembre 2026: P526 integrato nel motore

P526 supera le prove native del percorso completo: sei scenari senza
ripetizione, risposte corrette, successo ripetuto senza doppio conteggio,
uscita dopo quattro errori e uscita volontaria. Global42 e ritorno a P268.
Custom13 configura l'orbita e controlla la risposta sul fotogramma corrente
di sprite18, prima della condizione successiva nello stesso script.

Il movimento riproduce _fxm_eclipse e la parte di _fxm_move_ellipse usata
da P526. La conversione 1:15c3 tronca sqrt prima del rapporto dei raggi.
Sono conservati ordine dei callback, alternanza davanti/dietro, cambio
dei raggi nello scenario3 e normalizzazione del fotogramma all'arresto.
Il confronto nativo coincide con 24 traiettorie ottenute eseguendo oltre
4 milioni di istruzioni originali in probe_p526_motion.py. I timer e le
funzioni SpriteWorld esterne sono modellati nella sonda, non emulati.
probe_p526_answers.py verifica 588 combinazioni normali e 294 casi di
confine dello scenario; l'originale sceglie la tabella solo con scenario>4.
Verificati anche ordine sincrono della risposta e rifiuto fuori contesto.

Compilazione e suite completa PASS; prove e hash in
evidence/development-validation.json. Ventuno scene hanno percorsi completi
verificati automaticamente, comprese sei varianti dello stesso gruppo.
Conferma manuale ancora soltanto P508. Il dato statico resta 98/121 (81.0%)
con animazione disabilitata: non misura il completamento del gioco intero.
Nessun nuovo prototipo, launcher, ZIP o aggiornamento del pacchetto v34.

P512: nuova sonda probe_p512_weather.py esegue tutte le 24.576 combinazioni
delle tre regolazioni (0..15) per i sei scenari originali. Verifica anche
la priorita delle voci d'errore S12/S11/S10 e i sei segmenti FLATPHEN.MOV.
Custom24 e il percorso completo P512 restano da integrare; questa prova
di ricerca non incrementa il numero di scene completabili.


## Sviluppo 27 settembre: meteorologia, montaggio e aggancio orbitale

Build locale e collaudo generale PASS. Nessun nuovo pacchetto/prototipo.
P512: 24576 combinazioni originali, sei scenari, tre regolazioni,
errori/recupero, successo ripetuto, uscita non risolta; sei segmenti di
FLATPHEN.MOV verificati anche a velocita reale. Opcode36 e custom24 attivi.
Correzione della ricerca: ShowMovie AVVIA il filmato (MCActionPlay8).
P515/P536: cinque configurazioni del razzo, due fasi, misura errata e
recupero, lancio verso P510 e conteggio solo al primo successo.
I cambi scena rispettano opcode49 inline; un frame oltre la fine viene
ignorato come in SWSetCurrentFrameIndex, mantenendo immagine e stato.
P514: due traiettorie da1000 passi confrontate con x86, 17161 regioni,
224 collisioni originali, tre velocita, limiti dei controlli, aggancio,
carburante esaurito, uscita volontaria e successo senza doppio conteggio.
Custom16/3 muove sprite20 ma confronta sprite19; usa cinque punti del
rettangolo bersaglio e cancella gli altri comandi pendenti al successo.
25 scene con percorsi automatici, incluse sei varianti di uno stesso
gruppo e due scene dello stesso puzzle di montaggio. Manuale solo P508.
La copertura statica non e una percentuale di giocabilita complessiva.
P513: sole prove originali per168 confronti, nessun supporto ancora attivo.


## Sviluppo 28 settembre: fotoni e ruota zodiacale

Build locale e collaudo generale PASS. Nessun nuovo pacchetto/prototipo.
P513: custom10/0 e10/1 attivi. Confronto con126 risposte originali e
nove traiettorie; quattordici scenari, limiti1..9, sette risposte corrette,
maschera completa, dieci errori, uscita volontaria e successo ripetuto.
Custom25 incrementa solo al primo successo e non riproduce S12.
P507: custom11 usa l'ultimo clic accettato. Verificati68121 punti originali,
dodici immagini e settori, S6, annulus30..122 inclusivo, clic bloccati,
indicatore alternato e uscite P508/P388. E una scena interattiva separata.
26 scene di puzzle con percorsi automatici, oltre P507. Manuale solo P508.
Validazione statica106/121 (87.6%): non percentuale di gioco completabile.
P522: ricerca originale, non ancora abilitato. Calendario1991..2003,
un lancio fallito e cinque finestre favorevoli eseguiti dalle istruzioni
originali; prove in evidence/p522-motion.json. I tick della ricerca non
sono ancora una verifica del tempo reale o dei quattro controlli.


## Checkpoint30 settembre: P522 e P524

Compilazione e collaudo generale PASS; manifest development-validation.json.
P522: calendario1991..2003, sei tracce di lancio originali, quattro controlli,
errore/recupero, successo ripetuto, scadenza e uscita. Il delta della sonda
si applica anche senza callback; hash calendario corretto0x865b4d54.
P524: nove immagini/risposte, aiuto e ritorno dal pulsante originale P408,
stato ripristinato, tre errori, successo ripetuto e uscita. Custom28 salva
locals0..9 nei globals10..19 e ripristina solo dopo P408. Opcode51 ammette
la coda della sequenza originale, con i controlli delle transizioni opcode5.
28 scene di puzzle con percorsi automatici, piu P507 interattiva.
Non28 puzzle distinti; conferma manuale solo P508. Nessun nuovo prototipo.


## 1 ottobre: P501 custom7

Ricostruzione originale segment4:029e..0c71 e callback3:023b..06ed.
Hit strict40<distance<100; catch strict-30<distance<60 su Vesta.
Nove tracce native coincidono; 3600 transizioni hanno hash63b6a619
(stato, numero comandi, ultimo suono, callback); undici percorsi PASS.
I comandi generati hanno scadenze indipendenti. Phobos lineare5,-3;
Luna parabola/400 e rallentamento dx2->1; Vesta parabola/640, wrap
e pausa5000ms poi10ms (setter7:0ba6 scrive79 e6f).
Custom7 usa il rettangolo visualizzato1f per le finestre di input.
Terzo errore: S12, backorbi, ripresaS0, nasconde personaggi.
Il campoY del comando20 generato non e inizializzato esplicitamente
dall originale; la ricostruzione sceglie0 per il fondo completo.
Prove generali in corso; vedere NEXT-STEPS e manifest finali.


Checkpoint 1 ottobre00:11:01: compilazione e collaudo generale PASS.
P501 integrato: nove traiettorie originali,3600 transizioni,11 percorsi.
29 scene di puzzle con percorsi automatici, oltre P507 interattiva.
Non29 puzzle distinti; conferma manuale soloP508. Percentuale globale
non determinata. Prossimo gruppoP502-P504, poiP516/P510/P523.


## Comet movement checkpoint, 1 October 2026

P502/P503/P504 movement implemented in sprites.cpp; all30 original
trajectory hashes match the native build. Original setup research covers
1920 cases, and both original probes reproduce their saved evidence exactly.
Full native suite PASS after the movement addition. Scene dispatch and
two-layer integration remain disabled and untested as interactive routes.
See COMET-RESEARCH.md for exact behavior, limitations and integration steps.
This does not increase the29 verified route scenes or establish a whole-game
completion percentage. No new package, prototype or launcher was created.


## Integrated comet puzzles, 1 October 2026

P502/P503/P504 are integrated in the ScummVM engine. Full suite PASS.
Native checks:30 original trajectories,1920 setup/display states,9 independent
layer/clone/clipping compositions, complete P502-P503-P504-P527 chain,
repeated victory, low/high speed, wrong direction and voluntary exits.
The checkpoint now includes32 route scenes, not32 independent puzzles.
Manual confirmation remains limited toP508. Whole-game percentage is unknown.
P516 research covers128 setup and64 collision cases; P516 is not enabled.
See COMET-RESEARCH.md, P516-RESEARCH.md and NEXT-STEPS.md for limitations.
No prototype, package or launcher was created.


## Integrated P516 checkpoint, 1 October 2026

P516 is integrated in the native ScummVM engine. Full regression suite PASS.
Native verification:128 original setup configurations,20 seconds of eight
original orbit trajectories,64 collision fixtures plus four API edge cases,
three independent image compositions and79/80ms frame timing on both layers.
Actual click routes cover victory/repeat, zero-speed and missed launches,
and voluntary exits. Total33 verified route scenes; these are not33 distinct
puzzles. Whole-game completion percentage remains unknown. Manual P516
audiovisual verification and help/return remain pending. No prototype,
package or launcher was created. See P516-RESEARCH.md for proof boundaries.


## Integrated P510 checkpoint, 2 October 2026

P510 now runs the original movie-controlled puzzle in the native engine.
Full regression suite PASS;34 route scenes, not34 independent puzzles.
Original callback comparison432 cases; eight click routes cover three starts,
both directions, first/repeated victory, failure, voluntary exit and timeout.
A complete winning movie route also passed continuous playback without seeks.
P516 remains integrated and verified. Manual confirmation remains limited to
P508; whole-game completion percentage is unknown. See P510-RESEARCH.md.
No prototype, package or launcher was created.


## Integrated P523 checkpoint, 3 October 2026

Native P523 and full regression suite PASS.35 route scenes, not35 distinct
puzzles. Controls:5899 reachable states/35394 transitions. Callback comparison:
262656 cases, with the explicit malformed event8 call repair documented below.
Positions:100 exact x87 cases. Ten click routes include first/repeated victory,
five failures, simultaneous response flags, exit and opening help. A complete
winning movie route passed without seeks and with real input delays.
Manual audiovisual review, help return, saves and whole-game playthrough remain.

Original4:7a87-7a9f passes two WORDs to a two-DWORD movie-range function,
producing start5246601 and an uninitialized duration. The native engine uses
the explicit original WORD values3721/80 for this failure clip. This is a
documented compatibility repair, not literal emulation of undefined stack data.
The original probes now label that duration unknown; normalized native
reference hash:f8ea0405. Control hash:40e80615; position hash:742cfb9d.
P523 also needs the full movie duration before startup custom5 selects a range.


## Mentor help checkpoint, 4 October 2026

P408 mentor buttons now play their original contextual video ranges. Native
comparison passes1900 cases, with explicit no-hint handling for undefined
P524 variant0/9.170 decoded selections,37 source-scene returns, no-hint speech
and natural continuous segment completion pass, together with the full suite.
P523 help return resets modified controls and response flags and reinstalls
the movie callbacks; original input still works after returning.
The Windows help book (custom22), native saves and manual audiovisual review
remain incomplete.35 puzzle-route scenes remain verified, not35 distinct
puzzles; no whole-game completion percentage is asserted.


## Exploration saves checkpoint, 4 October 2026

Native saves now preserve exploration location, completed-puzzle counter and
100 globals. F5 opens the standard ScummVM menu. Startup loading, slot listing,
metadata and menu opening/closing pass.840 truncated/corrupted payload checks
pass; unsupported destinations do not change the active game. Video and script
time pause in the menu. The full regression suite passes with these changes.
Saves are currently limited to settled mode1 exploration screens. No original
gamestat import or arbitrary mid-puzzle restoration is claimed. See
SAVE-RESEARCH.md.35 puzzle-route scenes remain verified; whole-game completion
is not measured. Windows help book and manual audiovisual playthrough remain.


## Scene progression checkpoint, 4 October 2026

Original transition rules are integrated: nine directed world gates, consumed
permit, puzzle-entry prerequisite, and global denial/unsolved-exit voices.
47,520 original instruction cases and native comparison pass. P429's five
denial movie segments, P427, P426/P428 timed exits and seven P425 credit images
are tested. The complete native regression suite passes. See
PROGRESSION-RESEARCH.md. This does not establish a complete game route:
custom26 inventory/state transfers remain unimplemented. Independent original
research now covers2436 custom26 cases and42 resume/memory boundaries.
The35 verified puzzle-route scenes and manual confirmation scope are unchanged.


## Game-wide state checkpoint, 4 October 2026

Custom26 is integrated and matches2436 original instruction cases plus42
resume/memory boundaries. Cabinet/item persistence, world-door flag, live
completion count, hub indicators, credit bookkeeping and the P407/P422
keypad sequences pass native checks. Global voices and zero-layer exploration
images now support those original scripts. Full regression passes. See
GAME-STATE-RESEARCH.md for explicit legacy resume/memory adaptations.
P409 custom27 research covers34800 cases; it is not integrated yet. No new
whole-game percentage or manual completion is claimed.


## Advice checkpoint, 5 October 2026

P409 custom27/32 and world countdown are integrated and verified against
34800/108/10530 original cases. Native interaction, seven warning sounds,
expiry and continuous advice playback pass. Saves now use version2 (424
byte prefix) with clock epoch; inactive version1 remains readable. See
P409-RESEARCH.md. Four ending routes423/424/435..437 now play five movies and reach credits.
Full suite PASS; no global completion percentage claimed.


## Intro and logo checkpoint, 10 October 2026

The new-game click, P2/P4 movies and nine P3 cards now reach exploration27.
P4 reads its movie fromP2 as the original loader specifies. Opcode50's
Win16 display palette is adapted to native RGB rendering: both original
Cinepak video descriptions are24-bit. Its original OPEN2_B must decode,
the movie and screen must be RGB, and other contexts/names fail closed.
Logo0 handles state61=0/2 returning to menu and1 quitting after20000ms.
Quit accepts trailing condition closures only; following effects still fail.
P432/P433 moving text, stops, movie frames and continuous playback pass.
The prior full-suite failure was P423 reaching19.475s of video at the26s
wall deadline. The test now allows50s but still requires natural completion;
new diagnostics record wall/media/end times. Full regression PASS.
Intro continuous playback and manual audiovisual review remain unverified.
Evidence:probe_intro_logo.py, intro-logo-original.json and runtime logs.


Real-time introduction, 10 October 2026: PASS in the normal native main loop, with entry scripts and audio enabled, headless. P2 -> P3 -> P4 -> P27 completed without accelerated time. This verifies scene progression only. P2 media reached only about156s at the208s scene deadline, closing while playing. Investigate headless clock/performance; audiovisual continuity is NOT validated. Manual audiovisual review remains pending.


## P29 and audio clock, 11 October 2026

P29 original FLAT29.MOV integrated with both control orders, repeat-control guards, four decoded positions, redraw at65000ms, cursor release and delayed input unlock. Custom29 rebuilds background/sprites without stopping the movie. Original evidence in probe_world_interactions.py includes final display callback and cursor flag consumer. Native cursor movement is constrained below the movie; manual pointer review remains pending. World scenes82/222/231 remain unsupported.
The Oct10 intro timing discrepancy was reproduced in SDL dummy without game/video: 9.6595 audio seconds in12 wall seconds. On Windows WASAPI, P2 ends naturally before the208s transition and P4 advances69.994s at the70s transition. No production movie clock change was required. Real-audio intro proof retains its exact pre-P29 executable hash; the subsequent full native regression uses WASAPI and passes on the new build. Manual audiovisual review and full-game completion remain unverified.


## World movies82/222/231, 11 October 2026

Original MOV files now play in world panels82,222,231. Controller replay is scoped to supported world movies: completed playback seeks to0 before play; in-range playback preserves position. Original QCMC control-flow research executes762 boundary cases. Native tests cover arm toggles, unarmed rejection, four decoded positions, input/cursor release deadlines, P222 replay and in-range resume, P222 two-second sprite animation and exit407. Continuous native playback passes for29/82/222/231 with WASAPI. Complete native regression PASS. No extra puzzle completion count is claimed. Manual audiovisual/pointer review and a complete game playthrough remain pending.


## Hover checkpoint, 11 October 2026

Native hover now handles32 original paired targets in P1/P505/P519/P526. All targets, four P505 sounds, stationary suppression, original overlap order, conditional branches, click-lock independence and scene resets pass.256 native dispatch cases agree with the original dispatch study. Build and full WASAPI regression PASS. Help file research decodes1701 phrases and2117 records with exact length checks;782 titles match the independent index. Native help UI remains unimplemented. Custom33 reads text gamestat, distinct from the binary routine studied earlier. See HOVER-RESEARCH.md and HELP-RESEARCH.md. No manual audiovisual or complete-playthrough claim is made.


## Native help reading view, 12 October 2026

The original HLP is read directly by the engine.781 articles and812 keywords are accessible from the original P1/P408 help controls. Search, modal return, pause, corrupt/truncated data and scoped command validation pass. All2117 decoded records match independent FNV2cab83c0. Actual GUI captures of the index and an article were inspected. Build and full WASAPI regression PASS. This is a reading view:31 inline images, original styles/symbol fonts and inline hyperlinks remain pending. No manual game-playthrough claim. See HELP-RESEARCH.md and help-native-validation.json.


## Native help images and basic formatting, 12 October 2026

All31 original bitmap palettes/pixels and their associations with20 articles are checked against independent file research. The native Images button opens article pictures with previous/next navigation.41 image corruption cases reject bad data while preserving the loaded book. All1335 body records and11455 formatting commands match semantic FNVb5265663;304 table rows are decoded. Basic bold/italic, paragraphs and table cells are rendered. All781 articles opened in the production renderer without failure; targeted GUI captures and full WASAPI regression PASS. Exact typography, symbol fonts, underline/strikeout, original measurements and inline image positions remain pending. All body commands were inspected: there are no inline hyperlink opcodes in this original file; See references are text. This corrects the earlier pending-hyperlink assumption. No manual complete game-playthrough claim. See help-native-validation.json.


## Original text GAMESTAT import, 13 October 2026

The native engine reads gamestat/GAMESTAT from the selected game directory without modifying it. It validates all102 signed decimal values and the destination before enabling the original P1 saved-game choice. Custom33 restores the exploration scene, completed count and100 globals. Imported games can then use ordinary ScummVM saves. Original drive-root/current-directory fallbacks are not searched. The decoded snapshot stays stable during the menu interaction. Binary gamestat belongs to another original routine and is not imported.

Active countdown modes1/2 with nonzero global8 remain rejected. The original text writer stores the timestamp, not the current epoch or elapsed time. Two original countdown executions with the same saved timestamp produce different results at different current clocks; see legacy-resume-original.json. No timestamp is guessed from file dates and no countdown is reset. Only mode1 exploration destinations are admitted; arbitrary puzzle state cannot be reconstructed from the global-only file.

Build,15 original payload comparisons,102 token-boundary truncations, signed bounds, malformed/oversized inputs, file discovery, missing/invalid files, atomic rejection, original menu clicks, native resave, native slot startup, all781 help article openings and full WASAPI regression PASS. The fixture original file is unchanged. Syntactically valid altered numbers cannot be recognized as corruption because the original format has no checksum. No manual full-game completion claim.

Future puzzle saves: probe_puzzle_save_requirements.py inventories the 35 verified route resources, including local conditions, sprite frames/clones, automatic motion, movie references, script delays and custom handlers. Uninterpreted resource tails are hashed separately; they are not discarded or claimed decoded. This is a static inventory, not a save implementation. A scene reload plus globals cannot restore mutable sprite state, local conditions, pending work or per-puzzle/random state. Continuation tests must compare uninterrupted and restored runs at intermediate states. See evidence/puzzle-save-requirements.json.


## Inline help pictures, 13 October 2026

All 31 pictures now appear between the original text runs in 20 articles. Anchors come from decoded bitmap commands, not caption matching. All are in paragraph records, none in tables. Rendering combines the existing Markdown text with decoded original pixels in one scrolling article; pictures shrink only for narrow viewports and retain their aspect ratio. No generated image archive or filesystem cache is needed. The separate Images view is still available. Exact WinHelp spacing is not claimed.

The production GUI opened all 781 articles. Pixel checks cover all 31 inline pictures, scrolling to both ends, wheel and drag, narrow width, height-only resize and restored dimensions. Andromeda, Jupiter and Moon captures were visually inspected. Native save/import regressions and the full WASAPI suite passed on the matching executable.

probe_help_inline.py also inventories every nonempty font run. No Symbol font is used; descriptors with flags 4 and 33 have no nonempty text runs. Earlier generic pending Symbol/underline items were not demonstrated by the original contents. Arial Super occurs in 13 runs, 21 characters, including Kepler and relativity exponents. These now use explicit ^(exponent) notation instead of misleading baseline digits. All 13 original runs and both formulas are checked; no new scientific values or corrections are added. Kepler article rendering was visually inspected. Raised glyph typography remains an adaptation, not a pixel-identical font recreation. See help-inline-original.json.
