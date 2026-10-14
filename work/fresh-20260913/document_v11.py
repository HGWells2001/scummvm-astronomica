from pathlib import Path
root=Path('outputs/astronomica-cleanroom')
p=root/'README.md';s=p.read_text().replace('revisione 10. Progresso complessivo stimato: circa 29%', 'revisione 11. Progresso complessivo stimato: circa 31%')
s=s.replace('sottoinsieme di quindici opcode', 'sottoinsieme di sedici opcode').replace('31, 32, 42,', '31, 32, 41, 42,')
s=s.replace('- Lettore Python indipendente', '- Timer in millisecondi e richiami accodati degli script: lampeggio automatico completo di P29.\n- Lettore Python indipendente')
s=s.replace('non simula il suo lampeggio automatico, ancora non implementato.', 'resta una prova manuale. Per il lampeggio automatico usare il nuovo avvio descritto sotto.')
s=s.replace('Il prototipo parte da P1.', '`bin/Prova-lampeggio.cmd` apre P29 con il suo unico script di ingresso originale completo. Il display lampeggia automaticamente con il ritardo dichiarato di 600 ms, oltre ai passaggi della coda. Non serve premere V. La verifica controlla i limiti 599/600 e 1199/1200 ms e confronta i pixel degli stati acceso/spento con i riferimenti indipendenti. I pulsanti TV/VCR della scena richiedono altri comandi e non sono ancora utilizzabili.\n\nIl prototipo parte da P1.')
p.write_text(s)
p=root/'INTERPRETER.md';s=p.read_text()
s=s.replace('La durata reale dei tick non è ancora stabilita. La funzione C++ di verifica usa tick astratti; l\'integrazione interattiva rifiuta ritardi positivi.', 'Dalla revisione 11 il timer è identificato in millisecondi; le continuazioni temporizzate sono abilitate per gli script di ingresso ammessi. I clic conservano per ora il sottoinsieme senza ritardi positivi.')
s=s.replace('nessuna scena con script, nel corpus rigorosamente decodificato, ha ancora tutte le sue sequenze di ingresso coperte dal sottoinsieme attuale.', 'fino alla revisione 10 nessuna scena con script aveva tutte le sequenze di ingresso coperte; la revisione 11 esegue integralmente quella di P29.')
s+='''

## Timer e richiami: revisione 11

Il modulo 3 della tabella import NE originale è MMSYSTEM. `_handle_pending`
15:1b48 richiama il suo ordinal 607: `timeGetTime`, identificato dalla
[tabella ABI Win16 mantenuta da Wine](https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/mmsystem.dll16/mmsystem.dll16.spec).
La [documentazione Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timegettime)
specifica millisecondi e rollover a 32 bit. `analyze_timing.py` riestrae i nomi
dei moduli dal solo ASTRO.EXE originale, verificandone SHA-256; le chiamate
sono visibili nei disassemblati riproducibili già inclusi.

L'opcode 41, handler 15:118b, legge l'indice zero-based dalla tabella a
DS:0cd8 e chiama `_pend_command`. Non chiama `_do_command`: il programma
richiamato attende un altro passaggio della coda. Il motore usa getMillis()
in esecuzione normale e un orologio controllato nelle verifiche native.

Prima di avviare una catena si verifica tutto il grafo dei programmi
raggiungibili, gestendo anche i cicli senza ricorsione. Indici inesistenti,
programmi vuoti, comandi sconosciuti o bersagli non disponibili causano il
rifiuto prima di qualsiasi effetto. Un richiamo aggiunge lavoro alla coda,
senza ricorsione nell'esecuzione.

Limite esplicito: `_pend_command` copia il timestamp del template, non lo
reinizializza. Finché non è ricostruito il suo intero ciclo di vita, vengono
rifiutati i programmi richiamati e gli ingressi con primo ritardo positivo.
Le continuazioni positive, il cui timestamp è aggiornato in 15:1679, sono
supportate. L'API di test mantiene separatamente i ritardi iniziali astratti.

Il test carica P29 originale ed esegue l'intero script flash_light: condizioni,
show/hide, assegnazione dello stato e autorichiamo dopo 600 ms. Controlla
assenza di esecuzione anticipata, rinvio del richiamo al passaggio successivo,
ritorno allo stato iniziale e hash RGB degli stati. Include inoltre test
sintetici per richiamo ciclico, indice errato e rifiuto atomico di una catena
che richiama codice non supportato. Tutti i test precedenti restano attivi.

Questo verifica un'animazione guidata dallo script originale, non il supporto
generale dell'avanzamento automatico dei fotogrammi o della scena TV/VCR.
'''
p.write_text(s)
base=Path('work/fresh-20260913')
s=(base/'package_v10.py').read_text().replace('v10','v11')
anchor='# Verify the distributable probe independently against the same original.'
s=s.replace(anchor,'''cfg.write_text(cfg.read_text()+'\\n[astronomica-blink]\\nengineid=astronomica\\ngameid=astronomica\\npath=D:\\\\astro\\nastronomica_start_place=29\\nastronomica_entry_scripts=true\\n')
(out/'bin/Prova-lampeggio.cmd').write_bytes(b'@echo off\\r\\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-blink\\r\\n')
'''+anchor)
s=s.replace("assert 'frame verification: PASS'", "assert 'timer verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'frame verification: PASS'")
(base/'package_v11.py').write_text(s)
