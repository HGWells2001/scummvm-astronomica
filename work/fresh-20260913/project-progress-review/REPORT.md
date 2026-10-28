# Avanzamento del progetto Astronomica — 27 ottobre 2026

Indice complessivo di accettazione: **60% — 6 criteri superati su 10**. È un nuovo indice esplicito dei traguardi del progetto, basato su una checklist fissa. Non misura il lavoro già svolto in ore e non certifica che il60% del gioco sia giocabile. La percentuale del lavoro totale rimane non determinabile finché manca un inventario completo delle obbligazioni e una stima del lavoro residuo.

La versione verificata usata per questo indice è P504/formato26, eseguibile SHA256 `2a305b13466244f84cfd092bfa20774ea0bcfe2f91dbef77decddb850a3a727c`, pubblicata nel commit `1af25c6ced7b315e2c7bbd7bba3c58d125a0c022`. Suite completa, compatibilità, copia indipendente e remoto sono PASS. Il candidato P501 in lavorazione non entra nel conteggio finché non completa le proprie verifiche. Un candidato ancora in prova non cancella i risultati della versione pubblicata precedente.

## I dieci criteri fissi

Ogni criterio vale un punto quando è interamente superato. Parziale e non verificato valgono zero; non vengono assegnate percentuali soggettive alle parti aperte. Formula: `100 × criteri PASS / 10`. Le unità sono traguardi di accettazione, non quantità equivalenti di lavoro. Non si dividono o accorpano i criteri per far aumentare il numero.

| ID | Criterio e condizione di superamento | Stato attuale | Evidenza principale |
|---|---|---|---|
|A01|Motore reale integrato in ScummVM: riconoscimento della copia originale e build Windows locale riproducibile con controlli sullo stesso eseguibile.|PASS|`engine/astronomica/detection.cpp`; `evidence/development-validation.json`; `p504-checkpoint-status.json`.|
|A02|Avvio normale da P1, configurazione di gioco, input e navigazione di base verificati; preferenze e salvataggi personali preservati.|PASS|`LOCAL-PLAY.md`; `evidence/local-launcher-validation.json`; `evidence/runtime.log`.|
|A03|Inventario completo delle funzionalità originali necessarie e dei rami importanti: ogni voce associata a una prova di esecuzione o a un limite esplicito accettato, senza rami necessari rimasti ignoti.|NON VERIFICATO|Esistono35 scene di percorso e121 template statici; questi inventari non costituiscono ancora un elenco esaustivo dell'intero gioco.|
|A04|Tutte le35 scene di puzzle dell'inventario corrente superano le rispettive suite native automatiche sullo stesso eseguibile.|PASS|`evidence/development-validation.json`; `evidence/runtime.log`; `p504-checkpoint-status.json`.|
|A05|Riproduzione audiovisiva e presentazione supportate superano i controlli automatici: filmati originali, WAV, Music/Effects e immagine completa.|PASS|`evidence/audio-channels-validation.json`; `evidence/presentation-validation.json`; elenco scene video nel manifest di sviluppo.|
|A06|Aiuto nativo funzionale: lettura/rendering di781 articoli e31 immagini originali, ricerca, scorrimento, navigazione e ritorno al gioco.|PASS|`evidence/help-native-validation.json`; `evidence/help-native-runtime.log`.|
|A07|Esplorazione e tutte le35 scene inventariate hanno salvataggi nativi utili ai confini dichiarati, con continuazione, nuovo processo, metadati, rifiuto atomico e compatibilità verificati.|PARZIALE|30/35; restano P501, P510, P512, P523 e P525. I30 ambiti supportati mantengono i propri limiti dichiarati.|
|A08|Tipografia e impaginazione dell'aiuto fedeli: misure di paragrafi/tabelle e presentazione dei caratteri/esponenti verificate rispetto ai riferimenti originali.|PARZIALE|Contenuto e immagini funzionano; restano le misure esatte e la tipografia.13 gruppi di esponenti usano la notazione `^(valore)`.|
|A09|Partita audiovisiva manuale integrale dall'avvio alla conclusione, con mouse/UI, audio, filmati, aiuto e salvataggio/ripresa controllati e risultati registrati; rami alternativi richiesti verificati o esplicitamente delimitati.|NON VERIFICATO|`LOCAL-PLAY.md` e le prove di aiuto/avvio dichiarano ancora necessaria la conferma manuale. Richiede un controllo umano; le suite automatiche non lo sostituiscono.|
|A10|Suite completa sullo stesso eseguibile, veri slot delle versioni precedenti compatibili, hash conservati, pubblicazione dei soli sorgenti verificata su copia indipendente e remoto, checkpoint congelato.|PASS|`p504-checkpoint-status.json`; `p504-completion-status.json`; `p504-seal-status.json`.|

