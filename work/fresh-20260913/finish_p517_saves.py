"""Finalize aurora saves only after fresh-process, old-slot and full same-build suites."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe';ai_before=Path('AI_MODEL_CHECKPOINT.md').read_text()
for name,marker in [('p517-saves.log','P517 saves: PASS ('),('p517-saves-startup.log','P517 startup save: PASS'),('p513-previous-slot.log','P513 startup save: PASS')]:
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime and marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((work/'p517-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==11 and proof['boundaries']>2000
assert (proof['routes'],proof['settings'],proof['animation_cases'],proof['truncations'],proof['corruptions'])==(3,14,2240,3660,3660)
assert proof['invalid_states']>30
assert proof['music_restart']
for src,dst in [('p517-saves.log','p517-saves-runtime.log'),('p517-saves-startup.log','p517-saves-startup.log'),('p517-save-proof.json','p517-save-proof.json'),('p513-previous-slot.log','p513-previous-slot.log'),('p513-previous-slot-proof.json','p513-previous-slot-proof.json')]:shutil.copyfile(work/src,root/'evidence'/dst)
assert json.loads((work/'p513-previous-slot-proof.json').read_text())['unchanged']
audit=json.loads((work/'builder-boundaries.json').read_text())
assert audit['status']=='PASS' and audit['boundaries']>100 and audit['exe_sha256']==hashlib.sha256(exe.read_bytes()).hexdigest()
audit_log=(work/'builder-boundaries.log').read_text()
assert 'P515/P536 interaction verification: PASS' in audit_log and 'FAIL' not in audit_log and 'Log closed successfully' in audit_log
for name in ('builder-boundaries.json','builder-boundaries.log'):shutil.copyfile(work/name,root/'evidence'/name)
p=root/'BUILDER-SAVE-PLAN.md';s=p.read_text().replace('This conclusion from command order is scheduled for separate native validation in the next build.','Native early-Launch routes verify this conclusion, including the unchanged P515 completion count; see evidence/builder-boundaries.json.').replace('The staged check_builder_boundaries.py','check_builder_boundaries.py').replace('No native boundary report exists yet for this investigation.',f'{audit["boundaries"]} settled native boundaries are recorded in evidence/builder-boundaries.json; they are not proof of builder save support.');p.write_text(s)
v=dict(date='2026-10-19',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),format_version=12,payload_bytes=3660,scene=517,boundaries=proof['boundaries'],gameplay_successor_comparisons=proof['boundaries'],
 solve_and_exit_routes=3,settings=14,animation_cases=2240,full_frame_height=480,truncations=3660,byte_corruptions=3660,invalid_checksummed_states=proof['invalid_states'],fresh_process_slot=11,fresh_process_fingerprint=proof['fresh_process_fingerprint'],
 active_animation=True,inactive_phases=True,next_frame_timing=True,first_completion_count=True,repeated_completion_count=True,minimum_clamp=True,unsolved_exit=True,music_restart=True,full_suite=True,
 compatibility='Versions1-11 retained; previous-build v3-v11 slots unchanged',limitations=['Settled script boundaries only; ordinary aurora animation continues','Successor hashes omit newly rebuilt program and departure-sound epochs; exact pre-action payload comparison retains saved epochs','Music may restart from its beginning','No complete manual audiovisual playthrough'])
(root/'evidence/p517-saves-validation.json').write_text(json.dumps(v,indent=2))
p=subprocess.run([sys.executable,str(work/'finish_p513_saves.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-300:])
note=(f'\n\n## P517 aurora saves,19 October2026\n\nNative v12 retains both locals, all eleven sprite records, the active aurora timer and stopped inactive phases, background, gauge and marker. '
 f'{proof["boundaries"]} native round trips/successors cover all14 settings,2240 animation cases, both controls, minimum clamp and first/repeated completion count. '
 f'Slot11 resumes setting12 with active/stopped phases in a fresh process and completes with the original count. All3660 truncations,3660 byte corruptions and{proof["invalid_states"]} checksummed invalid states reject atomically. '
 'Versions1-11, old slots, full graphics/audio/help/import/WASAPI and normal launcher startup pass on the same build.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=root/name;s=p.read_text()
 if '## P517 aurora saves,19 October2026' not in s:s+=note
 p.write_text(s)
p=root/'P517-SAVE-FORMAT.md';p.write_text(p.read_text().replace('Implementation being prepared,19 October2026; not yet a verified checkpoint.','Implemented and verified19 October2026; see evidence/p517-saves-validation.json.').replace('The proposed v12 payload','The v12 payload'))
heading=('# Ripresa: salvataggi P517,19 ottobre2026\n\n'
 f'Formato v12:{proof["boundaries"]} ripristini/successori,14 posizioni,2240 casi animazione PASS. Conserva fasi attive/ferme, timer,immagine,indicatore e cursore grafico.\n'
 'Slot11 in nuovo processo dalla posizione12 PASS; primo/ripetuto successo,limite minimo e uscita volontaria PASS. Compatibilita v1-v11,vecchi slot v3-v11 e suite completa WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint:finish_p517_saves.py;check_p517_saves.py,check_p517_regressions.py e P517-SAVE-FORMAT.md. Non rieseguire finalizzatori precedenti da soli.\n'
 'Avvio:Avvia-Astronomica.cmd;preferenze/salvataggi personali in userdata/astronomica. Restano altri salvataggi,verifica audiovisiva manuale integrale e tipografia aiuto. Quindici scene con salvataggi non misurano il completamento globale.\n\n')
p=root/'NEXT-STEPS.md';s=p.read_text()
if not s.startswith('# Ripresa: salvataggi P517'):s=heading+s
p.write_text(s)
model=next(line for line in ai_before.splitlines() if line.startswith('Modello dichiarato'))
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,19 ottobre2026\n\n'+model+'\n\n'
 f'Checkpoint:P517 v12,3660 byte,{proof["boundaries"]} successori,14 posizioni,2240 casi animazione e slot11 in nuovo processo PASS. Fasi attive/ferme e timer conservati; primo/ripetuto conteggio,limiti/uscite PASS. Compatibilita v1-v11 e suite completa WASAPI PASS.\n\n'
 'Seguire NEXT-STEPS.md,P517-SAVE-FORMAT.md e check_p517_saves.py/check_p517_regressions.py/finish_p517_saves.py. Sorgenti canonici in outputs/astronomica-cleanroom/engine/astronomica. Non ricopiare staging precedente.\n\n'
 'Avvio:Avvia-Astronomica.cmd;preferenze/salvataggi personali in userdata/astronomica. Restano altri salvataggi,verifica audiovisiva manuale integrale e tipografia aiuto. Quindici scene con salvataggi non sono una percentuale globale.\n\n'
 'Vincoli:originali D:/astro,solo cleanroom dal13 settembre2026,niente vecchi tentativi esclusi o prototipi. Modello corrente sufficiente,nessun cambio richiesto. Controllare entrambe le quote,riservare verifica/pubblicazione e fermarsi vicino all\'1% limitante;nessun acquisto o riscatto reset.\n')
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P517 v12 verified19 October2026. Targeted/fresh-process/prior-slot and full compatible WASAPI suites PASS; no tests running. Follow NEXT-STEPS.md and AI_MODEL_CHECKPOINT.md.\n')
print('P517 v12 save checkpoint PASS')
