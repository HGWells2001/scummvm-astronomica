from pathlib import Path
import runpy,sys
r=Path('outputs/astronomica-cleanroom');base=Path('work/fresh-20260913')
probe=(base/'rng_probe.py').read_text()
probe=probe.replace("sys.path.insert(0,str(Path('work/fresh-20260913/deps-verified').resolve()))", "import argparse,hashlib\nap=argparse.ArgumentParser();ap.add_argument('exe',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)")
probe=probe.replace("b=Path('D:/astro/SETUP/ASTRO.EXE').read_bytes()", "b=args.exe.read_bytes()\nassert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'")
probe=probe.replace("    print(name,", "    (args.out/(name+'.asm')).write_text('\\n'.join(lines)+'\\n')\n    print(name,")
(r/'probe_random.py').write_text(probe)
sys.path.insert(0,str((base/'deps-verified').resolve()))
sys.argv=[str(r/'probe_random.py'),'D:/astro/SETUP/ASTRO.EXE','--out',str(r/'evidence/random-asm')]
runpy.run_path(str(r/'probe_random.py'),run_name='__main__')
p=r/'README.md';s=p.read_text().replace('revisione 16. Progresso complessivo stimato: circa 39%', 'revisione 17. Progresso complessivo stimato: circa 40%')
s=s.replace('sottoinsieme di venti opcode', 'sottoinsieme di ventuno opcode').replace('32, 33, 41,', '32, 33, 40, 41,')
s=s.replace('- Lettore Python indipendente', '- Generatore casuale originale e scelta in un intervallo (opcode 40), verificati sulle varianti di P510.\n- Lettore Python indipendente')
s=s.replace('La revisione 16 estende la logica interna degli enigmi;', 'Le revisioni 16 e 17 estendono la logica interna degli enigmi;')
s=s.replace('non aggiunge una\nnuova prova interattiva né rende completabile P511.', 'non aggiungono una\nnuova prova interattiva né rendono completabili P510/P511.')
p.write_text(s)
p=r/'INTERPRETER.md';s=p.read_text();s+='''

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
larghezza signed 16 bit vengono rifiutati prima di consumare casualità.
Lo scope 2 rimane escluso.

Il seme iniziale in esecuzione normale proviene da ScummVM e viene
ridotto a 16 bit; l'originale usa il tempo del sistema nella chiamata
iniziale a srand. Si riproduce la sequenza a parità di seme, non la stessa
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
È una prova dell'istruzione originale, non dell'intera catena d'ingresso
P510, che contiene ancora filmato e comandi personalizzati non supportati.
Compilazione e tutte le verifiche precedenti restano superate.
''';p.write_text(s)
s=(base/'package_v16.py').read_text().replace('v16','v17')
s=s.replace("assert 'bit verification: PASS'", "assert 'random verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'bit verification: PASS'")
(base/'package_v17.py').write_text(s)
