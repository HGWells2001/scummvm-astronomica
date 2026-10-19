# Astronomica � ripartenza dai file originali

Stato verificato: 19 ottobre 2026. Motore ScummVM nativo in sviluppo; build locale e suite completa WASAPI PASS.

Avvio corrente: aprire **Avvia-Astronomica.cmd nella radice del workspace**. Usa la build reale attuale, parte dal menu P1 e attiva audio, animazioni e interazione. Preferenze e salvataggi personali sono in userdata/astronomica, separati dalle prove. Il vecchio collegamento bin/Avvia-Astronomica.cmd rimanda allo stesso avvio. Vedere LOCAL-PLAY.md.

Sono verificati automaticamente percorsi in 35 scene di puzzle, oltre a navigazione, filmati, audio, aiuto e salvataggi di esplorazione. L'aiuto legge 781 articoli e 31 immagini originali fra testo e didascalie. I 13 esponenti originali sono resi con notazione ^(valore).

Salvataggi nativi verificati in esplorazione e in P505, P508, P519, P524, P526, P528, P530. Import GAMESTAT originale disponibile per esplorazione con countdown inattivo. Restano altri salvataggi, fedelta tipografica e verifica audiovisiva manuale integrale. Nessuna percentuale globale attendibile; 94.2% misura solo 114/121 template statici, non la giocabilita.

Usare NEXT-STEPS.md per riprendere e verify_development_evidence.py per verificare il checkpoint. Eseguibile corrente: work/fresh-20260913/build/Releasex64/scummvm.exe. L'avvio richiede la build locale e i file originali D:/astro; non e un nuovo pacchetto distribuibile.

Questo lavoro e stato ricostruito da D:/astro, senza consultare codice, rapporti o conclusioni dei tentativi precedenti esclusi dall'utente. Il nome della cartella indica questa ripartenza; non e una certificazione legale di processo clean room.

## Registro storico delle funzionalita (settembre)

- Un eseguibile Windows x64 di ScummVM con il nuovo modulo sperimentale `astronomica`.
- Riconoscimento della copia originale tramite impronte di `GAMEDATA` e `ASTRO.EXE`.
- Esploratore degli sfondi e dei pannelli originali, con navigazione da tastiera.
- Lettore C++ delle strutture di scene, sprite, aree cliccabili, condizioni e comandi.
- Primo interprete con coda dei comandi e collegamenti cliccabili semplici nelle scene senza sprite.
- Condizioni: confronti, assegnazioni, incrementi e diramazioni; caricamento dello stato locale dai file originali.
- Inizializzazione dei 100 valori globali, persistenza tra scene e azzeramento entrando in P1.
- Avvio sperimentale degli script di ingresso riconosciuti, attivabile nella configurazione.
- Visualizzazione degli sprite statici visibili, con maschere originali, nelle scene a un livello; inclusi i cloni con sorgente a un fotogramma.
- Comandi originali per mostrare e nascondere gli sprite supportati, con ripristino dello sfondo e ridisegno.
- Posizionamento degli sprite supportati tramite il comando originale 7, verificato su P517.
- Spostamenti relativi tramite il comando originale 47, con accumulo verificato su P510.
- Selezione esplicita dei fotogrammi tramite l'opcode 15, inclusa la selezione indipendente nei cloni.
- Timer in millisecondi e richiami accodati degli script: lampeggio automatico completo di P29.
- Clic sperimentali sugli sprite con geometria verificata, precedenza originale e blocco temporizzato degli input.
- Prima animazione automatica dei fotogrammi e pressione/rilascio dei pulsanti di tipo 2, verificati su P510.
- Riproduzione dei suoni PCM locali tramite ScummVM, associata ai clic originali dei pulsanti P510.
- Uscite originali di P510 verso P136 e P408, con suono, ritardo e pulizia delle continuazioni.
- Attivazione e disattivazione di singoli bit delle condizioni globali/locali tramite opcode 33, verificata sui comandi originali di P511.
- Generatore casuale originale e scelta in un intervallo (opcode 40), verificati sulle varianti di P510.
- Scelta casuale senza ripetizioni tramite opcode 39, con verifica delle otto varianti originali di P505.
- Arresto del suono tramite opcode 10, compresi comandi temporizzati e ripetuti.
- Sottofondo PCM locale ripetuto: scelta, sospensione e riattivazione tramite comandi 27, 25 e 26, con precedenza agli altri suoni.
- Intervalli di animazione modificabili tramite opcode 48: quattro comandi originali di P511 verificati, con confronto indipendente dei quattro fotogrammi.
- Prima operazione personalizzata di completamento P511: suono sincrono, variabile globale 27 e conteggio senza duplicati.
- Sequenza finale originale completa di P511 verificata: otto posizioni, attesa del suono e transizione a P388, partendo dallo stato risolto impostato dal test.
- Lettore Python indipendente, estrattore dei simboli originali, inventario SHA-256 e verifiche.

**Non è ancora il supporto giocabile del gioco.** L'interprete riconosce un sottoinsieme di 30 opcode (1, 2, 5, 6, 7, 9, 10, 15, 16, 17, 20, 23, 25, 26, 27, 28, 29, 31, 32, 33, 39, 40, 41, 42, 45, 46, 47, 48, 49 e 51), con ulteriori limiti descritti in `INTERPRETER.md`. Restano da completare animazione automatica, composizione su più livelli, interazione con gli sprite, enigmi, filmati, audio completo, inventario e salvataggi. Gli sprite con più fotogrammi vengono disegnati solo dopo una selezione esplicita del fotogramma. L'esecuzione degli script di ingresso è parziale e disattivata nell'esploratore normale. La barra in basso identifica sempre la modalità di esplorazione sperimentale.

