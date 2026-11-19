# Puntini e quadratini: indicatore originale dei puzzle

Indagine del 19 novembre 2026, dai due screenshot forniti e dall'eseguibile originale `D:/astro/SETUP/ASTRO.EXE`. Nessuna modifica al motore o ai file del gioco.

## Risultato

La fila rappresenta gli stati di completamento dei puzzle. Non si tratta di un'immagine decorativa: l'originale la disegna leggendo i valori della partita, attraverso la routine `_draw_score`, segmento3, indirizzi `39ca–3adf`.

Ogni posizione legge uno dei valori globali da20 a46. Quando il valore e' esattamente1 viene disegnato un quadratino; altrimenti viene disegnato un puntino. La routine non ricava i segni dal contatore numerico complessivo dei puzzle completati.

Normalmente sono visibili **26 posizioni**, relative ai valori20–45. Se il valore46 e'1, la routine disegna anche la posizione27, gia' come quadratino. Il valore46 e' registrato dal completamento di **P530**. Questa scelta non controlla che tutti gli altri26 valori siano1: non va interpretata come una verifica generale di fine partita.

Le posizioni rappresentano gruppi di completamento: non bisogna attribuire un segno distinto a ogni cartella o fase intermedia di un puzzle.

## Confronto dei tuoi screenshot

| Screenshot | Posizioni | Quadrati | Puntini |
| --- | ---: | ---: | ---: |
| 143113 | 26 | 15 | 11 |
| 143137 | 26 | 17 | 9 |

Due posizioni passano da punto a quadrato:

| Posizione da sinistra | Valore della partita | Puzzle che registra il risultato |
| --- | ---: | --- |
| 8 | 27 | P511 |
| 19 | 38 | P522 |

L'associazione di P511, P522 e P530 ai rispettivi valori e' stata ricontrollata nelle istruzioni originali dei loro gestori di completamento. L'analisi dei screenshot usa le dimensioni dei componenti bianchi nella fila; non presume che i tempi di cattura corrispondano a tempi di gioco consecutivi.

## Disegno esatto alla risoluzione originale

Il colore e' bianco. Con `i` che parte da1:

| Segno | Rettangolo, estremi destro/inferiore esclusi | Dimensione |
| --- | --- | --- |
| Risolto | `(10+6*i,327)` → `(14+6*i,331)` | 4×4 pixel |
| Non risolto | `(11+6*i,328)` → `(13+6*i,330)` | 2×2 pixel |

La distanza tra i centri e'6 pixel. Il primo quadrato parte da `x=16`. Il ridimensionamento del video nel browser spiega le dimensioni maggiori negli screenshot.

La chiamata originale avviene in `_load_place`, indirizzo `9:1911`, dopo la composizione dello sfondo. E' condizionata da `_nav_place != 0` e `_monitor_status != 0`: riguarda la visualizzazione di esplorazione. `_monitor_status` e' inizializzato a1 nell'eseguibile distribuito. Non e' il moderno overlay diagnostico di ScummVM.

## Situazione nel motore attuale

I valori di completamento sono gia' gestiti e conservati nei salvataggi. Nella versione verificata del motore manca invece il disegno equivalente a `_draw_score`: la composizione attuale di sfondo, sprite e fotogrammi non riproduce questa fila in funzione dei valori20–46.

Il ripristino richiede quindi una funzione di disegno che legga lo stato esistente, senza introdurre un secondo sistema di conteggio o cambiare il formato dei salvataggi. Dovra' rispettare le26/27 posizioni, il confronto esatto con1, le dimensioni originali e la condizione di visualizzazione nell'esplorazione. Il caricamento di una vecchia partita dovra' ricostruire la fila dagli stessi valori ripristinati.

Questa indagine **non implementa ancora la funzione**. Prima del rilascio serviranno controlli di immagine con nessun puzzle risolto, singoli risultati, risultati misti, P530 completato e ripristino dei salvataggi. Aggiungere la fila cambia i pixel della schermata: anche i confronti grafici esistenti dovranno tenere conto del comportamento originale appena recuperato.

## Prove e limiti

Il programma di analisi esegue le istruzioni originali della routine in un interprete ristretto, modellando solo le chiamate esterne di disegno. Ha verificato211 stati e ripetuto ciascuno con due valori diversi del contatore complessivo, per422 esecuzioni. I casi includono nessun risultato, tutti i risultati, ogni singolo valore e stati misti; i valori diversi da1 non producono quadrati.

Le funzioni di disegno sono identificate dalle rilocazioni NE e dai simboli presenti nello stesso eseguibile: `CreateSolidBrush`, `SelectObject`, `SetRect`, `FillRect`, `DeleteObject` e `_SWSetPortToBackGround`. Non e' una prova eseguita dal vecchio Windows/WinHelp e non e' un confronto integrale di tutti i pixel del video. La ricompressione e il ridimensionamento dei due screenshot consentono il riconoscimento dei segni, non una certificazione grafica completa.

Programma riproducibile: `probe_progress_indicator_nov19.py` in questa cartella. Risultato locale: `work/fresh-20260913/progress-indicator-original-nov19b/proof.json`.

L'eseguibile originale e' identificato dallo SHA256 `c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e`. La routine analizzata ha SHA256 `e94e52efeb586a59bd5ad0bb88856d16dc6463cae17c5db1efc6261f8b88f6b8`. Nessuna immagine del gioco o del video e' stata copiata nel repository di pubblicazione.

Il conteggio dei quadrati misura lo stato di quella partita; non misura la percentuale di sviluppo o la copertura di tutti i comportamenti del motore.
