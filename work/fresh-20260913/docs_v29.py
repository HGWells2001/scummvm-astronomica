from pathlib import Path
out=Path('outputs/astronomica-cleanroom')
p=out/'README.md'
s=p.read_text().replace('revisione 28.', 'revisione 29.')
a=s.index('Il file PLACES/P508/S9.WAV manca')
b=s.index('\n\n',a)
s=s[:a]+"La precedente diagnosi di un suono mancante era errata: il comando 9 [9]\nseleziona S8.WAV, presente nei dati originali. La revisione 29 corregge\nla conversione e rimuove l'eccezione introdotta nella revisione 27."+s[b:]
s=s.replace('riproduce S3;', 'riproduce S2;').replace('riproduce S6 e poi S2', 'riproduce S5 e poi S1')
s+='''
## Revisione 29: corrispondenza dei suoni

Il caricatore originale sottrae 1 al numero serializzato dei comandi
audio 9 e 27. Il prototipo ometteva questa conversione e sceglieva il
file successivo. Ora P508 usa S8.WAV per la risposta corretta, S7.WAV
per quella errata e S6.WAV per il sottofondo selezionato dal comando 27 [7].
Il suono globale di completamento, chiamato direttamente dal motore,
rimane SOUNDS/S12.WAV.

La conversione e verificata sull'eseguibile originale e con prove native
di entrambi gli opcode, inclusi i limiti degli indici. Passano anche le
prove PCM, del sottofondo e dei due percorsi completi di P508. Le prove
automatiche usano SDL dummy: non costituiscono un ascolto manuale.
L'utente ha confermato che P508 e completabile nella prova interattiva;
questo non dimostra la completabilita degli altri enigmi.
'''
p.write_text(s)
p=out/'INTERPRETER.md';s=p.read_text()
a=s.index('Questo ammette i grafi degli script 0 e 2 di P508')
b=s.index('\n\nclickAt',a)
s=s[:a]+'''Questo ammette i grafi degli script 0 e 2 di P508 e i clic degli sprite
5 e 7. La diagnosi successiva di un S9.WAV mancante era errata: mancava
la conversione dell'indice nel prototipo. L'eccezione per un file assente
introdotta nella revisione 27 e stata rimossa nella revisione 29.
'''+s[b:]
s='''> Correzione revisione 29: le vecchie associazioni dirette fra argomenti
> serializzati audio e nomi dei file nelle sezioni storiche 14-28 sono
> superate dalla conversione descritta sotto. Non esiste piu l'eccezione
> per il presunto S9.WAV mancante di P508.

'''+s
s+='''
## Indici audio: revisione 29

La tabella di dispatch di `_read_command_mem` a 9:3528 porta opcode 9
a 9:306d (salto breve verso 9:30b0) e opcode 27 direttamente a 9:30b0.
Il lettore comune esegue `DEC EAX` a 9:30d3 e memorizza il primo argomento
decrementato. Il successivo `_playSound` riceve quindi gia l'indice del
file, non il valore serializzato. Evidenza riproducibile:
`probe_sound_index.py`, `evidence/sound-index.json`.

Il nostro ResourceReader conserva i dati grezzi. ScriptRunner converte
il primo argomento di 9/27 sia nella validazione del bersaglio sia
nell'azione emessa. Gli indici locali serializzati ammessi sono 1..900;
0 e 901 vengono rifiutati. Le chiamate interne dirette, incluso il suono
globale 912 di `_puzzle_successful`, non subiscono questa conversione.

P508: comando 9 [9] -> S8.WAV, 9 [8] -> S7.WAV, 27 [7] -> S6.WAV.
I riferimenti PCM aggiornati sono P510 S1/S2/S5 e P511 S11 per il loop.
I test controllano la conversione per entrambi gli opcode agli indici
1, 2, 9, 900, il rifiuto di 0/901, campioni e hash PCM, ripetizione
del loop, priorita del suono e i percorsi completi di P508. Compilazione
Release x64 e suite nativa superate. Nessuna prova di ascolto manuale.
'''
p.write_text(s)
base=Path('work/fresh-20260913')
(base/'package_v29.py').write_text((base/'package_v28.py').read_text().replace('v28','v29'))