Le revisioni 16�18 estendono la logica interna degli enigmi; non aggiungono una
nuova prova interattiva n� rendono completabili P510/P511. Gli avvii gi� disponibili
restano validi. La nuova verifica automatica usa le istruzioni originali
per controllare che un singolo indicatore cambi senza alterare gli altri.

## Avvio del prototipo

Aprire `bin/Avvia-Astronomica.cmd`. La configurazione punta a `D:\astro`.
L'avviso di ScummVM sul supporto incompleto è previsto: il modulo è marcato `ADGF_UNSTABLE`.

- Pagina giù / Pagina su: scena successiva / precedente disponibile.
- Frecce sinistra, su e destra: collegamenti di navigazione dichiarati nella scena.
- Clic sinistro: sequenze semplici riconosciute nelle aree delle scene prive di sprite.
- Esc: uscita.

Per provare direttamente il nuovo collegamento, aprire `bin/Prova-collegamento.cmd`: parte da P103. Cliccare nell'area x=311–551, y=61–154 per passare a P126. Le sequenze non supportate vengono ignorate con una segnalazione nel log.

`bin/Prova-script.cmd` apre P505 con l'avvio sperimentale degli script abilitato. Il log `bin/astronomica.log` riporta le sequenze accodate e quelle escluse; non rappresenta ancora l'avvio completo dell'enigma. Questa modalità corrisponde a `astronomica_entry_scripts=true` nella configurazione.

`bin/Prova-sprite.cmd` apre P29: il display del videoregistratore è ora composto sullo sfondo usando lo sprite e la maschera originali. `P29-static-reference.png` è il riferimento indipendente prodotto con Pillow, non una cattura dello ScummVM in esecuzione.

In P29 premere **V** per nascondere o mostrare il display del videoregistratore. Questa prova esegue singole istruzioni estratte dalla sequenza originale della scena; resta una prova manuale. Per il lampeggio automatico usare il nuovo avvio descritto sotto.

`bin/Prova-movimento.cmd` apre P517. Premere **M** per spostare lo sprite 7 dalla posizione (447,361) a (477,361) e viceversa, eseguendo le due istruzioni originali. È una prova del posizionamento, non l'esecuzione dell'enigma completo.

`bin/Prova-spostamento-relativo.cmd` apre P510. Ogni pressione di **M** esegue l'istruzione originale che sposta lo sprite 8 di un pixel verso il basso; **R** ricarica la scena per ripartire. Anche questa è una prova diagnostica, non l'enigma completo.

Dalla revisione 9 P510 mostra anche il clone, sprite 9. **C** sposta soltanto il clone; **M** continua a spostare soltanto la sorgente. I due condividono l'immagine, ma hanno posizioni indipendenti.

`bin/Prova-fotogrammi.cmd` apre P510: **F** alterna i fotogrammi 0 e 1 dello sprite 10 usando singole istruzioni originali. Non è ancora l'animazione o l'interazione completa dell'enigma.

`bin/Prova-lampeggio.cmd` apre P29 con il suo unico script di ingresso originale completo. Il display lampeggia automaticamente con il ritardo dichiarato di 600 ms, oltre ai passaggi della coda. Non serve premere V. La verifica controlla i limiti 599/600 e 1199/1200 ms e confronta i pixel degli stati acceso/spento con i riferimenti indipendenti. I pulsanti TV/VCR della scena richiedono altri comandi e non sono ancora utilizzabili.

`bin/Prova-pulsanti.cmd` apre P510 con i clic sugli oggetti abilitati.
Cliccare il pulsante vicino a **(240,397)**, poi quello vicino a **(266,376)**:
le sequenze originali selezionano il pulsante, deselezionano gli altri quattro
e aggiornano la variabile della scena. Per 150 ms dopo l'aggiornamento lo
script blocca nuovi clic. Non serve premere F. Gli altri comandi dell'enigma
possono essere rifiutati; questa prova non rende l'enigma completabile.
L'opzione corrispondente � `astronomica_sprite_input=true`; resta disattivata
nell'esploratore normale. Nessun evento di trascinamento � implementato.

`bin/Prova-animazione.cmd` apre P510 con il primo fotogramma degli oggetti
e l'animazione sperimentale abilitati. Cliccare il pulsante vicino a
**(130,400)**: appare l'indicatore a (50,100), che alterna due fotogrammi
ogni 400 ms. Il pulsante torna al fotogramma di riposo dopo 500 ms;
l'indicatore viene nascosto dopo la pausa di 10 secondi successiva allo
sblocco dei clic. Funzionano anche i pulsanti di selezione gi� verificati.
Le altre funzioni dell'enigma rimangono incomplete. La modalit� usa
`astronomica_animation=true` e `astronomica_sprite_input=true`.

`bin/Prova-audio.cmd` apre P510 con immagini iniziali, animazioni, mouse
e suoni locali abilitati. Il pulsante vicino a **(35,380)** riproduce S2;
quello vicino a **(600,380)** riproduce S5 e poi S1 secondo i ritardi
dello script originale. Ogni nuovo suono sostituisce il precedente.
Funzionano anche le prove di selezione e dell'indicatore animato.
L'enigma resta incompleto: alcuni pulsanti e le sequenze d'ingresso
contengono ancora comandi non implementati. L'opzione audio �
`astronomica_audio=true`; non � attiva negli avvii precedenti.

