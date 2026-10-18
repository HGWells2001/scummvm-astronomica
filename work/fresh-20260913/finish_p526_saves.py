"""Finalize P526 v7 only after targeted, prior-slot and full compatible tests."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
tree=ast.parse((work/'finish_p519_saves.py').read_text())
required=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='required' for t in n.targets))
required.update({'p524-saves.log':['P524 saves: PASS (72 boundaries, 48 animation cases'],
 'p524-saves-startup.log':['P524 startup save: PASS'],'p519-previous-slot.log':['P519 startup save: PASS'],
 'p524-previous-slot.log':['P524 startup save: PASS'],
 'p526-boundaries.log':['P526 interaction verification: PASS'],
 'p526-saves.log':['P526 saves: PASS (686 boundaries, 216 animation cases, 432 answer cases, 4956 truncations, 4956 corruptions, 25 invalid states','P526 save verification: PASS'],
 'p526-saves-startup.log':['P526 startup save: PASS','P526 save verification: PASS']})
for name,markers in required.items():
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime,name
 assert 'FAIL' not in s and 'Log closed successfully' in s,name
 for marker in markers:assert marker in s,(name,marker)
for p in (root/'engine/astronomica').iterdir():
 if p.is_file():
  assert p.read_bytes()==(work/'scummvm/engines/astronomica'/p.name).read_bytes(),p
  assert p.stat().st_mtime<exe.stat().st_mtime,p
audit=json.loads((work/'p526-boundaries.json').read_text())
assert audit['status']=='PASS' and audit['boundaries']==33 and audit['exe_sha256']==hashlib.sha256(exe.read_bytes()).hexdigest()
proof=json.loads((work/'p526-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed']
for scene in (505,508,519,524,526):
 for src,dst in [('saves.log','saves-runtime.log'),('saves-startup.log','saves-startup.log'),('save-proof.json','save-proof.json')]:
  shutil.copyfile(work/f'p{scene}-{src}',root/'evidence'/f'p{scene}-{dst}')
 # Animation epochs make a new fixture's fingerprint legitimately differ
 # from the prior run. Keep the old coverage assertions but bind them to
 # this run's freshly checked physical-slot proof.
 if scene != 526:
  path=root/f'evidence/p{scene}-saves-validation.json';previous=json.loads(path.read_text())
  current=json.loads((work/f'p{scene}-save-proof.json').read_text())
  assert current['status']=='PASS' and current['metadata_listed']
  previous['fresh_process_fingerprint']=current['fresh_process_fingerprint'];previous['latest_validation_date']='2026-10-18'
  path.write_text(json.dumps(previous,indent=2))
for scene in (505,508,519,524):
 for suffix in ('previous-slot.log','previous-slot-proof.json'):shutil.copyfile(work/f'p{scene}-{suffix}',root/'evidence'/f'p{scene}-{suffix}')
for src,dst in [('p526-boundaries.json','p526-native-save-boundaries.json'),('p526-boundaries.log','p526-native-save-boundaries.log'),
 ('help.log','help-native-runtime.log'),('legacy.log','legacy-runtime.log'),('legacy-file-proof.json','legacy-file-proof.json')]:shutil.copyfile(work/src,root/'evidence'/dst)
validation=dict(date='2026-10-18',status='PASS',format_version=7,payload_bytes=4956,scene=526,boundaries=686,gameplay_successor_comparisons=33,identity_roundtrips=5,animation_cases=216,synthetic_answer_cases=432,
 observed_native_boundaries=33,solve_routes=2,fourth_error_exit=True,voluntary_exit=True,hover_resumptions=True,truncations=4956,byte_corruptions=4956,invalid_checksummed_states=25,
 fresh_process_slot=6,fresh_process_fingerprint=proof['fresh_process_fingerprint'],music='Ambient restarts from beginning',compatibility='Exploration v1/v2, P508 v3, P505 v4, P519 v5 and P524 v6 retained; previous-build slots unchanged',
 limitations=['No snapshots during orbital travel','Synthetic phase trials are not claims of natural reachability','Other puzzle saves remain unsupported','No complete manual audiovisual playthrough'])
(root/'evidence/p526-saves-validation.json').write_text(json.dumps(validation,indent=2))
note=('\n\n## P526 native saves, 18 October 2026\n\n'
 'Native v7 saves settled P526 entry, stopped experiments and answered states. It retains the full runner/RNG, clock/count, '
 '23 sprite records with render/center positions, animation and movement epochs, orbital parameters and flags, committed picture and six hover bits. '
 'Orbit travel, foreground audio, queued work and staged images exclude saving. Ambient music restarts at its beginning.\n\n'
 'Verified on one matching build: 686 round trips (33 gameplay successors, five identities, 216 animation comparisons, 432 synthetic phase/answer cases), '
 '4956 truncations, 4956 byte corruptions and 25 checksummed invalid states. A physical slot6 loads in a fresh process and completes all remaining questions. '
 'The separate native audit observes 33 boundaries on real routes. Full v1-v6 compatibility, previous-build v3-v6 slots, exploration, import, help and WASAPI regressions pass. '
 'This is automated evidence, not a full manual audiovisual playthrough.\n')
for name in ('README.md','SAVE-RESEARCH.md','P526-SAVE-PLAN.md'):
 p=root/name;s=p.read_text()
 if '## P526 native saves, 18 October 2026' not in s:s+=note
 if name=='P526-SAVE-PLAN.md':s=s.replace('Saving P526 is not implemented.','P526 v7 settled saves are implemented and verified; see P526-SAVE-FORMAT.md.\nThe preparation below records the original implementation questions.')
 p.write_text(s)
p=root/'P526-SAVE-FORMAT.md';s=p.read_text().replace('Implementation under verification, 18 October 2026. Do not interpret this\ncontract as a completed checkpoint until p526-saves-validation.json is PASS.','Implemented and verified 18 October 2026; p526-saves-validation.json is PASS.');p.write_text(s)
p=root/'NEXT-STEPS.md';s=p.read_text();heading=('# Ripresa: salvataggi P526, 18 ottobre 2026\n\n'
 'P526 v7: 686 ripristini, 216 casi animazione, 432 combinazioni artificiali fase/risposta, slot e nuovo processo PASS.\n'
 '33 successori di gioco e cinque identita distinti dai casi artificiali; audit nativo 33 confini sui sei scenari.\n'
 'P505/P508/P519/P524, precedenti slot v3-v6, esplorazione v1/v2, import, aiuto e suite WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_p526_saves.py. Test: check_p526_saves.py e check_p526_regressions.py.\n'
 'Leggere P526-SAVE-FORMAT.md. Prossimo: PRESENTATION-RESEARCH.md (barra che copre24 righe), poi P528-SAVE-PLAN.md (due sfondi e riga persistente).\n'
 'Protocollo AI: AI_MODEL_CHECKPOINT.md nella radice del workspace. Nessuna percentuale globale attendibile.\n\n')
if not s.startswith('# Ripresa: salvataggi P526'):s=heading+s
p.write_text(s)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI, 18 ottobre 2026\n\n'
 'P526 v7 verificato: 686 ripristini, 33 successori di gioco, cinque identita, 216 casi animazione e 432 casi artificiali fase/risposta. '
 'Audit nativo33 confini; compatibilita v1-v6 e suite WASAPI superate sullo stesso eseguibile.\n\n'
 'Sorgenti modificati: outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp e astronomica.h. '
 'Driver e prove: check_p526_saves.py, check_p526_boundaries.py, check_p526_regressions.py, finish_p526_saves.py; '
 'contratto P526-SAVE-FORMAT.md e evidence/p526-saves-validation.json.\n\n'
 'Obiettivo: motore reale dai file D:/astro, cleanroom dal13 settembre2026. Prossimo: PRESENTATION-RESEARCH.md, poi P528-SAVE-PLAN.md, '
 'verifica audiovisiva manuale e tipografia aiuto. Leggere NEXT-STEPS.md; non rieseguire finalizzatori storici.\n\n'
 'Valutazione AI: configurazione corrente sufficiente in questa fase. Variante e livello selezionati nel client non verificabili. '
 'Nessun cambio applicato o richiesto. Candidato per difficolta persistenti: gpt-6.1-sol, xhigh, documentato in '
 'https://developers.openai.com/api/docs/models/gpt-6.1-sol. Prima di ogni nuova fase rivalutare il vantaggio concreto; '
 'se serve un cambio, salvare il checkpoint, richiederlo e attendere conferma come da protocollo utente.\n\n'
 'Limiti: cinque scene con salvataggi interni non misurano completamento globale; nessuna percentuale globale attendibile.\n')
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P526 v7 saves verified 18 October 2026. Matching build, 686 round trips, native boundary audit, malformed rejection, slot/fresh-process completion, v1-v6 compatibility and full WASAPI suite PASS. No tests running. See NEXT-STEPS.md and workspace AI_MODEL_CHECKPOINT.md.\n')
print('P526 save checkpoint PASS')
