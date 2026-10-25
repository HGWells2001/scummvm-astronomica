"""Record P511 v21 only after complete same-build native WASAPI verification."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

r=Path('outputs/astronomica-cleanroom')
w=Path('work/fresh-20260913')
exe=w/'build/Releasex64/scummvm.exe'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=next(line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if line.startswith('Modello dichiarato'))
proof=json.loads((w/'p511-save-proof.json').read_text())
assert proof['status']=='PASS' and proof['exe_sha256']==digest(exe)
assert proof['metadata_listed'] and proof['slot']==20 and not proof['diagnostic']
assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
assert proof['truncations']==proof['corruptions']==6256
for key in ('boundaries','history_boundaries','dormant_boundaries','ordinary_boundaries','busy_rejections','invalid_states','natural_voice_ends','retained_image_boundaries','frame_history_boundaries','animation_boundaries','successor_checks','future_outcome_checks','timer_cases'):
    assert proof[key]>0,key
assert proof['choice_controls']==8 and proof['future_outcome_checks']>=4
assert (proof['dial_settings'],proof['cloud_settings'],proof['type_settings'])==(16,14,4)
assert proof['ambient_deadline_cases']==3
assert proof['variant_fixture_unchanged'] and proof['music_restart'] and proof['extended_atomic_state']
previous=json.loads((w/'p509-previous-slot-proof.json').read_text())
assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==digest(exe)
for name,marker in [('p511-saves.log','P511 save verification: PASS'),('p511-saves-startup.log','P511 startup save: PASS'),('p509-previous-slot.log','P509 startup save: PASS')]:
    path=w/name
    text=path.read_text()
    assert path.stat().st_mtime>exe.stat().st_mtime and marker in text and 'FAIL' not in text
    assert text.rstrip().endswith('--- Log closed successfully.') and 'Using SDL Audio Driver "wasapi"' in text
for src,dst in [('p511-saves.log','p511-saves-runtime.log'),('p511-saves-startup.log','p511-saves-startup.log'),('p511-save-proof.json','p511-save-proof.json'),('p509-previous-slot.log','p509-previous-slot.log'),('p509-previous-slot-proof.json','p509-previous-slot-proof.json')]:
    shutil.copyfile(w/src,r/'evidence'/dst)
validation=dict(proof)
validation.update(date='2026-10-25',format_version=21,payload_bytes=6256,scene=511,full_suite=True,
    fresh_process_slot=20,byte_corruptions=proof['corruptions'],invalid_checksummed_states=proof['invalid_states'],
    scope='idle_script_p511',compatibility='Versions1-20 retained; genuine frozen verified v20 slot19 read unchanged',
    limitations=['Only ordinary P511 idle-script boundaries with criterion mask0..6',
        'Foreground audio, queued work, startup and success transitions remain excluded',
        'No complete manual audiovisual playthrough'])
(r/'evidence/p511-saves-validation.json').write_text(json.dumps(validation,indent=2))
subprocess.run([sys.executable,str(r/'probe_p511_save.py'),'--scene','511','--out',str(r/'evidence/p511-save-original.json')],check=True)
# New validation must exist before older finishers regenerate shared coverage.
subprocess.run([sys.executable,str(w/'finish_p509_saves.py')],check=True)
heading=('# Ripresa: salvataggi P511,25 ottobre2026\n\n'
    f'Formato v21:6256byte,{proof["boundaries"]} ripristini verificati. '
    'Conserva immagini CLOUD, fotogrammi e intervalli anche discordanti, animazioni nascoste, clock, valori ereditati e stato dormiente. Slot20 in nuovo processo PASS.\n'
    'Compatibilita v1-v20, vero slotv20 congelato, rifiuto atomico dei file alterati, suite completa WASAPI e avvio normale sullo stesso eseguibile. Altre code, voci attive e transizioni restano escluse.\n'
    'Checkpoint:finish_p511_saves.py;check_p511_saves.py;check_p511_regressions.py;P511-SAVE-FORMAT.md. Non eseguire finalizzatori precedenti da soli.\n'
    'Venticinque scene con salvataggi verificati non misurano il completamento globale. Restano altri salvataggi, tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED.\n\n')
path=r/'NEXT-STEPS.md'
text=path.read_text()
path.write_text(text if text.startswith('# Ripresa: salvataggi P511') else heading+text)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,25 ottobre2026\n\n'+model+'\n\n'+heading+
    'Originali D:/astro; solo cleanroom dal13settembre2026, senza prototipi o tentativi esclusi. Fermarsi vicino1% della quota limitante; nessun acquisto o riscatto reset.\n')
path=r/'P511-SAVE-PLAN.md'
text=path.read_text()
note='## Verified P511 save support,25 October2026\n\nVersion21 is verified; see P511-SAVE-FORMAT.md and evidence/p511-saves-validation.json. The candidate investigation below remains history.\n\n'
path.write_text(text if text.startswith(note) else note+text)
path=r/'P511-SAVE-FORMAT.md'
text=path.read_text().replace('Status: candidate, SDL only; official native suite pending.','Status: verified25October2026; same-build native WASAPI and complete compatible suite PASS.')
path.write_text(text)
note=('\n\n## P511 saves,25 October2026\n\n'
    f'Version21 preserves {proof["boundaries"]} measured ordinary P511 boundaries with retained cloud image, independent frame/range history and exact timed continuation. '
    'Fresh-process slot20 and unchanged genuine frozen v20 compatibility pass. Original frame ranges, hidden animations and timer epochs are preserved. '
    'Foreground audio, queued work and success transitions remain excluded. All6256 truncations and6256 byte corruptions reject atomically. Complete same-build WASAPI suite PASS.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
    path=r/name;text=path.read_text();path.write_text(text if '## P511 saves,25 October2026' in text else text+note)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
    subprocess.run([sys.executable,str(w/name)],check=True)
(r/'RUN-IN-PROGRESS.md').write_text('P511 v21 saves verified25October2026. Complete same-build native WASAPI suite, fresh-process slot20 and genuine frozen v20 slot PASS. Publication requires export verification. Newest finisher finish_p511_saves.py. Automation remains PAUSED.\n')
print('P511 v21 checkpoint PASS',flush=True)


