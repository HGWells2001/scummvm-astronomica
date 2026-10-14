from pathlib import Path
p=Path('outputs/astronomica-cleanroom/README.md');s=p.read_text();s=s.replace('revisione 19. Progresso complessivo stimato: circa 42%', 'revisione 20. Progresso complessivo stimato: circa 43%');s=s.replace('- Arresto del suono tramite opcode 10, compresi comandi temporizzati e ripetuti.', '- Arresto del suono tramite opcode 10, compresi comandi temporizzati e ripetuti.\n- Intervalli di animazione modificabili tramite opcode 48: quattro comandi originali di P511 verificati, con confronto indipendente dei quattro fotogrammi.');start=s.index("L'interprete riconosce un sottoinsieme di ");end=s.index(' opcode (',start);s=s[:start]+"L'interprete riconosce un sottoinsieme di 24"+s[end:];s=s.replace('45, 46, 47 e 51)', '45, 46, 47, 48 e 51)');s += '''
## Revisione 20

Il comando 48 cambia l'intervallo dei fotogrammi senza cambiare subito
l'immagine visibile o il timer. Le quattro istruzioni originali di P511
sono verificate a intervalli di 500 ms; le immagini coincidono con un
riferimento indipendente ricostruito dai bitmap originali. Build e suite
nativa superate. Questa verifica isola le istruzioni: l'enigma P511 completo
non e ancora giocabile e non viene aggiunto un nuovo avvio interattivo.
''';p.write_text(s)
p=Path('outputs/astronomica-cleanroom/INTERPRETER.md');s=p.read_text();s+='''
## Intervalli dei fotogrammi: revisione 20

Opcode 48 [sprite, primo, ultimo], handler originale 15:0520-05af.
Il limite inferiore negativo viene portato a zero, quello superiore
oltre il numero dei fotogrammi viene ridotto a numero-1. La chiamata
_SWSetSpriteFrameRange (7:0981) passa due interi con segno a 16 bit;
il setter scrive soltanto i campi +5f e +63. Il fotogramma corrente e
il timestamp restano invariati. _SWProcessSpriteWorld (6:0848-0899)
aggiunge il passo; sotto il primo limite passa all'ultimo, sopra
l'ultimo passa al primo. Per il sottoinsieme gia ammesso il passo e +1.

Il motore ammette intervalli risultanti validi, non vuoti, entro 0..32767.
Rifiuta preventivamente intervalli invertiti, sorgenti sconosciute e
catene con istruzioni non supportate. Gli intervalli sono per istanza;
l'animazione automatica dei cloni rimane esclusa dal sottoinsieme attuale.
Non viene forzato il fotogramma corrente quando cambia l'intervallo.

I quattro comandi originali nello script 1 di P511 sono [5,0,1],
[5,1,2], [5,2,3], [5,2,3], tutti con ritardo -1. Lo sprite 5 ha quattro
fotogrammi e temporizzazione [500,1,0]. La verifica nativa esegue ciascun
comando isolatamente e verifica quattro passi, il limite 499/500 ms,
la conservazione di frame/timer, il clamp e il rifiuto atomico.
verify_range_reference.py ricostruisce quattro immagini con Pillow dai
file originali: evidence/range contiene PNG e hash RGB888/RGB565.
Il test nativo confronta la composizione con questi hash mantenendo gli
altri sprite ai fotogrammi iniziali; non esegue l'intero enigma P511.
''';p.write_text(s)
p=Path('work/fresh-20260913/package_v19.py');s=p.read_text().replace('v19','v20');s=s.replace("assert 'stop verification: PASS'", "assert 'range verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'stop verification: PASS'");p.with_name('package_v20.py').write_text(s)