`bin/Prova-uscite.cmd` apre P510 con audio, animazioni e mouse.
Cliccare vicino a **(35,430)** per la sequenza originale che riproduce S4
e porta a P136 dopo 500 ms. Il pulsante vicino a **(600,430)** riproduce S5
e porta a P408 dopo 700 ms. Riavviare la prova per verificare l'altra uscita.
I ritardi decorrono dai rispettivi passaggi della coda. L'arrivo mostra
le risorse della destinazione; non significa che il suo comportamento
completo o l'enigma P510 siano implementati.

Il prototipo parte da P1. Le scene speciali che cambiano sfondo con comandi possono apparire nere o incomplete. Questo è atteso finché non viene implementato l'interprete. P406 viene rifiutata perché il file originale è troncato.

La build minimale può segnalare un carattere mancante per il tema dell'interfaccia e usare il fallback. Il test del modulo e il rendering degli sfondi terminano comunque correttamente. La prova di esecuzione effettuata usa il backend SDL dummy, non un confronto interattivo con il gioco originale.

## Verifiche eseguite

| Controllo | Risultato |
|---|---:|
| File originali inventariati | 1.606 |
| Dimensione complessiva | 422.477.593 byte |
| MEGAFILE.HYP | 421 |
| PLACEDEF testuali originali | 97 |
| Lettura rigorosa Python fino all'ultimo byte | 416/421 |
| Strutture leggibili conservando i residui separati | 420/421 |
| Bitmap incorporate decodificate anche con Pillow | 3.625 |
| Comandi decodificati | 10.316 |
| Layout opcode nel lettore originale | 49 |
| Record di simboli estratti dall'eseguibile originale | 3.686 |
| ScummVM: scene lette e sfondi disegnati nel test | 420 |
| Compilazione completa Visual Studio x64 | riuscita |
| Uscita del test ScummVM | codice 0 |
| Interprete: coda, ritardi, rollover, rifiuto atomico, annullamento e FIFO | superati |
| Clic sui dati originali P103 → P126 | superato nel test SDL dummy |
| Confronti: 64 combinazioni di operatori, scope e valori | superate |
| Script originali P505 (vero/falso) e P530 (azzeramento) | superati nel test SDL dummy |
| 100 valori globali, persistenza e azzeramento entrando in P1 | superati |
| Due script originali di P505 accodati senza esecuzione anticipata | superati |
| P29: pixel RGB confrontati con composizione indipendente Pillow | superati nel backend SDL dummy RGB565 a 16 bit |
| Maschera trasparente/opaca, ritaglio ai bordi, rifiuto atomico di maschere non binarie | superati |
| Comandi originali P29: nascondi/mostra, ripristino pixel dello sfondo e rifiuto di identificatori non validi | superati |
| P517: spostamento e ritorno, confronto pixel con riferimenti indipendenti | superati nel backend SDL dummy RGB565 |
| Coordinate: caso speciale (0,0) e conversione originale a 16 bit | superati |
| P510: sorgente e clone indipendenti, cinque riferimenti pixel e ordine dei comandi in coda | superati |
| Catene di cloni; rifiuto di riferimenti a se stessi, in avanti o non validi | superati |
| P510: fotogrammi 0/1/0, confronto RGB e rifiuto di indici non validi | superati |

I conteggi C++ e Python coincidono. I quattro test Python includono tutte le 2.944 troncature possibili del file P0, il confronto della bitmap incorporata con BLACK_B originale e la sequenza di comandi del logo confrontata con il PLACEDEF.

## Anomalie aperte

| Scena | Evidenza |
|---|---|
| P406 | File di 24 byte: la lettura si interrompe all'offset 0x18. |
| P502 | Struttura termina a 0x8f2cf; restano 83.184 byte. |
| P503 | Struttura termina a 0x96b5f; restano 165.284 byte. |
| P504 | Struttura termina a 0xa04d3; restano 148.864 byte. |
| P533 | Struttura termina a 0x86223; restano 12.288 byte. |

I residui non sono tutti zero. La loro origine resta da determinare; non vengono dichiarati dati inutili. Il lettore Python rigoroso li segnala come errore, quello C++ li conserva nel conteggio `trailing`.

## Riproduzione tecnica

Con Python 3.12:

```text
python astro_reader.py D:\astro --out decoded
python test_original_data.py
python -m pip install capstone==5.0.9
python extract_debug.py D:\astro\SETUP\ASTRO.EXE --out debug
python probe_interpreter.py D:\astro\SETUP\ASTRO.EXE --out interpreter
python analyze_conditions.py D:\astro --out condition-analysis.json
python verify_sprite_reference.py D:\astro --out P29-static-reference.png
python verify_move_reference.py D:\astro --out movement
python verify_offset_reference.py D:\astro --out offset
python verify_frame_reference.py D:\astro --out frames
```

L'estrattore di debug rifiuta varianti diverse dall'impronta SHA-256 verificata. Il lettore del gioco non dipende da Capstone.

Per ScummVM applicare `astronomica-engine.patch` alla revisione ufficiale `2085bcb368c19bc90f0190efcd56b9d58cd7fb5a`, oppure copiare la directory `engine/astronomica` in `engines/astronomica`, quindi abilitare l'engine `astronomica`. Il modulo non è abilitato di default.

La build fornita usa Visual Studio 2026, v145, Release x64 e SDL 2.32.6. Provenienza e impronte sono in `build-provenance.json`. I log di compilazione ed esecuzione sono nella directory `evidence`.

