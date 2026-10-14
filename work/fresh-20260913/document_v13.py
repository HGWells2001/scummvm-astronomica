from pathlib import Path
r=Path('outputs/astronomica-cleanroom')
p=r/'README.md';s=p.read_text().replace('revisione 12. Progresso complessivo stimato: circa 33%', 'revisione 13. Progresso complessivo stimato: circa 35%')
s=s.replace('Restano da implementare animazione automatica,', 'Restano da completare animazione automatica,')
s=s.replace('Gli sprite con più fotogrammi vengono disegnati solo dopo una selezione esplicita del fotogramma.', 'Nella modalità normale gli sprite con più fotogrammi attendono una selezione esplicita; la modalità animazione inizializza anche il primo fotogramma degli sprite non clonati.')
s=s.replace('- Lettore Python indipendente', '- Prima animazione automatica dei fotogrammi e pressione/rilascio dei pulsanti di tipo 2, verificati su P510.\n- Lettore Python indipendente')
s=s.replace('Il prototipo parte da P1.', '''`bin/Prova-animazione.cmd` apre P510 con il primo fotogramma degli oggetti
e l'animazione sperimentale abilitati. Cliccare il pulsante vicino a
**(130,400)**: appare l'indicatore a (50,100), che alterna due fotogrammi
ogni 400 ms. Il pulsante torna al fotogramma di riposo dopo 500 ms;
l'indicatore viene nascosto dopo la pausa di 10 secondi successiva allo
sblocco dei clic. Funzionano anche i pulsanti di selezione già verificati.
Le altre funzioni dell'enigma rimangono incomplete. La modalità usa
`astronomica_animation=true` e `astronomica_sprite_input=true`.

Il prototipo parte da P1.''');p.write_text(s)
p=r/'INTERPRETER.md';s=p.read_text().replace('anche una sequenza aggiuntiva per il trascinamento, ancora esclusa.', 'anche una sequenza aggiuntiva, esclusa nella revisione 12. La revisione 13 ne identifica la funzione come pressione/rilascio del pulsante, non trascinamento.')
s+='''

## Fotogrammi iniziali, animazione e pulsanti tipo 2: revisione 13

Nuove estrazioni dall'eseguibile originale:
`_SWAddFrame` (7:0678) seleziona il primo elemento dell'array dopo ogni
aggiunta; `_CreateSpriteFromBmpMem` (11:00b4) imposta l'intervallo 0..n-1.
`_SWCreateSprite` inizializza indice 0, avanzamento +1 e timestamp 0.
La modalità sperimentale inizializza quindi a 0 il fotogramma degli sprite
non clonati a un livello, senza dedurlo dall'aspetto dello sfondo.

`_load_place` 9:2e88–2eaa converte il primo campo del blocco auto-frame
attraverso AX signed 16 bit e lo passa a `_SWSetSpriteFrameTime` (7:09a9).
`_SWProcessSpriteWorld` (6:07c8) legge timeGetTime; quando la differenza
con segno raggiunge il periodo, salva il tempo attuale e avanza di uno,
ripartendo dall'inizio oltre l'ultimo indice. Non recupera più fotogrammi
per un ritardo lungo e non verifica la visibilità prima di avanzare.

La modalità `astronomica_animation=true` supporta per ora sprite non
clonati, senza movimento automatico, a un livello, con blocco originale
[periodo,1,0]. I periodi negativi vengono esclusi, 0 avanza a ogni passaggio.
I valori diversi dei due campi finali restano conservativamente esclusi;
non viene attribuito loro un significato non dimostrato.
Il timer parte da zero nel dominio getMillis di ScummVM: non si rivendica
la stessa fase iniziale dell'orologio globale di una sessione Windows 3.x.

Correzione della precedente interpretazione del clickType 2:
il simbolo originale DS:0bf0 è `_button_click`. `_do_place` 9:0071–00d5
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
`74ec5203`/`cbf46977`. Il motore confronta questi hash sullo schermo 640×456.
Il secondo riferimento include il pulsante ancora premuto a 400 ms.
Le immagini sono in `evidence/animation/`. Restano attive tutte le verifiche
precedenti; non è ancora possibile completare l'enigma P510.
''';p.write_text(s)
base=Path('work/fresh-20260913');s=(base/'package_v12.py').read_text().replace('v12','v13')
anchor='# Verify the distributable probe independently against the same original.'
s=s.replace(anchor,'''cfg.write_text(cfg.read_text()+'\\n[astronomica-animation]\\nengineid=astronomica\\ngameid=astronomica\\npath=D:\\\\astro\\nastronomica_start_place=510\\nastronomica_sprite_input=true\\nastronomica_animation=true\\n')
(out/'bin/Prova-animazione.cmd').write_bytes(b'@echo off\\r\\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-animation\\r\\n')
'''+anchor)
s=s.replace("assert 'mouse verification: PASS'", "assert 'animation verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'mouse verification: PASS'")
(base/'package_v13.py').write_text(s)
