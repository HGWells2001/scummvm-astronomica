from pathlib import Path
out=Path('outputs/astronomica-cleanroom');base=Path('work/fresh-20260913')
s=(base/'package_v30.py').read_text().replace('v30','v31')
anchor='# Verify the distributable probe independently'
insert='''cfg.write_text(cfg.read_text()+'\\n[astronomica-p511]\\nenable_unsupported_game_warning=false\\nengineid=astronomica\\ngameid=astronomica\\npath=D:\\\\astro\\nastronomica_start_place=511\\nastronomica_entry_scripts=true\\nastronomica_sprite_input=true\\nastronomica_animation=true\\nastronomica_audio=true\\n')
(out/'bin/Prova-enigma-P511.cmd').write_bytes(b'@echo off\\r\\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-p511\\r\\n')
'''
assert anchor in s;s=s.replace(anchor,insert+anchor)
s=s.replace("assert 'entry audio verification: PASS'", "assert 'P511 interaction verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'entry audio verification: PASS'")
s=s.replace("archive=out.parent/", "subprocess.run([sys.executable,str(base/'smoke_p511.py')],check=True)\nfor name in ('p511-launch.log','p511-launch-console.log'):\n shutil.copy2(base/name,out/'evidence'/name)\narchive=out.parent/")
(base/'package_v31.py').write_text(s)
s=(base/'smoke_p508.py').read_text().replace('508','511').replace('timeout=12','timeout=28').replace('3 queued','5 queued')
(base/'smoke_p511.py').write_text(s)
p=out/'README.md';s=p.read_text().replace('revisione 30.', 'revisione 31.',1)
s+='''
## Revisione 31: secondo enigma, P511

Avvio dedicato: bin/Prova-enigma-P511.cmd. Include la spiegazione iniziale
originale (circa 21 secondi), musica, animazioni e pulsanti. I controlli
inferiori regolano distanza della Luna, vento e barometro. Il pulsante
OFF consente di uscire dall'enigma; per ricominciare riaprire l'avvio.

P511 ora ha due percorsi di soluzione completi verificati con clic sui
pulsanti originali, a partire dai valori iniziali del file. Il test non
imposta lo stato risolto. Verifica anche limiti delle regolazioni,
inversione delle scelte e uscita senza successo. Questo supera la sola
prova della sequenza finale delle revisioni precedenti.

P508 e P511 sono quindi due enigmi con percorsi completi verificati
automaticamente. Solo P508 ha, finora, la conferma interattiva dell'utente.
Il pulsante ? di P511 raggiunge P408, ma il sistema di aiuto e il ritorno
da esso non sono ancora verificati. Non e ancora giocabile tutta l'avventura.
''';p.write_text(s)
p=out/'INTERPRETER.md';s=p.read_text()+'''
## P511 dal primo clic alla conclusione: revisione 31

La verifica precedente della sequenza finale rimane come controllo
temporale separato. La nuova prova carica invece tutte le condizioni
originali e accoda i cinque template di ingresso. Usa clickAtTime e
spriteAt, senza scritture nelle variabili locali o nella globale 27.
Ogni interazione attraversa input, scheduler, grafi degli script e azioni.

Due ordini di soluzione raggiungono P388 con globale 27=1 e incremento
singolo del contatore; OFF raggiunge P388 senza successo. I casi intermedi
coprono quattro posizioni della Luna, vento 0..15, barometro 52..0 a passi
di 4, limiti superiori/inferiori e inversioni. Le attese hanno un limite
di iterazioni, cosi una coda bloccata fallisce la prova.

Questa revisione aggiunge l'avvio dedicato e le prove complete: non richiede
nuovi opcode. L'avvio distribuito viene eseguito separatamente con SDL
dummy fino al termine dell'introduzione, verificando cinque template
accodati senza esclusioni e la ripresa della musica S0.WAV.
''';p.write_text(s)
p=out/'survey_puzzles.py';s=p.read_text().replace('P508 Astronomy vs Astrology ha due percorsi completi verificati', 'P511 ha due ordini di soluzione e uscita senza successo verificati tramite clic originali. P508 Astronomy vs Astrology ha due percorsi completi verificati')
s=s.replace('P511 ha la sequenza finale verificata con stato risolto imposto dal test.', 'P511 ha anche due soluzioni complete e uscita senza successo verificate tramite clic dalla revisione 31; la vecchia prova della sola sequenza finale resta separata.')
p.write_text(s)