I percorsi `evidence/` e `engine/` della tabella sono sotto `outputs/astronomica-cleanroom`; i file di stato P504 sono sotto `work/fresh-20260913`. `acceptance-index.json` contiene condizioni complete, percorsi dalla radice e hash di tutte le evidenze. `reproduce.py` ricalcola il risultato senza modificare sorgenti, manifest ufficiali o repository di pubblicazione.

## Misure separate che non vanno sommate o mediate

- **85,7% di copertura salvataggi:**30 delle35 scene inventariate hanno un ambito nativo verificato. Le scene includono varianti e non sono35 puzzle distinti. Non equivale a salvataggi in qualunque istante: voci attive, code e transizioni restano esclusi dove dichiarato.
- **35/35 suite di percorso inventariate:** è la copertura dell'inventario automatico corrente, non la prova di una partita continua completa o di ogni ramo originale.
- **94,2% di template statici:**114/121 template passano `canRun` con animazione disattivata. Non è esecuzione e non misura giocabilità. Le sette esclusioni richiedono classificazione; non sono automaticamente sette difetti di gioco.
- **781 articoli e31 immagini dell'aiuto verificati:** il contenuto e l'interazione non dimostrano l'impaginazione originale completa.

Nessun valore viene attribuito alle ore ancora necessarie. Fare la media di85,7%,100% e94,2% produrrebbe un numero privo di un denominatore comune.

## Lavoro residuo e priorità

1. Completare il contratto di salvataggio P501 dai167 stati nativi già osservati: poll originale, sfondi, stato privato della palla e fotogrammi nascosti conservati; poi revisione, ripresa in nuovo processo e suite completa. L'audit da solo non è supporto ai salvataggi.
2. Ricavare e verificare ambiti utili per P510, P512, P523 e P525 dai file originali. Questi percorsi hanno già logica di gioco verificata; il requisito ancora aperto qui è il salvataggio. Filmati, code e stati privati vanno analizzati prima di definire ogni contratto.
3. Chiudere A03 con una mappa versionata dei percorsi originali e dei rami alternativi/fallimento/temporizzazione necessari. I limiti ignoti vanno resi espliciti; non viene promesso di eseguire l'originale Windows se il relativo ambiente non è disponibile.
4. Completare i confronti tipografici dell'aiuto. Stabilire anche se il riavvio del sottofondo al caricamento, attuale convenzione degli slot, soddisfa il bersaglio di qualità fissato.
5. Eseguire e registrare la partita manuale richiesta da A09. Un difetto riproducibile trovato qui riapre il criterio pertinente e genera una correzione con nuova verifica.

## Regole per i prossimi aggiornamenti

Il titolo consigliato è «Avanzamento complessivo verificato:60% dei10 criteri di accettazione; salvataggi85,7%». Questa checklist viene congelata come `astronomica-acceptance-v1`: stessi dieci ID, stesso criterio PASS binario. Nuovi requisiti richiedono una revisione esplicita dello schema, non una modifica silenziosa del denominatore. Il completamento di un nuovo salvataggio porta avanti A07 e la sua misura30/35, ma A07 guadagna il proprio punto solo quando soddisfa la condizione completa.

I manifest esistenti mantengono `whole_game_completion_percent: null`: il nuovo indice ha un significato diverso e non li sostituisce. Il bersaglio della checklist è il motore locale per la copia originale Windows attualmente supportata. Una fusione nel repository ufficiale ScummVM, altre piattaforme/edizioni o un nuovo pacchetto distribuibile non risultano completati e non entrano implicitamente nel bersaglio; diventano criteri solo se richiesti. La pubblicazione nel repository privato dei sorgenti non certifica accettazione upstream.

Le17 evidenze della prima misurazione sono congelate in `project-progress-review/baseline-evidence`, mantenendo i percorsi originali dalla radice. `baseline-manifest.json` conserva tutti gli hash; `verify_frozen.py` li controlla senza scrivere nulla. Dopo il congelamento `reproduce.py` legge queste copie, quindi una modifica futura di README, NEXT-STEPS o dei manifest correnti non riscrive retroattivamente la misurazione P504. Per una nuova versione verificata si aggiorna esplicitamente il riferimento delle prove, conservando questa fotografia e gli stessi dieci criteri.
