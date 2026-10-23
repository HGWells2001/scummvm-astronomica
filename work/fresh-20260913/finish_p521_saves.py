"""Record P521 v19 only after the complete exact-build native WASAPI suite."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
r=Path('outputs/astronomica-cleanroom');w=Path('work/fresh-20260913');exe=w/'build/Releasex64/scummvm.exe'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=next(x for x in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if x.startswith('Modello dichiarato'))
proof=json.loads((w/'p521-save-proof.json').read_text())
assert proof['status']=='PASS' and proof['exe_sha256']==digest(exe) and proof['metadata_listed'] and proof['slot']==18 and not proof['diagnostic']
assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
assert proof['truncations']==proof['corruptions']==5392
for key in ('boundaries','history_boundaries','dormant_boundaries','ordinary_boundaries','busy_rejections','invalid_states','natural_voice_ends'):assert proof[key]>0,key
assert proof['variant_fixture_unchanged'] and proof['music_restart'] and proof['extended_atomic_state']
previous=json.loads((w/'planet-previous-slot-proof.json').read_text())
assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==digest(exe)
for name,marker in (('p521-saves.log','P521 save verification: PASS'),('p521-saves-startup.log','P521 startup save: PASS'),('planet-previous-slot.log','planet startup save: PASS')):
 p=w/name;text=p.read_text()
 assert p.stat().st_mtime>exe.stat().st_mtime and marker in text and 'FAIL' not in text
 assert text.rstrip().endswith('--- Log closed successfully.') and 'Using SDL Audio Driver "wasapi"' in text
for src,dst in (('p521-saves.log','p521-saves-runtime.log'),('p521-saves-startup.log','p521-saves-startup.log'),('p521-save-proof.json','p521-save-proof.json'),('planet-previous-slot.log','planet-previous-slot.log'),('planet-previous-slot-proof.json','planet-previous-slot-proof.json')):shutil.copyfile(w/src,r/'evidence'/dst)
validation=dict(proof)
validation.update(date='2026-10-23',format_version=19,payload_bytes=5392,scene=521,full_suite=True,fresh_process_slot=18,byte_corruptions=proof['corruptions'],invalid_checksummed_states=proof['invalid_states'],scope='idle_script_p521',compatibility='Versions1-18 retained; frozen verified v18 planet slot read unchanged',limitations=['Only P521 boundaries without queued scripts/actions, foreground audio or transitions','Ambient sample restarts from beginning','No complete manual audiovisual playthrough'])
(r/'evidence/p521-saves-validation.json').write_text(json.dumps(validation,indent=2))
# Refresh original resource identity/source references; no original program execution.
subprocess.run([sys.executable,str(r/'probe_p521_save.py'),'D:/astro'],check=True)
# New validation must exist before older finishers regenerate shared coverage.
subprocess.run([sys.executable,str(w/'finish_planet_saves.py')],check=True)

for key in ('retained_image_boundaries','fragment_history_boundaries','animation_boundaries','successor_checks','future_outcome_checks','timer_cases'):assert proof[key]>0,key
assert proof['choice_controls']==5 and proof['future_outcome_checks']>=4
heading=('# Ripresa: salvataggi P521,23 ottobre2026\n\n'+f'Formato v19:5392 byte,{proof["boundaries"]} ripristini/successori verificati. '+
 'Conserva lo sfondo esterno visualizzato, la storia dei frammenti nascosti, animazioni e timer, valori ereditati e stato dormiente. Slot18 in un nuovo processo PASS.\n'+
 'Compatibilita v1-v18, vero slotv18 congelato, rifiuto atomico dei file alterati, suite completa WASAPI e avvio normale verificati sullo stesso eseguibile. Comandi in attesa, flash, voci e transizioni restano esclusi.\n'+
 'Checkpoint:finish_p521_saves.py;check_p521_saves.py;check_p521_regressions.py;P521-SAVE-FORMAT.md. Non eseguire finalizzatori precedenti da soli.\n'+
 'Ventitre scene con salvataggi verificati non misurano il completamento globale. Restano altri salvataggi, tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED; preferenze e salvataggi personali intatti.\n\n')
p=r/'NEXT-STEPS.md';s=p.read_text();p.write_text(s if s.startswith('# Ripresa: salvataggi P521') else heading+s)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,23 ottobre2026\n\n'+model+'\n\n'+heading+'Originali D:/astro; solo cleanroom dal13settembre2026, senza prototipi o tentativi esclusi. Controllare entrambe le quote e fermarsi vicino1% della limitante. Nessun acquisto o riscatto reset.\n')
p=r/'P521-SAVE-FORMAT.md';s=p.read_text();s=s.replace('Status: candidate, SDL only; official native suite pending.','Status: verified23October2026; same-build native WASAPI and complete compatible suite PASS.').replace('The candidate saves','The format saves').replace('The candidate covers','The format covers');p.write_text(s)
p=r/'P521-SAVE-PLAN.md';s=p.read_text();note='## Verified P521 save support,23 October2026\n\nVersion19 is implemented and verified; see P521-SAVE-FORMAT.md and evidence/p521-saves-validation.json. The original inventory below remains research history.\n\n';p.write_text(s if s.startswith(note) else note+s)
note=('\n\n## P521 saves,23 October2026\n\n'+f'Version19 preserves P521 idle-script boundaries across {proof["boundaries"]} measured native round trips/successors, '+
 'with a fresh-process slot18 and unchanged verified v18 slot compatibility. Retained external image, hidden fragment history, animation/timer phases and inherited runner values are preserved. Queued commands, flash, foreground audio and transitions remain excluded. All5392 truncations and5392 byte corruptions reject atomically. The complete compatible native WASAPI suite passes on the same executable.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=r/name;s=p.read_text();p.write_text(s if '## P521 saves,23 October2026' in s else s+note)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(w/name)],check=True)
(r/'RUN-IN-PROGRESS.md').write_text('P521 v19 saves verified23October2026. Complete same-build native WASAPI suite, fresh-process slot18 and prior v18 slot PASS. Publication still requires export verification. Newest finisher finish_p521_saves.py. Automation remains PAUSED.\n')
print('P521 v19 save checkpoint PASS')
