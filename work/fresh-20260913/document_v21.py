from pathlib import Path
p=Path('outputs/astronomica-cleanroom/README.md');s=p.read_text().replace('revisione 20.', 'revisione 21.').replace('sottoinsieme di 24 opcode', 'sottoinsieme di 27 opcode').replace('15, 16, 17, 28, 29,', '15, 16, 17, 25, 26, 27, 28, 29,');s=s.replace('- Arresto del suono tramite opcode 10, compresi comandi temporizzati e ripetuti.', '- Arresto del suono tramite opcode 10, compresi comandi temporizzati e ripetuti.\n- Sottofondo PCM locale ripetuto: scelta, sospensione e riattivazione tramite comandi 27, 25 e 26, con precedenza agli altri suoni.');s+='''
## Revisione 21

Aggiunta la gestione esplicita del sottofondo locale. I test isolano i
comandi originali di P511 e P509, verificano la ripetizione dei campioni
di S12.WAV, il limite 5000/5001 ms e la precedenza del suono principale.
L'audio rimane facoltativo. Non sono ancora ricostruite la selezione
implicita dei sottofondi globali o la convivenza con i filmati.
Il progresso stimato rimane circa 43%: questo passaggio non rende ancora
completabile un nuovo enigma. P511 richiede anche la logica personalizzata
di successo, immagini aggiuntive e altre interazioni.
''';p.write_text(s)
p=Path('outputs/astronomica-cleanroom/INTERPRETER.md');s=p.read_text();s+='''
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
''';p.write_text(s)
p=Path('work/fresh-20260913/package_v20.py');s=p.read_text().replace('v20','v21');s=s.replace("assert 'range verification: PASS'", "assert 'loop verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'range verification: PASS'");p.with_name('package_v21.py').write_text(s)