## Prossimo sviluppo

1. Completare gli opcode necessari agli script di ingresso e la conversione dei tempi originali. La nuova analisi ha stabilito che i valori globali partono da zero, anziché essere inizializzati da GAMEDATA.
2. Collegare sprite, maschere, eventi mouse e navigazione al nuovo interprete.
3. Implementare audio e QuickTime, verificando codec e sincronizzazione sui file effettivi.
4. Ricostruire le azioni specifiche `_do_custom` e le routine degli enigmi.
5. Stato persistente, salvataggi e confronto sistematico con l'eseguibile originale.

Non viene inventato un comportamento per gli opcode ancora non interpretati.



La revisione 19 aggiunge l'arresto audio agli script. La verifica automatica
usa il comando originale temporizzato di P501 su un suono lungo di P510,
senza modificare i file originali. Non aggiunge un nuovo enigma completabile;
gli avvii interattivi esistenti restano disponibili.

## Revisione 20

Il comando 48 cambia l'intervallo dei fotogrammi senza cambiare subito
l'immagine visibile o il timer. Le quattro istruzioni originali di P511
sono verificate a intervalli di 500 ms; le immagini coincidono con un
riferimento indipendente ricostruito dai bitmap originali. Build e suite
nativa superate. Questa verifica isola le istruzioni: l'enigma P511 completo
non e ancora giocabile e non viene aggiunto un nuovo avvio interattivo.

## Revisione 21

Aggiunta la gestione esplicita del sottofondo locale. I test isolano i
comandi originali di P511 e P509, verificano la ripetizione dei campioni
di S12.WAV, il limite 5000/5001 ms e la precedenza del suono principale.
L'audio rimane facoltativo. Non sono ancora ricostruite la selezione
implicita dei sottofondi globali o la convivenza con i filmati.
Il progresso stimato rimane circa 43%: questo passaggio non rende ancora
completabile un nuovo enigma. P511 richiede anche la logica personalizzata
di successo, immagini aggiuntive e altre interazioni.

## Revisione 22

Implementata l'operazione personalizzata 25 dell'opcode 23, limitatamente
a P511 e con audio abilitato. Il suono globale SOUNDS/S12.WAV termina
prima dell'aggiornamento del risultato e della continuazione dei comandi.
Le prove verificano esecuzione singola, ripetizione, flag gia non nullo,
ritardi successivi, persistenza fra scene e azzeramento entrando in P1.

La prova esegue il comando originale isolatamente: non costituisce una
soluzione giocabile dell'enigma. Il grafo completo P511 resta escluso,
fra l'altro per il cambio scena seguito da una diramazione immediata
e per i comandi delle immagini. Non viene aggiunto un nuovo avvio.

## Revisione 23

Superata la verifica dell'intero script 0 originale di P511 (21 comandi),
con stato iniziale di enigma risolto impostato dal test. La sequenza esegue
le otto posizioni, attende il suono di successo e passa a P388. Verificato
anche il ramo non risolto, che sblocca i clic dopo 75 ms senza uscire.

Corretto inoltre un accesso oltre la fine dello script quando una
diramazione salta direttamente al termine. Ora sono ammesse le
transizioni seguite soltanto da controllo immediato del flusso;
gli effetti immediati sulla vecchia scena restano esclusi.

Il progresso stimato e circa 45%, senza equivalenza con la parte di gioco
completabile. Non e ancora possibile risolvere tutto P511 giocando: restano
le immagini aggiuntive e altre interazioni. Non sono aggiunti avvii di
soluzione automatica; questa e una verifica di sviluppo.

## Revisione 24: ricognizione degli altri enigmi

Il rapporto PUZZLE-SURVEY.md copre 37 scene P501-P537, comprese varianti.
Elenca comandi mancanti, operazioni personalizzate, livelli e gestori di
trascinamento. I comandi immagini 20/49 compaiono in 18 scene ciascuno:
sono una priorita condivisa per il prossimo sviluppo.

La registrazione del successo e stata estesa a 29 scene verificate
nell'eseguibile originale, inclusi P501, P505, P510, P517 e P525.
Sono 29 associazioni scena/variabile, non 29 enigmi resi giocabili.
P506 e P531-P535 condividono la variabile globale 23. P513, P529 e P530
sono esclusi perche hanno effetti diversi. Test e compilazione passano,
compresa una prova del comando originale di successo del pulsante P517.

## Revisione 25: immagini aggiuntive

Implementata la coppia di comandi 20/49 quando il caricamento e seguito
immediatamente dalla visualizzazione. Il bitmap originale viene copiato
sullo sfondo, poi gli sprite vengono ridisegnati. Sono verificate sei
coppie originali di P505, P509 e P511 contro immagini indipendenti.

Il supporto richiede una scena a un livello e un bitmap decodificabile;
le immagini esterne monocromatiche e i comandi separati da attese o
diramazioni restano esclusi. P508 usa proprio una di queste forme.
Nessun nuovo enigma viene dichiarato completabile: il rapporto degli
script viene aggiornato usando la nuova build.

## Revisione 26: immagini attraverso diramazioni e attese

Il caricamento di un'immagine non la disegna piu immediatamente: il
bitmap rimane in attesa fino al comando 49. Questo supera la restrizione
delle coppie consecutive della revisione 25. Un secondo caricamento
sostituisce l'immagine in attesa; il cambio scena la elimina.

