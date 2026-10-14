from pathlib import Path
r=Path('outputs/astronomica-cleanroom')
p=r/'README.md';s=p.read_text().replace('revisione 13. Progresso complessivo stimato: circa 35%', 'revisione 14. Progresso complessivo stimato: circa 37%')
s=s.replace('sottoinsieme di diciotto opcode', 'sottoinsieme di diciannove opcode').replace('6, 7, 15,', '6, 7, 9, 15,')
s=s.replace('enigmi, filmati, audio, inventario', 'enigmi, filmati, audio completo, inventario')
s=s.replace('- Lettore Python indipendente', '- Riproduzione dei suoni PCM locali tramite ScummVM, associata ai clic originali dei pulsanti P510.\n- Lettore Python indipendente')
s=s.replace('Il prototipo parte da P1.', '''`bin/Prova-audio.cmd` apre P510 con immagini iniziali, animazioni, mouse
e suoni locali abilitati. Il pulsante vicino a **(35,380)** riproduce S3;
quello vicino a **(600,380)** riproduce S6 e poi S2 secondo i ritardi
dello script originale. Ogni nuovo suono sostituisce il precedente.
Funzionano anche le prove di selezione e dell'indicatore animato.
L'enigma resta incompleto: alcuni pulsanti e le sequenze d'ingresso
contengono ancora comandi non implementati. L'opzione audio è
`astronomica_audio=true`; non è attiva negli avvii precedenti.

Il prototipo parte da P1.''');p.write_text(s)
p=r/'INTERPRETER.md';s=p.read_text();s+='''

## Suoni locali: revisione 14

L'opcode 9 entra in 15:04a8, chiama `_in_custom` (18:18ba, qui senza
effetti) e passa il primo argomento a 16 bit a `_playSound` (9:3b07).
Quest'ultima usa direttamente l'id nel nome del file: il ramo locale
costruisce `%s/PLACES/P%ld/S%d.WAV`, stringa originale DS:04ad.
La tabella delle dichiarazioni sonore della scena non viene consultata
da questo ramo. L'argomento 3 in P510 riproduce quindi P510/S3.WAV.

La chiamata MMSYSTEM ordinal 2 usa flag 3 nel ramo normale, riproduzione
asincrona senza suono predefinito. Il precedente suono viene interrotto.
Il motore utilizza un solo handle del mixer ScummVM; un nuovo avvio ferma
quell'handle, mentre caricamento di una nuova scena e distruzione del
motore liberano il suono. `_do_place` invoca `_stop_sounds` in 9:06a6.

La modalità opt-in `astronomica_audio=true` ammette solo WAV PCM locali
riconosciuti dal lettore ScummVM e argomenti 0..899. La disponibilità viene
registrata al caricamento e controllata prima di eseguire una sequenza:
un file mancante fa rifiutare l'intero script. Restano esclusi gli id globali
900+, i casi sincroni P505/S2..S10 e P512/S14, e la pausa/ripresa del filmato
presente nell'originale. Non viene rivendicato il supporto audio completo,
del suono d'ingresso o dell'audio di fondo. I filmati non sono ancora attivi.

Il test nativo legge P510/S2, S3 e S6 con il decoder ScummVM e confronta
numero dei campioni, frequenza 11025 Hz, mono, e hash dei campioni PCM16LE.
`verify_audio_reference.py` genera gli stessi riferimenti indipendentemente
con il modulo Python wave, partendo dai WAV originali PCM8 unsigned:
3627/4272/23808 campioni, hash `1c898683`/`eed1c407`/`01fbde02`.
Il rapporto `evidence/audio.json` contiene anche SHA-256 dei file originali.

La prova dei clic usa i programmi originali completi degli sprite 3 e 5:
S3 viene avviato dopo il passaggio in coda; S6 viene sostituito da S2
soltanto dopo 150 ms di attesa per lo sblocco e altri 1300 ms. Si verificano
handle attivo, numero degli avvii, rifiuto di S899 mancante e arresto al
cambio scena. Il backend di verifica è SDL dummy: questi controlli
verificano decodifica e consegna al mixer, non un ascolto dagli altoparlanti.
''';p.write_text(s)
base=Path('work/fresh-20260913');s=(base/'package_v13.py').read_text().replace('v13','v14')
anchor='# Verify the distributable probe independently against the same original.'
s=s.replace(anchor,'''cfg.write_text(cfg.read_text()+'\\n[astronomica-audio]\\nengineid=astronomica\\ngameid=astronomica\\npath=D:\\\\astro\\nastronomica_start_place=510\\nastronomica_sprite_input=true\\nastronomica_animation=true\\nastronomica_audio=true\\n')
(out/'bin/Prova-audio.cmd').write_bytes(b'@echo off\\r\\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-audio\\r\\n')
'''+anchor)
s=s.replace("assert 'animation verification: PASS'", "assert 'audio verification: PASS' in (out/'evidence/runtime.log').read_text()\nassert 'animation verification: PASS'")
(base/'package_v14.py').write_text(s)
