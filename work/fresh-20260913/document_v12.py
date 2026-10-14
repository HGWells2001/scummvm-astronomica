from pathlib import Path
r=Path('outputs/astronomica-cleanroom')
p=r/'README.md';s=p.read_text().replace('revisione 11. Progresso complessivo stimato: circa 31%', 'revisione 12. Progresso complessivo stimato: circa 33%')
s=s.replace('sottoinsieme di sedici opcode', 'sottoinsieme di diciotto opcode').replace('16, 17, 31, 32, 41', '16, 17, 28, 29, 31, 32, 41')
s=s.replace('composizione su più livelli, interazione con gli sprite, enigmi', 'composizione su più livelli, interazione completa con gli sprite, enigmi')
s=s.replace('- Lettore Python indipendente', '- Clic sperimentali sugli sprite con geometria verificata, precedenza originale e blocco temporizzato degli input.\n- Lettore Python indipendente')
s=s.replace('Il prototipo parte da P1.', '''`bin/Prova-pulsanti.cmd` apre P510 con i clic sugli oggetti abilitati.
Cliccare il pulsante vicino a **(240,397)**, poi quello vicino a **(266,376)**:
le sequenze originali selezionano il pulsante, deselezionano gli altri quattro
e aggiornano la variabile della scena. Per 150 ms dopo l'aggiornamento lo
script blocca nuovi clic. Non serve premere F. Gli altri comandi dell'enigma
possono essere rifiutati; questa prova non rende l'enigma completabile.
L'opzione corrispondente è `astronomica_sprite_input=true`; resta disattivata
nell'esploratore normale. Nessun evento di trascinamento è implementato.

Il prototipo parte da P1.''')
p.write_text(s)
p=r/'INTERPRETER.md';s=p.read_text()
s=s.replace('I clic sono abilitati soltanto nelle scene prive di sprite, poiché la precedenza e le maschere degli sprite non sono implementate.', 'Nell’esploratore normale i clic restano abilitati soltanto nelle scene prive di sprite. La revisione 12 aggiunge una modalità sperimentale per gli sprite, descritta sotto: il test originale usa rettangoli, non le maschere grafiche.')
s+='''

## Input sugli sprite: revisione 12

`_do_mouse` 9:1181–11eb cerca gli sprite in ordine crescente, dal primo.
Sono candidati quelli con flag click (+2d5) o drag (+2d9) uguale a 1.
`_SWIsPointInSprite` 7:0ec1 confronta coordinate signed 16 bit con il
rettangolo +17/+19/+1b/+1d: **tutti i bordi sono inclusi**. Non legge
visibilità o maschera. Il primo candidato colpito impedisce la ricerca delle
aree rettangolari sottostanti. Le aree non-sprite conservano i bordi destro
e inferiore esclusi. Il tipo 0 usa il normale accodamento; il tipo 2 esegue
anche una sequenza aggiuntiva per il trascinamento, ancora esclusa.

Il caricatore conserva ora distintamente flag click, drag, auto-frame e
auto-move. La modalità `astronomica_sprite_input=true` accetta geometrie
statiche a un livello. Quando il fotogramma di anteprima non è selezionato,
richiede che tutti i fotogrammi abbiano dimensioni identiche; quindi non
presume quale fotogramma sia attivo. Una geometria sconosciuta impedisce
di proseguire la ricerca; uno script sconosciuto consuma il clic senza
eseguirlo o trasferirlo agli oggetti sottostanti. È una modalità parziale.

Opcode 28/29: gli handler 15:0c08/0c3c impostano/azzerano DS:06a5 quando
l'argomento è negativo. Gli argomenti non negativi modificano l'abilitazione
di un singolo sprite e sono tuttora rifiutati. Il flag globale blocca nuovi
clic ma non ferma la coda. `_do_place` 9:01e0 lo azzera al cambio scena;
il motore riproduce questo azzeramento.

P510, sprite 10 e 11: la verifica usa gli script di clic completi originali,
non singole istruzioni estratte. Controlla accodamento, scelta esclusiva dei
cinque fotogrammi, variabile locale 4 uguale a 1/2, blocco a 149 ms e
riabilitazione a 150 ms. Al cambio scena verifica pulizia della coda e del
blocco. Verifica anche bordi inclusivi e la precedenza di uno sprite
invisibile con script rifiutato. Quest'ultimo caso è una variazione di test
in memoria, non una modifica dei file originali.

`verify_mouse_reference.py` genera indipendentemente con Pillow le due
immagini attese usando bitmap e maschere originali. Hash FNV-1a RGB565:
`fb10a99b`, `966034ff`; RGB888: `3f2d859f`, `655cfed9`.
Le immagini sono in `evidence/mouse/`. Il test nativo confronta l'intero
schermo utile 640×456, oltre allo stato interno.

Questo aggiunge interazioni complete di singoli pulsanti; mancano ancora
inizializzazione completa degli enigmi, trascinamento, hover, audio, filmati
e confronto interattivo con l'eseguibile originale.
'''
p.write_text(s)
p=r/'SPRITES.md';s=p.read_text();s+='''

## Clic: revisione 12

Il nuovo test originale `_SWIsPointInSprite` dimostra che le maschere non
servono per i clic: viene usato il rettangolo, con tutti i bordi inclusi,
indipendentemente dalla visibilità. La ricerca sceglie il primo sprite
abilitato in ordine di file. Dettagli, limiti della modalità sperimentale e
verifiche dei pulsanti P510 sono in `INTERPRETER.md`.
''';p.write_text(s)
base=Path('work/fresh-20260913')
s=(base/'package_v11.py').read_text().replace('v11','v12')
anchor='# Verify the distributable probe independently against the same original.'
s=s.replace(anchor,'''cfg.write_text(cfg.read_text()+'\\n[astronomica-buttons]\\nengineid=astronomica\\ngameid=astronomica\\npath=D:\\\\astro\\nastronomica_start_place=510\\nastronomica_sprite_input=true\\n')
(out/'bin/Prova-pulsanti.cmd').write_bytes(b'@echo off\\r\\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-buttons\\r\\n')
'''+anchor)
s=s.replace("assert 'timer verification: PASS'", "assert 'mouse verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'timer verification: PASS'")
(base/'package_v12.py').write_text(s)