Verificato lo script 1 originale completo di P508 per tutte le 18
varianti, con confronto dei pixel e controllo che nessuna immagine
compaia anticipatamente. Non e ancora una prova di soluzione dell'enigma:
le altre sequenze e interazioni possono restare incomplete.

## Revisione 27: prova dell'enigma P508

Aprire bin/Prova-enigma-P508.cmd. Viene avviato Astronomy vs Astrology
con immagini, animazione, audio disponibile, clic e script originali.
Leggere la frase nel pannello inferiore e scegliere ASTRONOMY oppure
ASTROLOGY. Otto risposte corrette completano la sequenza; tre errori
fanno uscire senza successo. Per ricominciare riaprire questo avvio.

Entrambi i percorsi sono verificati automaticamente tramite gli stessi
metodi di input e temporizzazione usati dal gioco, senza impostare lo
stato risolto. La prova non sostituisce un controllo manuale nella finestra
Windows e non rende completabile l'intera avventura.

La precedente diagnosi di un suono mancante era errata: il comando 9 [9]
seleziona S8.WAV, presente nei dati originali. La revisione 29 corregge
la conversione e rimuove l'eccezione introdotta nella revisione 27.

L�avvio dedicato P508 disabilita il dialogo iniziale sul supporto sperimentale; il prototipo resta sperimentale come indicato qui e nella barra del gioco.

## Revisione 28: cursore visibile

Corretto il puntatore invisibile dentro la finestra: il motore inizializza
la freccia standard di ScummVM, la rende visibile e aggiorna lo schermo
anche quando lo sfondo e fermo. Il cursore rimane visibile dopo il cambio
scena. Questa freccia e provvisoria; le forme specifiche originali del
cursore non sono ancora ricostruite.

Chiudere la precedente versione e avviare bin/Prova-enigma-P508.cmd dalla
nuova cartella estratta. La prova automatica controlla lo stato visibile
del cursore, non una cattura visiva della finestra Windows.

## Revisione 29: corrispondenza dei suoni

Il caricatore originale sottrae 1 al numero serializzato dei comandi
audio 9 e 27. Il prototipo ometteva questa conversione e sceglieva il
file successivo. Ora P508 usa S8.WAV per la risposta corretta, S7.WAV
per quella errata e S6.WAV per il sottofondo selezionato dal comando 27 [7].
Il suono globale di completamento, chiamato direttamente dal motore,
rimane SOUNDS/S12.WAV.

La conversione e verificata sull'eseguibile originale e con prove native
di entrambi gli opcode, inclusi i limiti degli indici. Passano anche le
prove PCM, del sottofondo e dei due percorsi completi di P508. Le prove
automatiche usano SDL dummy: non costituiscono un ascolto manuale.
L'utente ha confermato che P508 e completabile nella prova interattiva;
questo non dimostra la completabilita degli altri enigmi.

## Revisione 30: spiegazione iniziale e musica di P508

Ripristinato l'audio automatico all'ingresso nelle scene di tipo 0 con
script e audio abilitati. P508 dichiara come introduzione S302.WAV:
il file e identico byte per byte a S1.WAV (6,60 secondi). La voce viene
riprodotta per intero prima di avviare gli script. S0.WAV e il sottofondo
locale predefinito, ripetuto quando non sono attivi altri suoni e dopo
il limite temporale originale. Gli effetti lo interrompono; poi riprende.
La selezione esplicita di altri sottofondi resta affidata agli script.

Avvio: bin/Prova-enigma-P508.cmd. Le prove automatiche verificano
l'introduzione completa, l'avvio degli script, la musica, le interruzioni
e la ripresa, oltre ai due percorsi completi dell'enigma. Non e una prova
di ascolto manuale. Le regole di musica globale degli altri tipi di scena
e quelle relative al ripristino di salvataggi restano da implementare.

## Revisione 31: secondo enigma, P511

Avvio dedicato: bin/Prova-enigma-P511.cmd. Include la spiegazione iniziale
originale (circa 21 secondi), musica, animazioni e pulsanti. I controlli
inferiori regolano distanza della Luna, vento e barometro. Il pulsante
OFF consente di uscire dall'enigma; per ricominciare riaprire l'avvio.

P511 ora ha due percorsi di soluzione completi verificati con clic sui
pulsanti originali, a partire dai valori iniziali del file. Il test non
imposta lo stato risolto. Verifica anche limiti delle regolazioni,
inversione delle scelte e uscita senza successo. Questo supera la sola
prova della sequenza finale delle revisioni precedenti.

P508 e P511 sono quindi due enigmi con percorsi completi verificati
automaticamente. Solo P508 ha, finora, la conferma interattiva dell'utente.
Il pulsante ? di P511 raggiunge P408, ma il sistema di aiuto e il ritorno
da esso non sono ancora verificati. Non e ancora giocabile tutta l'avventura.

## Revisione 32: attese iniziali degli script

Supportati i template con un primo comando ritardato, prima esclusi
all'ingresso e nei richiami. Il timer parte dalla registrazione degli
script, prima dell'audio introduttivo: il richiamo non azzera l'attesa.
Le continuazioni conservano invece il tempo relativo al comando precedente.

Verificato lo script originale 0 di P509 a 3499/3500 millisecondi,
insieme a richiami ripetuti, attese gia scadute, ricaricamento e ritorno
al valore zero dell'orologio a 32 bit. P508 e P511 mantengono le prove
complete superate. P509 resta parziale: questa revisione non aggiunge
un terzo enigma interamente completabile.

