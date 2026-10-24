"""Record P509 v20 only after complete same-build native WASAPI verification."""
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
proof=json.loads((w/'p509-save-proof.json').read_text())
assert proof['status']=='PASS' and proof['exe_sha256']==digest(exe)
assert proof['metadata_listed'] and proof['slot']==19 and not proof['diagnostic']
assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
assert proof['truncations']==proof['corruptions']==4540
for key in ('boundaries','history_boundaries','dormant_boundaries','ordinary_boundaries','busy_rejections','invalid_states','natural_voice_ends','retained_image_boundaries','target_history_boundaries','animation_boundaries','successor_checks','future_outcome_checks','timer_cases'):
    assert proof[key]>0,key
assert proof['choice_controls']==6 and proof['future_outcome_checks']>=4
assert proof['variant_fixture_unchanged'] and proof['music_state_preserved'] and proof['ambient_stays_stopped'] and proof['extended_atomic_state']
previous=json.loads((w/'p521-previous-slot-proof.json').read_text())
assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==digest(exe)
for name,marker in [('p509-saves.log','P509 save verification: PASS'),('p509-saves-startup.log','P509 startup save: PASS'),('p521-previous-slot.log','P521 startup save: PASS')]:
    path=w/name
    text=path.read_text()
    assert path.stat().st_mtime>exe.stat().st_mtime and marker in text and 'FAIL' not in text
    assert text.rstrip().endswith('--- Log closed successfully.') and 'Using SDL Audio Driver "wasapi"' in text
for src,dst in [('p509-saves.log','p509-saves-runtime.log'),('p509-saves-startup.log','p509-saves-startup.log'),('p509-save-proof.json','p509-save-proof.json'),('p521-previous-slot.log','p521-previous-slot.log'),('p521-previous-slot-proof.json','p521-previous-slot-proof.json')]:
    shutil.copyfile(w/src,r/'evidence'/dst)
validation=dict(proof)
validation.update(date='2026-10-24',format_version=20,payload_bytes=4540,scene=509,full_suite=True,
    fresh_process_slot=19,byte_corruptions=proof['corruptions'],invalid_checksummed_states=proof['invalid_states'],
    scope='trusted_pending_p509',compatibility='Versions1-19 retained; genuine frozen verified v19 slot18 read unchanged',
    limitations=['Only ordinary phase1/2 with one trusted original P5/index3 pending narrator',
        'Foreground audio, other queued work, startup and phase3 exit remain excluded',
        'No complete manual audiovisual playthrough'])
(r/'evidence/p509-saves-validation.json').write_text(json.dumps(validation,indent=2))
subprocess.run([sys.executable,str(r/'probe_p509_save.py'),'D:/astro'],check=True)
# New validation must exist before older finishers regenerate shared coverage.
subprocess.run([sys.executable,str(w/'finish_p521_saves.py')],check=True)
heading=('# Ripresa: salvataggi P509,24 ottobre2026\n\n'
    f'Formato v20:4540byte,{proof["boundaries"]} ripristini verificati. '
    'Conserva il narratore originale P5/indice3 in attesa, SKY1/SKY2, bersagli e animazioni nascoste, clock, valori ereditati e stato dormiente. Slot19 in nuovo processo PASS.\n'
    'Compatibilita v1-v19, vero slotv19 congelato, rifiuto atomico dei file alterati, suite completa WASAPI e avvio normale sullo stesso eseguibile. Altre code, voci attive e transizioni restano escluse.\n'
    'Checkpoint:finish_p509_saves.py;check_p509_saves.py;check_p509_regressions.py;P509-SAVE-FORMAT.md. Non eseguire finalizzatori precedenti da soli.\n'
    'Ventiquattro scene con salvataggi verificati non misurano il completamento globale. Restano altri salvataggi, tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED.\n\n')
path=r/'NEXT-STEPS.md'
text=path.read_text()
path.write_text(text if text.startswith('# Ripresa: salvataggi P509') else heading+text)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,24 ottobre2026\n\n'+model+'\n\n'+heading+
    'Originali D:/astro; solo cleanroom dal13settembre2026, senza prototipi o tentativi esclusi. Fermarsi vicino1% della quota limitante; nessun acquisto o riscatto reset.\n')
path=r/'P509-SAVE-PLAN.md'
text=path.read_text()
note='## Verified P509 save support,24 October2026\n\nVersion20 is verified; see P509-SAVE-FORMAT.md and evidence/p509-saves-validation.json. The candidate investigation below remains history.\n\n'
path.write_text(text if text.startswith(note) else note+text)
path=r/'P509-SAVE-FORMAT.md'
text=path.read_text().replace('Status: candidate, SDL only; official native suite pending.','Status: verified24October2026; same-build native WASAPI and complete compatible suite PASS.')
path.write_text(text)
note=('\n\n## P509 saves,24 October2026\n\n'
    f'Version20 preserves {proof["boundaries"]} measured ordinary P509 boundaries with the original pending narrator and exact timed continuation. '
    'Fresh-process slot19 and unchanged genuine frozen v19 compatibility pass. Retained sky identity, hidden bounce and timer epochs are preserved. '
    'Foreground audio, other queued work and phase3 exits remain excluded. All4540 truncations and4540 byte corruptions reject atomically. Complete same-build WASAPI suite PASS.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
    path=r/name;text=path.read_text();path.write_text(text if '## P509 saves,24 October2026' in text else text+note)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
    subprocess.run([sys.executable,str(w/name)],check=True)
(r/'RUN-IN-PROGRESS.md').write_text('P509 v20 saves verified24October2026. Complete same-build native WASAPI suite, fresh-process slot19 and genuine frozen v19 slot PASS. Publication requires export verification. Newest finisher finish_p509_saves.py. Automation remains PAUSED.\n')
print('P509 v20 checkpoint PASS',flush=True)
