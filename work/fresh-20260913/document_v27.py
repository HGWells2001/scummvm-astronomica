from pathlib import Path
p=Path('outputs/astronomica-cleanroom/survey_puzzles.py');s=p.read_text().replace('Nessun enigma completo e stato verificato giocabile.', 'P508 Astronomy vs Astrology ha due percorsi completi verificati tramite input simulato nel motore: otto risposte corrette e uscita dopo tre errori. Non e una prova manuale nella finestra di gioco.');s=s.replace('Non sono prove di risoluzione integrale degli enigmi.', 'Queste prove precedenti non sono soluzioni integrali; dalla revisione 27 P508 ha anche prove complete di risposte corrette e di tre errori.');p.write_text(s)
p=Path('outputs/astronomica-cleanroom/README.md');s=p.read_text().replace('revisione 26.','revisione 27.',1).replace('Nessun enigma completo e ancora verificato giocabile.', 'P508 Astronomy vs Astrology ha percorsi completi verificati automaticamente attraverso i clic; il gioco complessivo resta incompleto.');s+='''
## Revisione 27: prova dell'enigma P508

Aprire bin/Prova-enigma-P508.cmd. Viene avviato Astronomy vs Astrology
con immagini, animazione, audio disponibile, clic e script originali.
Leggere la frase nel pannello inferiore e scegliere ASTRONOMY oppure
ASTROLOGY. Otto risposte corrette completano la sequenza; tre errori
fanno uscire senza successo. Per ricominciare riaprire questo avvio.

Entrambi i percorsi sono verificati automaticamente tramite gli stessi
metodi di input e temporizzazione usati dal gioco, senza impostare lo
stato risolto. La prova non sostituisce un controllo manuale nella finestra
Windows e non rende completabile l'intera avventura.

Il file PLACES/P508/S9.WAV manca nella copia originale: il comando della
risposta corretta prosegue senza quel suono, come fa l'handler originale
quando la riproduzione fallisce. Non viene fornito un audio sostitutivo.
''';p.write_text(s)
p=Path('outputs/astronomica-cleanroom/INTERPRETER.md');s=p.read_text();s+='''
## P508: risposte e conclusione, revisione 27

La restrizione sui comandi immediati dopo una transizione controllava
l'intero suffisso e rifiutava anche effetti raggiungibili solo in un
passaggio futuro della coda. Ora la validazione segue i collegamenti
di confronto/else/end, esplorando entrambi gli esiti possibili, e si
ferma quando raggiunge una continuazione con delay diverso da -1.
Restano rifiutati effetti immediati realmente raggiungibili prima del
ricaricamento. Il test della coda non sicura di P511 continua a passare.

Questo ammette i grafi degli script 0 e 2 di P508 e i clic degli sprite
5 e 7. E emerso un secondo blocco reale: i due clic chiamano suono locale
9 per una risposta corretta, ma PLACES/P508/S9.WAV non esiste. _playSound
(9:3b8e-3c14) tenta la riproduzione e non propaga il fallimento al comando.
Una sola eccezione esplicita ammette quindi opcode 9 [9] nella scena
508 quando il file e assente e l'audio e abilitato: ferma il suono
precedente, aggiorna il timestamp e prosegue senza inventare campioni.
Il caso non autorizza loop 27 [9], file presenti malformati, altri file
mancanti o altri contesti. Il test verifica anche tale esclusione.

clickAt richiama ora clickAtTime con il tempo corrente; i test possono
fornire un orologio deterministico senza modificare gli script. La nuova
prova carica P508, accoda tutti e tre i programmi di ingresso originali
e usa gli hit test e i clic sui pulsanti. Non forza i contatori di
risposte o la variabile di successo. Un percorso risponde correttamente
otto volte, segue animazioni e script fino a P388 e controlla globale
24=1 e un incremento del contatore. L'altro sbaglia tre volte e verifica
P388 con globale 24=0 e nessun incremento. Gli stati intermedi verificano
conteggi, sblocco input e coda esaurita; esistono limiti alle iterazioni
per evitare che un ciclo errato faccia passare il test.

La prova usa tempo simulato e SDL dummy, non input fisico o ascolto.
L'avvio Prova-enigma-P508.cmd rende disponibile la stessa configurazione
per la prova interattiva. E il primo percorso di soluzione di un enigma
verificato in questo prototipo; non e una verifica dell'intera avventura.
''';p.write_text(s)
p=Path('work/fresh-20260913/package_v26.py');s=p.read_text().replace('v26','v27');s=s.replace("assert 'staged image verification: PASS'", "assert 'P508 interaction verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'staged image verification: PASS'");needle='# Verify the distributable probe independently against the same original.';addition='''cfg.write_text(cfg.read_text()+'\\n[astronomica-p508]\\nengineid=astronomica\\ngameid=astronomica\\npath=D:\\\\astro\\nastronomica_start_place=508\\nastronomica_entry_scripts=true\\nastronomica_sprite_input=true\\nastronomica_animation=true\\nastronomica_audio=true\\n')
(out/'bin/Prova-enigma-P508.cmd').write_bytes(b'@echo off\\r\\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-p508\\r\\n')
''';assert needle in s;s=s.replace(needle,addition+needle);p.with_name('package_v27.py').write_text(s)