## Revisione 33: enigma ambientale P509

Nuovo avvio bin/Prova-enigma-P509.cmd, con spiegazione, audio e animazioni.
Selezionare un intervento nel pannello inferiore, poi fare clic sulla
zona dell'immagine a cui applicarlo. Le sei scelte sono energia solare,
riforestazione, trasporto pubblico, ecocura, riciclo e area protetta.
Il pulsante OFF esce; per ricominciare riaprire l'avvio.

Supportate le attese dei clic sulle zone dell'immagine quando l'input
interattivo e abilitato. Sono inoltre ammesse le operazioni di stato
immediate dopo un cambio scena: avvengono prima del ricaricamento;
gli effetti grafici e audio immediati in quella posizione restano esclusi.

La prova completa parte dai valori originali, esegue le due fasi tramite
clic e raggiunge P304 con successo. Una seconda prova sbaglia tre volte
e verifica l'uscita senza successo. Tutti e sei gli script di ingresso
sono ora accodati. P508 e P511 conservano le verifiche complete.

Tre enigmi hanno percorsi completi verificati automaticamente: P508,
P509 e P511. L'utente ha confermato interattivamente P508; gli altri
restano da provare manualmente. L'avventura e il sistema di aiuto non
sono ancora completi. Questa revisione supera il limite P509 della v32.

## Revisione 34: voci sincrone e P505

Nuovo avvio bin/Prova-enigma-P505.cmd. Dopo l'introduzione, leggere la
richiesta nel pannello inferiore e fare clic sul soggetto corrispondente
nell'immagine. Le spiegazioni vocali devono terminare prima che lo
script prosegua, come nell'originale. Tre errori fanno uscire dall'enigma.

Implementate le eccezioni audio sincrone di P505 (file S2..S10) e P512
(S14). Le attese successive partono dalla fine della voce. Rimangono
attive le risposte alla richiesta di chiusura della finestra.

P505 ha prove complete delle otto risposte e dell'uscita dopo tre errori,
tramite clic sulle zone originali senza impostare lo stato risolto.
La soluzione conduce a P520: IL FILMATO SUCCESSIVO NON E ANCORA SUPPORTATO.
Quindi la conclusione del puzzle e verificata, ma non la prosecuzione
attraverso quel filmato. P508, P509 e P511 conservano le verifiche complete.
La conferma manuale dell'utente resta disponibile soltanto per P508.

## Sviluppo del filmato P520

Implementati selezione del segmento (37) e avvio QuickTime (3) per P520.
La scena usa PLACES/P408/MENTORS.MOV: segmento da 55407 per 1274 unita
alla scala di 30 unita/secondo, visualizzato a (240,130), 160x120.
La riproduzione e asincrona e conserva il timer originale di 44 secondi
verso P537. Il clic sulla scena salta il filmato verso la stessa destinazione.
Il decoder e l'audio del filmato vengono liberati al cambio scena.

Questa modifica supera il limite del filmato P520 descritto nella revisione
34. Il supporto video e per ora registrato solo in questo contesto; P537
e altri filmati richiedono ancora sviluppo. Non sono stati creati nuovi
archivi, launcher o pacchetti dimostrativi. La compilazione di sviluppo
rimane in work/fresh-20260913/build/Releasex64/scummvm.exe nel workspace.

Verifica continua superata: 425 fotogrammi, termine del segmento prima
del cambio scena a 44 secondi. Video senza finestra e audio WASAPI muto;
ascolto e visione manuali restano da verificare.

## Indicatori e selettore P537

Corretta l'eredita del fotogramma iniziale negli sprite clonati, secondo
_SWCloneSprite originale. In P537 vengono ora disegnati 29 sprite iniziali
anziche 9: ricompaiono i 20 indicatori che condividono i dieci fotogrammi
dello sprite sorgente. La prova tramite clic originali verifica tutti i
valori 0..15, incremento, decremento e blocco ai due estremi.
Il lancio del razzo (comando personalizzato 23/14) resta non implementato:
P537 non e ancora un puzzle completabile. Nessun nuovo pacchetto creato.

## Sviluppo successivo: P537 e P527

Implementato il lancio originale di P537: tre traiettorie, cifre e indicatori,
successo alle impostazioni 11 e 12 e ritorno a P321. Superate le limitazioni
sul lancio descritte sopra. Le prove usano i comandi originali e controllano
anche che il successo ripetuto non venga contato due volte.

P527 ora carica FLATRING.MOV e le sue quattro selezioni; il video resta
visibile durante i ridisegni e si mette in pausa durante le voci sincrone.
Percorsi e uscita sono verificati nel motore con tempo accelerato e seek;
la visione continua dei quattro segmenti resta da verificare.

Le modifiche restano nei sorgenti e nella compilazione di sviluppo.
Non sono stati creati prototipi, nuovi ZIP o launcher. Il gioco completo
non e ancora supportato; gli altri enigmi e la navigazione richiedono lavoro.


## Sviluppo del 24 settembre: P517 e P519

P517 ora esegue l'avvio dell'animazione (19) e l'arresto con scomparsa (30)
secondo l'eseguibile originale. Verificati tramite clic i quattordici valori,
i due pulsanti, il limite inferiore, gli indicatori e le animazioni; la
soluzione conduce a P512 e imposta global33. L'uscita senza soluzione
conduce a P157 e lascia global33 a zero. P512 resta incompleto.

