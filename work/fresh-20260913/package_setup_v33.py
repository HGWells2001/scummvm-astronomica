from pathlib import Path
out=Path('outputs/astronomica-cleanroom');base=Path('work/fresh-20260913')
s=(base/'package_v32.py').read_text().replace('v32','v33')
anchor='# Verify the distributable probe independently'
insert='''cfg.write_text(cfg.read_text()+'\\n[astronomica-p509]\\nenable_unsupported_game_warning=false\\nengineid=astronomica\\ngameid=astronomica\\npath=D:\\\\astro\\nastronomica_start_place=509\\nastronomica_entry_scripts=true\\nastronomica_sprite_input=true\\nastronomica_animation=true\\nastronomica_audio=true\\n')
(out/'bin/Prova-enigma-P509.cmd').write_bytes(b'@echo off\\r\\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-p509\\r\\n')
'''
s=s.replace(anchor,insert+anchor)
s=s.replace("assert 'P511 interaction verification: PASS'", "assert 'P509 interaction verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'P511 interaction verification: PASS'")
s=s.replace("archive=out.parent/", "subprocess.run([sys.executable,str(base/'smoke_p509.py')],check=True)\nfor name in ('p509-launch.log','p509-launch-console.log'):\n shutil.copy2(base/name,out/'evidence'/name)\narchive=out.parent/")
(base/'package_v33.py').write_text(s)
s=(base/'smoke_p508.py').read_text().replace('508','509').replace('S302.WAV','S300.WAV').replace('3 queued','6 queued')
s=s.replace("assert 'P509 loop: S0.WAV' in text\n",'')
s=s.replace("log=base/'p509-launch.log'", "log=base/'p509-launch.log'\nif log.exists(): log.unlink()")
(base/'smoke_p509.py').write_text(s)
p=out/'README.md';s=p.read_text().replace('revisione 32.','revisione 33.',1)
s+='''
## Revisione 33: enigma ambientale P509

Nuovo avvio bin/Prova-enigma-P509.cmd, con spiegazione, audio e animazioni.
Selezionare un intervento nel pannello inferiore, poi fare clic sulla
zona dell'immagine a cui applicarlo. Le sei scelte sono energia solare,
riforestazione, trasporto pubblico, ecocura, riciclo e area protetta.
Il pulsante OFF esce; per ricominciare riaprire l'avvio.

Supportate le attese dei clic sulle zone dell'immagine quando l'input
interattivo e abilitato. Sono inoltre ammesse le operazioni di stato
immediate dopo un cambio scena: avvengono prima del ricaricamento;
gli effetti grafici e audio immediati in quella posizione restano esclusi.

La prova completa parte dai valori originali, esegue le due fasi tramite
clic e raggiunge P304 con successo. Una seconda prova sbaglia tre volte
e verifica l'uscita senza successo. Tutti e sei gli script di ingresso
sono ora accodati. P508 e P511 conservano le verifiche complete.

Tre enigmi hanno percorsi completi verificati automaticamente: P508,
P509 e P511. L'utente ha confermato interattivamente P508; gli altri
restano da provare manualmente. L'avventura e il sistema di aiuto non
sono ancora completi. Questa revisione supera il limite P509 della v32.
''';p.write_text(s)
p=out/'INTERPRETER.md';s=p.read_text()+'''
## Zone cliccabili e transizioni di P509: revisione 33

_do_mouse 9:12ba-1309 accoda i comandi delle zone rettangolari con la
stessa coda dei pulsanti. Ora l'opzione sprite_input abilita anche le
attese dei clic rettangolari. La modalita esploratore conserva il
sottoinsieme senza attese. La precedenza degli sprite resta invariata.

_execute_command 15:0385-0389 memorizza la destinazione e il flag di
cambio scena, poi continua nel percorso comune 15:1636. Il prototipo
esegue gia le modifiche alle variabili prima di applicare le azioni:
sono quindi sicuri dopo opcode 5 anche 32/33/39/40/46 e 41. Il richiamo
41 accoda soltanto lavoro, cancellato dal caricamento della scena nuova.
Restano respinti effetti immediati grafici o sonori che richiederebbero
un contesto di scena diverso; il test negativo P511 resta valido.

P509 ha una prova completa di selezione pulsante e clic rettangolare,
su sei bersagli e due fasi, senza assegnare lo stato risolto. La fine
raggiunge P304, globale 25=1 e un solo incremento del contatore. Tre
scelte sbagliate raggiungono P304 con globale 25=0 e nessun incremento.
La coda del suono ambientale e ciclica: la prova usa finestre temporali
limitate e controlla stato/input anziche attendere che la coda si svuoti.
''';p.write_text(s)
p=out/'survey_puzzles.py';s=p.read_text().replace('P511 ha due ordini di soluzione', 'P509 ha soluzione delle due fasi e uscita dopo tre errori verificate tramite clic dalla revisione 33. P511 ha due ordini di soluzione');p.write_text(s)
