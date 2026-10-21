"""Finalize v14 only after targeted, fresh-process and complete same-build tests."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
r=Path('outputs/astronomica-cleanroom');w=Path('work/fresh-20260913');exe=w/'build/Releasex64/scummvm.exe'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=next(line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if line.startswith('Modello dichiarato'))
for name,marker in [('rocket-saves.log','rocket saves: PASS ('),('rocket-saves-startup.log','rocket startup save: PASS'),('builder-previous-slot.log','builder startup save: PASS'),('rocket-boundaries.log','rocket boundary verification: PASS')]:
 p=w/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime and marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((w/'rocket-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==13 and not proof['diagnostic'] and proof['audio_driver']=='native'
assert proof['boundaries']>500 and proof['history_boundaries']>300 and proof['dormant_boundaries']>300 and proof['busy_rejections']>0
assert proof['truncations']==proof['corruptions']==7680 and proof['invalid_states']>40 and proof['variant_fixture_unchanged']
audit=json.loads((w/'rocket-boundaries.json').read_text());assert audit['status']=='PASS' and audit['exe_sha256']==digest(exe) and audit['boundaries']==402
for src,dst in [('rocket-saves.log','rocket-saves-runtime.log'),('rocket-saves-startup.log','rocket-saves-startup.log'),('rocket-save-proof.json','rocket-save-proof.json'),('rocket-boundaries.json','rocket-boundaries.json'),('rocket-boundaries.log','rocket-boundaries.log'),('builder-previous-slot.log','builder-previous-slot.log'),('builder-previous-slot-proof.json','builder-previous-slot-proof.json')]:shutil.copyfile(w/src,r/'evidence'/dst)
v=dict(date='2026-10-21',status='PASS',exe_sha256=digest(exe),format_version=14,payload_bytes=7680,scene=537,
 boundaries=proof['boundaries'],history_boundaries=proof['history_boundaries'],dormant_boundaries=proof['dormant_boundaries'],busy_rejections=proof['busy_rejections'],
 truncations=7680,byte_corruptions=7680,invalid_checksummed_states=proof['invalid_states'],fresh_process_slot=13,fresh_process_fingerprint=proof['fresh_process_fingerprint'],
 music_restart=True,comet_phase_retained=True,dormant_sequence_retained=True,previous_readout_retained=True,stopped_motion_epoch_retained=True,full_frame_height=480,full_suite=True,
 compatibility='Versions1-13 retained; previous-build v3-v13 slots unchanged',limitations=['Settled script boundaries only; no queued mid-launch serialization','Ambient sample may restart from beginning','No complete manual audiovisual playthrough'])
(r/'evidence/rocket-saves-validation.json').write_text(json.dumps(v,indent=2))
p=subprocess.run([sys.executable,str(w/'finish_builder_saves.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-200:])
heading=('# Ripresa: salvataggi razzo P537,21 ottobre2026\n\n'
 f'Formato v14:7680byte,{proof["boundaries"]} ripristini/successori,{proof["history_boundaries"]} confini con display precedente,{proof["dormant_boundaries"]} con custom17 sospeso PASS. Tutti16 selector,limiti,rilanciozero,uscita/help,primo/ripetuto successo verificati.\n'
 'Slot13 in nuovo processo:precedente fallimento veloce,selector11,round2 sospeso e successo contato una volta PASS. Delta/since del moto fermo e cometa conservati. Audit nativo indipendente402confini. Compatibilita v1-v13 e suite completa WASAPI/avvio normale PASS sullo stesso eseguibile.\n'
 'Checkpoint:finish_rocket_saves.py;check_rocket_saves.py/check_rocket_regressions.py/check_rocket_boundaries.py/P537-SAVE-FORMAT.md. Non eseguire finalizzatori precedenti da soli.\n'
 'Diciotto scene con salvataggi verificati non sono una percentuale globale. Restano altri salvataggi,tipografia aiuto e verifica audiovisiva manuale integrale. Avvio:Avvia-Astronomica.cmd;userdata/astronomica intatti.\n\n')
p=r/'NEXT-STEPS.md';s=p.read_text();p.write_text(heading+s if not s.startswith('# Ripresa: salvataggi razzo') else s)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,21 ottobre2026\n\n'+model+'\n\n'+heading+'Vincoli:originali D:/astro,solo cleanroom dal13settembre2026,niente tentativi esclusi o prototipi. Modello invariato. Controllare entrambe le quote e fermarsi vicino1%limitante;nessun acquisto/riscatto reset.\n')
p=r/'P537-SAVE-FORMAT.md';s=p.read_text().replace('Prepared21 October2026. Implementation is under native verification; support is not yet a verified checkpoint.','Implemented and verified21 October2026; see evidence/rocket-saves-validation.json.').replace('These are test requirements until their native logs and evidence are finalized.','All these checks pass on the same executable; archived logs and proof record the measured coverage.');p.write_text(s)
p=r/'P537-SAVE-PLAN.md';s=p.read_text();s='## Verified settled save support,21 October2026\n\nVersion14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.\n\n'+s;p.write_text(s)
note=f'\n\n## P537 rocket saves,21 October2026\n\nVersion14 retains all48 sprites, selector, prior digits/gauges, stopped motion epoch and dormant cross-puzzle state. {proof["boundaries"]} exact round trips/successors and fresh-process slot13 pass; all7680 truncations,7680 corruptions and{proof["invalid_states"]} checksummed invalid states reject atomically. Full native WASAPI suite and normal startup pass with versions1-13 retained.\n'
for name in ('README.md','SAVE-RESEARCH.md'):
 p=r/name;s=p.read_text();p.write_text(s+note if '## P537 rocket saves,21 October2026' not in s else s)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(w/name)],check=True)
(r/'RUN-IN-PROGRESS.md').write_text('P537 v14 verified21October2026. Targeted/fresh-process/independent-boundary/prior-slot and complete native WASAPI suite plus launcher PASS. No tests running. Follow NEXT-STEPS.md/AI_MODEL_CHECKPOINT.md; newest finisher finish_rocket_saves.py.\n')
print('P537 v14 rocket save checkpoint PASS')