P519 ora esegue anche il lampo bianco originale (21). Verificati i cinque
abbinamenti corretti in due ordini, un abbinamento errato, il ripristino
dell'immagine dopo il lampo e l'uscita senza soluzione. Il ritorno e P281;
global35 viene impostato soltanto dopo tutti gli abbinamenti corretti.

La suite nativa completa passa con questi due nuovi percorsi. Sono prove
automatiche nel motore, con tempi degli script accelerati; non sostituiscono
la verifica manuale di immagini e suoni. Le evidenze originali riproducibili
sono in probe_p517_p519.py e evidence/p517-p519.json. La conferma manuale
dell'utente rimane quella di P508. Sette puzzle hanno ora percorsi completi
verificati: P505, P508, P509, P511, P517, P519, P537. P527 conserva le prove
separate con seek del video. Non e ancora disponibile una percentuale
attendibile dell'intera avventura completabile.

Supportato anche opcode 24 (spostamento e fotogramma): sette comandi
originali P525 verificati, inclusa conservazione dello stato e rifiuto degli
indici non validi. Suite completa nuovamente superata dopo questa modifica.
P525 resta incompleto: FSUN.MOV richiede quattro segmenti, ora documentati
in evidence/p525-video.json ma non ancora abilitati nel motore.
Copertura statica aggiornata: 83/121 template (68,6%); non misura la
percentuale di gioco completabile. Manifesto della compilazione di sviluppo:
evidence/development-validation.json. Binari e pacchetto v34 invariati.


## Sviluppo del 24 settembre, sera: P525 e P529

P525: verificati i sette esperimenti, limite del selettore, ripetizione e
uscite risolta/non risolta. Soluzione verso P509, global41=1; uscita normale
verso P304 senza successo. Implementato FSUN.MOV e corretto il cambio di
immagine, che cancella il fotogramma video precedente come nell'originale.

P529: verificati i quattro esiti, limiti 0..15, avvio/arresto degli indicatori,
soluzione completa e uscita anticipata riuscita dopo il gruppo 6..8; uscita
senza successo dopo il gruppo 1..5. Destinazione P98. Il successo imposta
global45 e sblocca global60; la ripetizione ripristina global60 senza
incrementare di nuovo il contatore. Implementato FUNIV.MOV.

Prove continue dei quattro segmenti di ciascuno dei tre contesti P525,
P527 e P529: dodici segmenti completi, senza seek accelerato. Restano prove
automatiche: ascolto e visione manuali non sono certificati. La voce
introduttiva viene ora riprodotta anche nelle scene con filmati; P529 ha
una prova di durata (20187 ms misurati per una voce di 20154 ms).

La suite nativa completa passa. Dieci puzzle hanno percorsi verificati
automaticamente: P505, P508, P509, P511, P517, P519, P525, P527, P529, P537.
Per i puzzle con video le prove delle interazioni e dei segmenti continui
sono separate. Il gioco intero resta incompleto, senza percentuale globale
attendibile. Manifesto aggiornato: evidence/development-validation.json.
Nessun nuovo prototipo, ZIP o launcher; il pacchetto v34 resta invariato.


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


## Help keyboard navigation, 14 October 2026

PageUp/PageDown scroll the article with one line of context; Home/End reach its bounds, including inline pictures. These are native reader controls, not inferred original WinHelp behavior. Other keys and modified shortcuts retain the standard ScummVM dialog handling. All 781 articles passed production dialog dispatch checks, beginning/end clamping, opposite-page movement and modifier rejection. Full WASAPI regression and native save/import checks passed on the matching executable.


## P508 settled question saves, 15 October 2026

Native version3 now saves P508 between questions, including six locals, all global/local values and their known/width metadata, full32-bit RNG, program epoch, branch state, previous place, completion count, sprite visibility/frame selection and ambient audio state. Pending actions, foreground speech, staged images, moving sprites and button pulses are excluded. Original data confirms18 opaque508x108 pictures at(67,354); the selected picture reconstructs the background without storing media. Startup scripts and introduction are skipped on load. Ambient music restarts at the beginning, not at the exact saved sample.

Three seeds and correct/wrong/mixed routes cover63 saved boundaries and 291 resumed answer steps, comparing screen pixels, script data, RNG, sound IDs/counts, destination and completion count with uninterrupted runs. Save/load/save data is stable except for the advancing clock. 2464 truncations,2464 byte corruptions and14 invalid checksummed states are rejected without changing the live state. Physical slot2 loads in a fresh process with the identical state/screen fingerprint and completes the seven remaining correct answers. Music/foreground guards and slot metadata pass. Exploration v1/v2 regressions, help and full WASAPI suite pass on the matching executable. Other puzzle saves remain unsupported.


## P505 settled question saves, 15 October 2026

Native v4 saves P505 between questions. It retains all script state, RNG, completion count, sprite visibility/frame selection, ambient state and entered flags for four sprite and ten rectangle hover targets. The original eight opaque 135x86 pictures at (254,362) reconstruct the current question. Loading skips startup and speech; remaining on a highlighted target does not replay its entry event. Foreground speech, queued work, staged pictures and button pulses exclude saving. Music restarts from its beginning.

Two seeds and correct/wrong/mixed routes verify 38 saved boundaries and their 38 successor states against uninterrupted play, including screen, script/RNG, sound count/ID and hover exit. All 38 unchanged-hover checks pass. 2472 truncations, 2472 byte corruptions and 16 checksummed invalid states reject atomically. Physical slot 3 restores in a fresh process with the same fingerprint and finishes six remaining answers. P508 v3 (63 boundaries, 291 resumed steps), exploration v1/v2, original GAMESTAT import, help and full WASAPI regressions pass on the matching build. These are automated tests; manual audiovisual verification and saves in other puzzles remain outstanding.


