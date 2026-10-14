from pathlib import Path
r=Path('outputs/astronomica-cleanroom');base=Path('work/fresh-20260913')
p=r/'README.md';s=p.read_text().replace('revisione 17. Progresso complessivo stimato: circa 40%', 'revisione 18. Progresso complessivo stimato: circa 41%')
s=s.replace('sottoinsieme di ventuno opcode', 'sottoinsieme di ventidue opcode').replace('33, 40, 41,', '33, 39, 40, 41,')
s=s.replace('- Lettore Python indipendente', '- Scelta casuale senza ripetizioni tramite opcode 39, con verifica delle otto varianti originali di P505.\n- Lettore Python indipendente')
s=s.replace('Le revisioni 16 e 17', 'Le revisioni 16–18');p.write_text(s)
p=r/'INTERPRETER.md';s=p.read_text();s+='''

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
calcolano la disponibilità al momento dell'esecuzione, anche se lo stato
è cambiato dopo l'accodamento. Lo stato sorgente viene aggiornato prima
del risultato, nell'ordine originale.

La verifica usa il comando [1,1,1,0] originale di P505, con le dichiarazioni
originali (larghezza 8, maschera iniziale 0). Con seme 1 l'ordine è
1,2,5,3,6,4,8,7. Dopo otto estrazioni la maschera è 255; la nona lascia
invariato il risultato ma consuma il generatore. Il successivo numero
grezzo deve essere 31126. `verify_variant_reference.py` ricava un riferimento
indipendente usando una lista di candidati, nei dati `evidence/variants.json`.

I test isolati verificano tutte le quattro combinazioni globale/locale,
una maschera parzialmente usata, bit esterni preservati, esaurimento e
rifiuto di larghezza 32 senza consumare casualità. Le verifiche precedenti
continuano a passare. L'intera sequenza d'ingresso P505 resta incompleta:
non è ancora una prova giocabile dell'enigma.
''';p.write_text(s)
s=(base/'package_v17.py').read_text().replace('v17','v18')
s=s.replace("assert 'random verification: PASS'", "assert 'variant bag verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'random verification: PASS'")
(base/'package_v18.py').write_text(s)
