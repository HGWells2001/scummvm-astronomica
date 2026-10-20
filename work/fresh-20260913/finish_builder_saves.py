"""Finalize v13 only after builder, frozen-slot and complete same-build suites."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
model=next(line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if line.startswith('Modello dichiarato'))
for name,marker in [('builder-saves.log','builder saves: PASS ('),('builder-saves-startup.log','builder startup save: PASS'),('p517-previous-slot.log','P517 startup save: PASS')]:
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime and marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((work/'builder-save-proof.json').read_text())
assert proof['audio_driver']=='native' and not proof['diagnostic']
assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==12 and proof['boundaries']>300
assert proof['fresh_scene_timer_comparisons']>=6
assert proof['routes']==6 and proof['matrix_cases']>=280 and proof['truncations']==proof['corruptions']==8960 and proof['invalid_states']>40
assert proof['comet_phase_retained'] and proof['music_restart'] and proof['dormant_boundaries'] and proof['no_picture_boundaries'] and proof['variant_fixture_unchanged']
assert json.loads((work/'p517-previous-slot-proof.json').read_text())['unchanged']
for src,dst in [('builder-saves.log','builder-saves-runtime.log'),('builder-saves-startup.log','builder-saves-startup.log'),('builder-save-proof.json','builder-save-proof.json'),('p517-previous-slot.log','p517-previous-slot.log'),('p517-previous-slot-proof.json','p517-previous-slot-proof.json')]:shutil.copyfile(work/src,root/'evidence'/dst)
v=dict(date='2026-10-20',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),format_version=13,payload_bytes=8960,scenes=[515,536],
 boundaries=proof['boundaries'],routes=6,matrix_cases=proof['matrix_cases'],fresh_scene_timer_comparisons=proof['fresh_scene_timer_comparisons'],full_frame_height=480,truncations=8960,byte_corruptions=8960,invalid_checksummed_states=proof['invalid_states'],
 fresh_process_slot=12,fresh_process_fingerprint=proof['fresh_process_fingerprint'],dormant_sequence_retained=True,comet_phase_retained=True,first_completion_count=True,repeated_completion_count=True,
 early_launch=True,p515_success_noop=True,music_restart=True,full_suite=True,compatibility='Versions1-12 retained; previous-build v3-v12 slots unchanged',
 limitations=['Settled script boundaries only; Choose awaits Confirm before a save is allowed','New destination active frame epochs compare by age; saved builder bytes stay exact','Ambient sample may restart from its beginning','All five designs and both scenes in memory; physical slot represents partial P536 design5','No complete manual audiovisual playthrough'])
(root/'evidence/builder-saves-validation.json').write_text(json.dumps(v,indent=2))
runtime=(work/'runtime.log').read_text()
assert 'P537 original callback comparison: PASS (96 fixtures, 14592 steps, 292dc3fd)' in runtime and 'FAIL' not in runtime
assert (work/'runtime.log').stat().st_mtime>exe.stat().st_mtime
readout=json.loads((work/'p537-readout-proof.json').read_text())
assert readout['status']=='PASS' and not readout['diagnostic'] and readout['exe_sha256']==hashlib.sha256(exe.read_bytes()).hexdigest()
assert readout['checked_pixels']>1000 and readout['old_shift_mismatch_pixels']>0 and {c['setting'] for c in readout['captures']}=={1,7,11,13}
readout_folder=work/'p537-readout-regression'
assert (readout_folder/'runtime.log').stat().st_mtime>exe.stat().st_mtime
for item in readout['captures']:
 image=readout_folder/('rocket-readout-'+str(item['setting'])+'.png')
 assert hashlib.sha256(image.read_bytes()).hexdigest()==item['png_sha256']
 shutil.copyfile(image,root/'evidence'/('p537-readout-'+str(item['setting'])+'.png'))
shutil.copyfile(work/'p537-readout-proof.json',root/'evidence/p537-readout-proof.json')
shutil.copyfile(readout_folder/'runtime.log',root/'evidence/p537-readout-runtime.log')
original=json.loads((root/'evidence/p537-motion-original.json').read_text())
assert original['combined_fnv32']=='292dc3fd' and original['steps']==14592 and len(original['traces'])==96
rocket=dict(date='2026-10-20',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),fixtures=96,steps=14592,combined_fnv32='292dc3fd',
 original_evidence_sha256=hashlib.sha256((root/'evidence/p537-motion-original.json').read_bytes()).hexdigest(),
 readout_proof_sha256=hashlib.sha256((work/'p537-readout-proof.json').read_bytes()).hexdigest(),rendered_pixels=readout['checked_pixels'],native_runtime_sha256=hashlib.sha256((work/'runtime.log').read_bytes()).hexdigest(),inactive_digit_timers=21,full_suite=True,
 corrections=['Final readout uses original one-based sprite IDs','All21 digit frame periods become-1 when stopped'],
 limitations=['Explicit callback fixtures, not96 UI routes','Only selected SpriteWorld fields/setters are modeled','Animation scheduling and success-helper internals are outside the original instruction model'])
(root/'evidence/p537-motion-validation.json').write_text(json.dumps(rocket,indent=2))
p=subprocess.run([sys.executable,str(work/'finish_p517_saves.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-300:])
p=root/'BUILDER-SAVE-FORMAT.md';s=p.read_text().replace('Prepared19 October2026. Implementation is staged separately from the verified engine; no builder save support is claimed yet.','Implemented and verified20 October2026; see evidence/builder-saves-validation.json.').replace('The proposed v13 format','The v13 format').replace('The8960-byte payload','The8960-byte payload').replace('## Verification prepared','## Verification').replace('These are requirements and test code, not recorded passes until their logs and proof are finalized.','All these checks pass on the same build; the archived logs and proof record the measured coverage.');p.write_text(s)
p=root/'BUILDER-SAVE-PLAN.md';s=p.read_text().replace('Save support is not implemented or verified for these two scenes.','Save support is implemented and verified for both scenes; see BUILDER-SAVE-FORMAT.md and evidence/builder-saves-validation.json.').replace('This is a verification plan, not implemented support.','This cross-puzzle case is verified in memory and through physical slot12.');p.write_text(s)
note=(f'\n\n## Construction saves,20 October2026\n\nNative v13 retains both P515/P536 construction scenes and the dormant custom17 round/mask and comet orientation. '
 f'{proof["boundaries"]} round trips/successors and{proof["matrix_cases"]} control matrix cases cover six routes, all five designs, early Launch, no-picture states, partial parts and cap recovery. '
 'Physical slot12 resumes partial P536 design5 in a fresh process, preserves dormant round2 and applies first completion exactly once. P515 success remains the original no-op. '
 f'All8960 truncations,8960 byte corruptions and{proof["invalid_states"]} checksummed invalid states reject atomically. Versions1-12 and the complete WASAPI regression pass on this build.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=root/name;s=p.read_text()
 if '## Construction saves,20 October2026' not in s:s+=note
 p.write_text(s)
heading=('# Ripresa: salvataggi costruttore,20 ottobre2026\n\n'
 f'Formato v13:8960 byte,{proof["boundaries"]} ripristini/successori,{proof["matrix_cases"]} casi controlli,sei percorsi e cinque progetti PASS. P515/P536 conservano anche round/mask custom17 sospesi.\n'
 'Slot12 in nuovo processo da P536 parziale con round2 sospeso PASS; primo/ripetuto conteggio,Launch anticipato,P515 no-op,cap/ripristino e stati senza immagine PASS. Compatibilita v1-v12 e suite completa WASAPI PASS sullo stesso eseguibile.\n'
 'P537:corretti gli ID delle cifre finali e21 periodi fermi;96 fixture/14592 passi originali e12096 pixel di quattro schermate PASS. P537 non ha ancora salvataggi.\n'
 'Checkpoint:finish_builder_saves.py;check_builder_saves.py,check_builder_regressions.py,BUILDER-SAVE-FORMAT.md. Non eseguire finalizzatori precedenti da soli.\n'
 'Avvio:Avvia-Astronomica.cmd;preferenze/salvataggi personali in userdata/astronomica. Restano altri salvataggi,verifica audiovisiva manuale integrale e tipografia aiuto. Diciassette scene con salvataggi non sono una percentuale globale.\n\n')
p=root/'NEXT-STEPS.md';s=p.read_text()
if not s.startswith('# Ripresa: salvataggi costruttore'):s=heading+s
p.write_text(s)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,20 ottobre2026\n\n'+model+'\n\n'+heading+
 'Vincoli:originali D:/astro,solo cleanroom dal13 settembre2026,niente tentativi esclusi o prototipi. Modello invariato. Controllare entrambe le quote e fermarsi vicino all\'1% limitante;nessun acquisto o riscatto reset.\n')
p=root/'P537-SAVE-PLAN.md';s=p.read_text().replace('A real-engine correction to period-1 and a native96-fixture comparison are staged with construction v13; no native pass is claimed until their runtime log is checked.','The real-engine correction to period-1 and the original final readout IDs passes the native96-fixture comparison and exact original-image pixel checks on the same verified construction v13 build.')
s+='\n\n## Native callback correction verified,20 October2026\n\nThe production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.\n';p.write_text(s)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Construction v13 verified20 October2026. Targeted/fresh-process/prior-slot and complete compatible WASAPI suites PASS; no tests running. Follow NEXT-STEPS.md and AI_MODEL_CHECKPOINT.md.\n')
print('Builder v13 save checkpoint PASS')
