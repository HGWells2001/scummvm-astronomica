"""Record P518 v18 only after the complete exact-build native WASAPI suite."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
r=Path('outputs/astronomica-cleanroom');w=Path('work/fresh-20260913');exe=w/'build/Releasex64/scummvm.exe'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=next(x for x in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if x.startswith('Modello dichiarato'))
proof=json.loads((w/'planet-save-proof.json').read_text())
assert proof['status']=='PASS' and proof['exe_sha256']==digest(exe) and proof['metadata_listed'] and proof['slot']==17 and not proof['diagnostic']
assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
assert proof['truncations']==proof['corruptions']==6184
for key in ('boundaries','history_boundaries','dormant_boundaries','ordinary_boundaries','busy_rejections','invalid_states','natural_voice_ends'):assert proof[key]>0,key
assert proof['variant_fixture_unchanged'] and proof['music_restart'] and proof['extended_atomic_state'] and proof['count8_zero_checks']==1
previous=json.loads((w/'rendezvous-previous-slot-proof.json').read_text())
assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==digest(exe)
for name,marker in (('planet-saves.log','planet save verification: PASS'),('planet-saves-startup.log','planet startup save: PASS'),('rendezvous-previous-slot.log','rendezvous startup save: PASS')):
 p=w/name;text=p.read_text()
 assert p.stat().st_mtime>exe.stat().st_mtime and marker in text and 'FAIL' not in text
 assert text.rstrip().endswith('--- Log closed successfully.') and 'Using SDL Audio Driver "wasapi"' in text
for src,dst in (('planet-saves.log','planet-saves-runtime.log'),('planet-saves-startup.log','planet-saves-startup.log'),('planet-save-proof.json','planet-save-proof.json'),('rendezvous-previous-slot.log','rendezvous-previous-slot.log'),('rendezvous-previous-slot-proof.json','rendezvous-previous-slot-proof.json')):shutil.copyfile(w/src,r/'evidence'/dst)
validation=dict(proof)
validation.update(date='2026-10-22',format_version=18,payload_bytes=6184,scene=518,full_suite=True,fresh_process_slot=17,byte_corruptions=proof['corruptions'],invalid_checksummed_states=proof['invalid_states'],scope='idle_script_planets',compatibility='Versions1-17 retained; frozen verified v17 rendezvous slot read unchanged',limitations=['Only P518 boundaries without queued scripts/actions, foreground audio or transitions','Ambient sample restarts from beginning','No complete manual audiovisual playthrough'])
(r/'evidence/planet-saves-validation.json').write_text(json.dumps(validation,indent=2))
# Refresh original resource identity/source references; no original program execution.
subprocess.run([sys.executable,str(r/'probe_p518_save.py'),'D:/astro'],check=True)
# New validation must exist before older finishers regenerate shared coverage.
subprocess.run([sys.executable,str(w/'finish_rendezvous_saves.py')],check=True)
heading=('# Ripresa: salvataggi pianeti P518,22 ottobre2026\n\n'+f'Formato v18:6184 byte,{proof["boundaries"]} ripristini/successori verificati. '+
 'Conserva pianeti agganciati e rilasciati, scelta casuale, maschera, contatori, timer e storia nascosta dei tentativi falliti. Slot17 in un nuovo processo PASS.\n'+
 'Compatibilita v1-v17, vero slotv17 congelato, rifiuto atomico dei file alterati, suite completa WASAPI e avvio normale verificati sullo stesso eseguibile. Comandi in attesa, voci e transizioni restano esclusi.\n'+
 'Checkpoint:finish_planet_saves.py;check_planet_saves.py;check_planet_regressions.py;P518-SAVE-FORMAT.md. Non eseguire finalizzatori precedenti da soli.\n'+
 'Ventidue scene con salvataggi verificati non misurano il completamento globale. Restano altri salvataggi, tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED; preferenze e salvataggi personali intatti.\n\n')
p=r/'NEXT-STEPS.md';s=p.read_text();p.write_text(s if s.startswith('# Ripresa: salvataggi pianeti P518') else heading+s)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,22 ottobre2026\n\n'+model+'\n\n'+heading+'Originali D:/astro; solo cleanroom dal13settembre2026, senza prototipi o tentativi esclusi. Controllare entrambe le quote e fermarsi vicino1% della limitante. Nessun acquisto o riscatto reset.\n')
p=r/'P518-SAVE-FORMAT.md';s=p.read_text()
s=s.replace('Status: candidate, SDL only; official native suite pending.','Status: verified22October2026; same-build native WASAPI and complete compatible suite PASS.')
s=s.replace('The candidate saves','The format saves')
s=s.replace('Exact measured results belong to the final proof/CHECKPOINT; until present this paragraph is the test design.','The exact measured results and executable identity are recorded in evidence/planet-save-proof.json and evidence/planet-saves-validation.json; the official WASAPI and complete compatible same-build suite pass.')
s=s.replace('Preflight checks the complete489731byte original HYP, SHA256235de8b0fbb86b6cc1a8337779d6c6f7804e8455bce0dc607ea00092f3f6ffbd/byteFNV838a2480,','Runtime preflight checks the complete489731byte original HYP using byteFNV838a2480 (the separately recorded original SHA256 is235de8b0fbb86b6cc1a8337779d6c6f7804e8455bce0dc607ea00092f3f6ffbd),')
p.write_text(s)
p=r/'P518-SAVE-PLAN.md';s=p.read_text();note='## Verified P518 save support,22 October2026\n\nVersion18 is implemented and verified; see P518-SAVE-FORMAT.md and evidence/planet-saves-validation.json. The original inventory below remains research history.\n\n';p.write_text(s if s.startswith(note) else note+s)
note=('\n\n## P518 planet saves,22 October2026\n\n'+f'Version18 preserves P518 idle-script boundaries across {proof["boundaries"]} measured native round trips/successors, '+
 'with a fresh-process slot17 and unchanged verified v17 slot compatibility. Planet motion, random selection, hidden failed-attempt history and timer phases are retained. Queued commands, foreground audio and transitions remain excluded. All6184 truncations and6184 byte corruptions reject atomically. The complete compatible native WASAPI suite passes on the same executable.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=r/name;s=p.read_text();p.write_text(s if '## P518 planet saves,22 October2026' in s else s+note)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(w/name)],check=True)
(r/'RUN-IN-PROGRESS.md').write_text('P518 v18 planet saves verified22October2026. Complete same-build native WASAPI suite, fresh-process slot17 and prior v17 slot PASS. Publication still requires export verification. Newest finisher finish_planet_saves.py. Automation remains PAUSED.\n')
print('P518 v18 planet save checkpoint PASS')