## P519 native saves, 16 October 2026

Native v5 now saves idle P519 selections and partial solutions. It retains all script state and RNG, clock/count, 27 sprite frames and visibility, ten rectangle hover flags and ambient state. Two original image identities reconstruct the full background: the latest large image and optional subsequent small image. Image identities change only when display commits; a new large image clears the small record. Loading skips startup and speech. Foreground audio, queued work, button pulses and staged pictures exclude saving. Ambient music restarts from its beginning.

Tests pass 74 gameplay successor comparisons (all 25 detector/target pairs, both solve orders, repeated target and unsolved exit), plus 30 separate native image-composition round trips. All compare script/RNG, background/screen pixels, sprite frames, hover state and applicable sound IDs/counts. 2584 truncations, 2584 byte corruptions and 18 checksummed invalid states reject without changing live state. Physical slot 4 loads in a fresh process with an identical fingerprint and completes five pairings after the wrong Sun selection. P505/P508 full save tests, previous-build v3/v4 slots, exploration saves, original import, help and full WASAPI suite pass. This remains automated evidence; manual audiovisual playthrough and other puzzle saves are outstanding.


## P524 native saves, 18 October 2026

Native v6 saves settled P524 questions with all script/RNG state, previous scene, clock/count, 32 sprite frames/visibility and the continuing Triton animation epoch and parameters. Mentor return preserves the additional known local values. The original committed picture is reconstructed. The Moon follows all eight random choices; the earlier preparation calling it an initial stage was incorrect. Startup and foreground speech are skipped on load; ambient music restarts from the beginning.

Validation: 72 round trips (23 gameplay successors, one post-help identity, 48 animation cases), all eight animation frames at 199/200/2200ms with ordinary and wrapping clocks, two solve routes, third-error exit, voluntary exit, mentor return and fresh-process slot5 completion. 2612 truncations, 2612 byte corruptions and 21 checksummed invalid states reject atomically. Full P505/P508/P519 saves, prior-build v3/v4/v5 slots, exploration v1/v2, import, help and WASAPI suite pass on the same build. These are automated results, not manual audiovisual confirmation.


## P526 native saves, 18 October 2026

Native v7 saves settled P526 entry, stopped experiments and answered states. It retains the full runner/RNG, clock/count, 23 sprite records with render/center positions, animation and movement epochs, orbital parameters and flags, committed picture and six hover bits. Orbit travel, foreground audio, queued work and staged images exclude saving. Ambient music restarts at its beginning.

Verified on one matching build: 686 round trips (33 gameplay successors, five identities, 216 animation comparisons, 432 synthetic phase/answer cases), 4956 truncations, 4956 byte corruptions and 25 checksummed invalid states. A physical slot6 loads in a fresh process and completes all remaining questions. The separate native audit observes 33 boundaries on real routes. Full v1-v6 compatibility, previous-build v3-v6 slots, exploration, import, help and WASAPI regressions pass. This is automated evidence, not a full manual audiovisual playthrough.


## Full original frame, 18 October 2026

Ordinary presentation now preserves all 640x480 original pixels. The diagnostic strip is opt-in via astronomica_debug_overlay. The old strip covered rows 456-479, including five rows of a P528 picture. Twelve scene comparisons, 855 original picture pixels, optional-strip activation and restoration pass. All existing v1-v7 saves, prior-build v3-v7 slots, help/import and full WASAPI regressions pass on the same executable. Existing legacy fingerprints intentionally retain their 456-row scope; the new presentation test checks all 480 rows.


## Separate music control, 18 October 2026

Looping background WAVs now use the ScummVM Music channel. Foreground recordings retain the Effects channel and replace the active loop as before. Six scenes pass with Music muted and volume zero, Effects audible, and all original controls restored afterward. Twelve original S0/S1 WAV hashes are unchanged. Presentation, compatible v1-v7 saves, prior-build slots, help/import and the full WASAPI suite pass on the same executable. This is automated channel/control verification; manual listening remains outstanding. See AUDIO-CHANNELS.md and evidence/audio-channels-validation.json.


## P528 native saves, 18 October 2026

Native v8 saves settled P528 states with full runner/RNG, clock/count, nine sprite records, partial eclipse flags, current image pair and retained tall-moon history. Tests cover160 reachable abstract states and640 round trips/successors, including six completion edges and160 exits, using full480-row pixel hashes. 3444 truncations,3444 byte corruptions and30 checksummed invalid states reject atomically. Slot7 loads in a fresh process, retains the old moon row and completes the remaining eclipse with first-success counting. Versions1-7, prior-build slots, presentation/audio controls, help/import and WASAPI regressions pass on the same executable. No whole-game completion percentage is inferred.


## P530 native saves,19 October2026

Native v9 retains14 locals and full runner/RNG,29 sprite records including hidden settled indicator positions, clock/count and the last picture or absence. 800 round trips across14 randomized routes cover five scenarios at every round, all25 pictures, all six placement permutations, wrong/repeated answers and unsolved exit. Slot8 loads in a fresh process with a partial component assembly and prior-round picture, then completes the remaining random rounds without increasing the counter, as in the original. 5604 truncations,5604 byte corruptions and31 checksummed invalid states reject atomically. Versions1-8, previous-build slots, full-frame presentation, music controls, help/import and WASAPI pass on the same executable.
