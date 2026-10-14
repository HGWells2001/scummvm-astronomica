from pathlib import Path
r=Path('outputs/astronomica-cleanroom');base=Path('work/fresh-20260913')
p=r/'README.md';s=p.read_text().replace('15 settembre 2026, revisione 18', '16 settembre 2026, revisione 19').replace('circa 41%', 'circa 42%')
s=s.replace('ventidue opcode', 'ventitré opcode').replace('7, 9, 15,', '7, 9, 10, 15,')
s=s.replace('- Lettore Python indipendente', '- Arresto del suono tramite opcode 10, compresi comandi temporizzati e ripetuti.\n- Lettore Python indipendente')
s+='''

La revisione 19 aggiunge l'arresto audio agli script. La verifica automatica
usa il comando originale temporizzato di P501 su un suono lungo di P510,
senza modificare i file originali. Non aggiunge un nuovo enigma completabile;
gli avvii interattivi esistenti restano disponibili.
''';p.write_text(s)
p=r/'INTERPRETER.md';s=p.read_text();s+='''

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
''';p.write_text(s)
s=(base/'package_v18.py').read_text().replace('v18','v19').replace('2026-09-15-v19','2026-09-16-v19')
s=s.replace("assert 'audio verification: PASS'", "assert 'stop verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'audio verification: PASS'")
(base/'package_v19.py').write_text(s)
