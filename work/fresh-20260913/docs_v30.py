from pathlib import Path
out=Path('outputs/astronomica-cleanroom');base=Path('work/fresh-20260913')
p=out/'README.md';s=p.read_text().replace('revisione 29.', 'revisione 30.',1)
s+='''
## Revisione 30: spiegazione iniziale e musica di P508

Ripristinato l'audio automatico all'ingresso nelle scene di tipo 0 con
script e audio abilitati. P508 dichiara come introduzione S302.WAV:
il file e identico byte per byte a S1.WAV (6,60 secondi). La voce viene
riprodotta per intero prima di avviare gli script. S0.WAV e il sottofondo
locale predefinito, ripetuto quando non sono attivi altri suoni e dopo
il limite temporale originale. Gli effetti lo interrompono; poi riprende.
La selezione esplicita di altri sottofondi resta affidata agli script.

Avvio: bin/Prova-enigma-P508.cmd. Le prove automatiche verificano
l'introduzione completa, l'avvio degli script, la musica, le interruzioni
e la ripresa, oltre ai due percorsi completi dell'enigma. Non e una prova
di ascolto manuale. Le regole di musica globale degli altri tipi di scena
e quelle relative al ripristino di salvataggi restano da implementare.
''';p.write_text(s)
p=out/'INTERPRETER.md';s=p.read_text()+'''
## Audio automatico della scena: revisione 30

ResourceReader ora conserva flag e ID dell'introduzione, prima scartati.
Nell'originale _load_place 9:156b assegna 0 al sottofondo per il modo 0;
9:1c45-1c4b passa direttamente l'ID dell'introduzione a _playSound.
9:2f22-2fa5 attende il termine del suono nelle scene senza filmati.
La provenienza da P408 esclude l'introduzione (9:1c26). Il contatore
relativo al caricamento salvato non e ancora modellato dal prototipo.

Il ramo implementato e limitato alle scene modo 0, con entry_scripts
e audio abilitati. L'attesa aggiorna lo schermo e gestisce la chiusura;
gli input di gioco non vengono accodati durante la spiegazione. Poi
avvia gli script e applica il criterio esistente del loop: canale libero
e oltre 5000 ms per le scene degli enigmi. Non viene creato un secondo
canale musicale, assente nel comportamento originale sndPlaySound.

P508 dichiara ID diretto 302: S302.WAV e S1.WAV hanno lo stesso SHA256.
probe_entry_audio.py riproduce questa verifica e controlla le istruzioni
originali; evidence/entry-audio.json conserva riferimenti e dati PCM.
La prova nativa entry audio attraversa loadPlace con le opzioni reali,
attende tutta l'introduzione e controlla script, S0, precedenza degli
effetti, ripresa, pulizia al cambio scena e audio disabilitato.
''';p.write_text(s)
p=base/'smoke_p508.py';s=p.read_text().replace('timeout=4','timeout=12');s=s.replace("assert 'resource explorer: P508' in text", "assert 'resource explorer: P508' in text\nassert 'P508 introduction: S302.WAV' in text\nassert 'P508 loop: S0.WAV' in text\nassert 'P508 entry scripts: 3 queued, 0 skipped' in text");p.write_text(s)
s=(base/'package_v29.py').read_text().replace('v29','v30')
s=s.replace("assert 'cursor verification: PASS'", "assert 'entry audio verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'cursor verification: PASS'")
(base/'package_v30.py').write_text(s)
