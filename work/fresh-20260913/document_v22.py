from pathlib import Path
p=Path('outputs/astronomica-cleanroom/README.md');s=p.read_text().replace('revisione 21. Progresso complessivo stimato: circa 43%', 'revisione 22. Progresso complessivo stimato: circa 44%').replace('sottoinsieme di 27 opcode', 'sottoinsieme di 28 opcode').replace('15, 16, 17, 25, 26,', '15, 16, 17, 23, 25, 26,');s=s.replace('- Lettore Python indipendente,', '- Prima operazione personalizzata di completamento P511: suono sincrono, variabile globale 27 e conteggio senza duplicati.\n- Lettore Python indipendente,');s+='''
## Revisione 22

Implementata l'operazione personalizzata 25 dell'opcode 23, limitatamente
a P511 e con audio abilitato. Il suono globale SOUNDS/S12.WAV termina
prima dell'aggiornamento del risultato e della continuazione dei comandi.
Le prove verificano esecuzione singola, ripetizione, flag gia non nullo,
ritardi successivi, persistenza fra scene e azzeramento entrando in P1.

La prova esegue il comando originale isolatamente: non costituisce una
soluzione giocabile dell'enigma. Il grafo completo P511 resta escluso,
fra l'altro per il cambio scena seguito da una diramazione immediata
e per i comandi delle immagini. Non viene aggiunto un nuovo avvio.
''';p.write_text(s)
p=Path('outputs/astronomica-cleanroom/INTERPRETER.md');s=p.read_text();s+='''
## Completamento P511: revisione 22

La tabella a 4:6c94 seleziona per P511 l'handler 4:57c6. Questo controlla
il DWORD +0x76 della struttura puntata da DS:07a8, richiama
_puzzle_successful soltanto quando vale zero, quindi scrive 1. Lo stesso
puntatore viene usato da _clear_globals (9:408c), che azzera 100 DWORD
a partire da +0x0a: +0x76 corrisponde quindi alla variabile globale 27,
non a uno stato separato. Anche valori negativi/nonzero vengono portati
a 1, senza ripetere il suono o incrementare il contatore.

_puzzle_successful (3:39ae) chiama _playSound(912), poi incrementa DS:0153.
Il percorso originale per id>=900 usa SOUNDS/S%d.WAV sottraendo 900.
Il suono 912 rientra nell'eccezione sincrona di _playSound: dura circa
2,206 secondi. Il riferimento indipendente e evidence/success.json:
24320 campioni mono 11025 Hz, hash PCM16LE 3dcde548.

L'interprete ammette soltanto 23 [25,0,0,0,0,0] quando il motore fornisce
il gestore P511 e ha validato il WAV PCM globale con audio abilitato.
Gli altri contesti e sottocomandi personalizzati restano esclusi. Il
callback applica prima gli effetti gia accodati, attende il mixer senza
eseguire altri script, incrementa il contatore e restituisce il tempo
successivo al suono. Solo dopo viene scritto il flag globale; eventuali
continuazioni temporizzate partono da quel tempo. Durante l'attesa resta
possibile chiudere l'applicazione; gli altri input non vengono eseguiti.
Il contatore e per la sessione e non esistono ancora salvataggi.

La verifica usa il comando originale isolato: rifiuto atomico di una
catena sconosciuta, prima esecuzione, ripetizione senza nuovo suono,
normalizzazione di -2, successore a 999/1000 ms dopo la fine del suono,
persistenza della globale cambiando scena, reset P1 e rifiuto senza audio.
Il test usa SDL dummy: prova l'attesa del mixer, non l'ascolto. La suite
precedente passa. Il grafo completo P511 resta escluso: include ancora
una transizione seguita da opcode 45 immediato e comandi di immagini non
supportati. Nessun enigma completo viene dichiarato giocabile.
''';p.write_text(s)
p=Path('work/fresh-20260913/package_v21.py');s=p.read_text().replace('v21','v22');s=s.replace("assert 'loop verification: PASS'", "assert 'success verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'loop verification: PASS'");p.with_name('package_v22.py').write_text(s)
