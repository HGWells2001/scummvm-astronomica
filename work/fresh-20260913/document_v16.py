from pathlib import Path
r=Path('outputs/astronomica-cleanroom')
p=r/'README.md';s=p.read_text().replace('revisione 15. Progresso complessivo stimato: circa 38%', 'revisione 16. Progresso complessivo stimato: circa 39%')
s=s.replace('sottoinsieme di diciannove opcode', 'sottoinsieme di venti opcode').replace('31, 32, 41,', '31, 32, 33, 41,')
s=s.replace('- Lettore Python indipendente', '- Attivazione e disattivazione di singoli bit delle condizioni globali/locali tramite opcode 33, verificata sui comandi originali di P511.\n- Lettore Python indipendente')
s=s.replace('## Avvio del prototipo', '''La revisione 16 estende la logica interna degli enigmi; non aggiunge una
nuova prova interattiva né rende completabile P511. Gli avvii già disponibili
restano validi. La nuova verifica automatica usa le istruzioni originali
per controllare che un singolo indicatore cambi senza alterare gli altri.

## Avvio del prototipo''');p.write_text(s)
p=r/'INTERPRETER.md';s=p.read_text();s+='''

## Indicatori nelle condizioni: revisione 16

L'opcode 33 non copia condizioni: modifica un bit del valore selezionato.
Gli argomenti sono scope, id, posizione del bit, azione. Lo scope 0 sceglie
i globali, 1 i locali; scope 2 resta escluso. La tabella originale in
15:180e contiene 0/1/2 e destinazioni 0f34/105b/1186.

L'eseguibile carica la costante float 2.0 da DS:0726 e chiama l'ordinal 632
di BC40RTL.DLL. Il nome esportato nella libreria originale è `_pow`,
confermato leggendo la sua tabella NE. `analyze_bits.py` riproduce questa
estrazione, riporta SHA-256 della libreria e verifica quello di ASTRO.EXE;
il rapporto è `evidence/bits.json`. Non è stato utilizzato codice di
implementazioni precedenti del gioco.

Con azione 1 il risultato 2^bit viene combinato con OR. Nel ramo di
disattivazione l'originale verifica prima che il bit sia presente, poi
sottrae 2^bit; quindi una seconda disattivazione non altera altri bit.
Il modulo ammette azioni 0/1 e posizioni 0..30, per le quali la potenza e
la conversione all'intero signed originale sono esatte. Bit 31, posizioni
negative, scope non supportati e id fuori intervallo vengono rifiutati
prima di qualsiasi effetto. Il codice usa unsigned 32 bit per conservare
gli altri indicatori, incluso un bit di segno già presente.

Le prove isolate verificano entrambi gli scope, bit 0/30, ripetizione delle
operazioni, conservazione del bit 31 già presente, separazione tra scope,
accodamento e rifiuto atomico dopo un'assegnazione valida.
La prova sul corpus carica P511 e usa quattro istruzioni originali 33
della sequenza 3, una per volta. Il valore locale 5 viene preparato a 6
nel test: i risultati attesi sono 7,6,6,6, mentre il globale 5 resta 123.
Questa preparazione verifica i bit estranei; non è lo stato iniziale del
gioco, che rimane inalterato nei file originali. Non viene eseguita tutta
la sequenza P511, che contiene ancora operazioni non supportate.

Compilazione e verifiche native precedenti continuano a passare.
L'avanzamento percentuale resta una stima del lavoro di sviluppo, non
una misura del gioco completabile.
''';p.write_text(s)
base=Path('work/fresh-20260913');s=(base/'package_v15.py').read_text().replace('v15','v16')
s=s.replace("assert 'transition verification: PASS'", "assert 'bit verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'transition verification: PASS'")
(base/'package_v16.py').write_text(s)
