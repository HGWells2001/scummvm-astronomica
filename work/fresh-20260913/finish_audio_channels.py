"""Finalize audio routing only after the same executable passes every suite."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
log=work/'audio-channels.log';text=log.read_text()
assert log.stat().st_mtime>exe.stat().st_mtime and 'FAIL' not in text and 'Log closed successfully' in text
assert 'audio channel verification: PASS (6 muted music loops, 6 foreground replacements, controls restored)' in text
proof=json.loads((work/'audio-channels-proof.json').read_text());assert proof['status']=='PASS' and proof['unchanged']
for name,expected in proof['original_wav_sha256'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected,name
for name in ('audio-channels.log','audio-channels-proof.json'):shutil.copyfile(work/name,root/'evidence'/name)
validation=dict(date='2026-10-18',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),scenes=[505,508,519,524,526,528],music_loops=6,foreground_replacements=6,music_muted=True,music_volume=0,effects_volume=256,effects_unmuted=True,controls_restored=True,full_suite=True,
 scope='Looping WAVs use Music; foreground WAVs retain Effects and the original single-handle replacement behavior',
 limitations=['Mixer channel/control assertions use real WASAPI; this is not manual listening or a PCM amplitude measurement','No new Speech classification is inferred for foreground recordings','No original game media is included in the export'])
(root/'evidence/audio-channels-validation.json').write_text(json.dumps(validation,indent=2))
old_next=(root/'NEXT-STEPS.md').read_text()
p=subprocess.run([sys.executable,str(work/'finish_presentation.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-400:]);(root/'NEXT-STEPS.md').write_text(old_next)
note=('\n\n## Separate music control, 18 October 2026\n\n'
 'Looping background WAVs now use the ScummVM Music channel. Foreground recordings retain the Effects channel and replace the active loop as before. '
 'Six scenes pass with Music muted and volume zero, Effects audible, and all original controls restored afterward. '
 'Twelve original S0/S1 WAV hashes are unchanged. Presentation, compatible v1-v7 saves, prior-build slots, help/import and the full WASAPI suite pass on the same executable. '
 'This is automated channel/control verification; manual listening remains outstanding. See AUDIO-CHANNELS.md and evidence/audio-channels-validation.json.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=root/name;s=p.read_text()
 if '## Separate music control, 18 October 2026' not in s:s+=note
 p.write_text(s)
heading=('# Ripresa: controllo Musica separato, 18 ottobre 2026\n\n'
 'Loop WAV sul canale Musica; registrazioni in primo piano sul canale Effetti, con sostituzione originale a singolo canale.\n'
 'Sei scene con Musica muta/volume zero, 12 WAV originali invariati, ripristino controlli PASS.\n'
 'Presentazione completa, salvataggi v1-v7, slot precedenti, import, aiuto e suite WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_audio_channels.py. Test: check_audio_channels.py e check_audio_channel_regressions.py.\n'
 'Prossimo: P528-SAVE-PLAN.md, verifica audiovisiva manuale e tipografia aiuto. Non rieseguire finalizzatori storici.\n'
 'Nessuna percentuale globale attendibile. Protocollo: AI_MODEL_CHECKPOINT.md.\n\n')
p=root/'NEXT-STEPS.md';s=p.read_text()
if not s.startswith('# Ripresa: controllo Musica separato'):s=heading+s
p.write_text(s)
p=Path('AI_MODEL_CHECKPOINT.md');s=p.read_text();s+='\nAudio verificato: loop sul canale Musica, primo piano sul canale Effetti; sei scene con Musica muta e volume zero, 12 WAV invariati. Suite completa PASS. Checkpoint attuale finish_audio_channels.py. Configurazione AI corrente sufficiente; nessun cambio richiesto o applicato. Prossimo P528-SAVE-PLAN.md.\n';p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Audio channels verified 18 October 2026. Six muted-music loops and six foreground replacements; original controls restored and twelve original WAV hashes unchanged. Presentation, v1-v7 saves, previous slots and full WASAPI suite PASS on the same executable. No tests running. See NEXT-STEPS.md and AI_MODEL_CHECKPOINT.md.\n')
print('Audio channels checkpoint PASS')
