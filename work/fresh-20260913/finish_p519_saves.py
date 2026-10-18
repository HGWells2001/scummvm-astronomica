"""Publishable P519 checkpoint requires one matching build and all regressions."""
from pathlib import Path
import json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
required={
 'p519-saves.log':['P519 saves: PASS (104 boundaries, 30 compositions, 2584 truncations, 2584 corruptions, 18 invalid states','P519 save verification: PASS'],
 'p519-saves-startup.log':['P519 startup save: PASS','P519 save verification: PASS'],
 'p505-saves.log':['P505 saves: PASS (38 boundaries and successor comparisons, 38 hover resumptions'],
 'p505-saves-startup.log':['P505 startup save: PASS'],
 'p505-previous-slot.log':['P505 startup save: PASS'],
 'p508-saves.log':['P508 saves: PASS (63 boundaries, 291 continuation steps'],
 'p508-saves-startup.log':['P508 startup save: PASS'],
 'p508-previous-slot.log':['P508 startup save: PASS'],
 'help.log':['help keyboard navigation: PASS (781 articles','help inline images: PASS (31 original images'],
 'runtime.log':['Astronomica script verification: PASS','legacy save verification: PASS'],
 'legacy.log':['legacy save verification: PASS'],
 'saves.log':['save verification: PASS','save file verification: PASS'],
 'saves-startup.log':['startup save verification: PASS']}
for name,markers in required.items():
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime,name
 assert 'FAIL' not in s and 'Log closed successfully' in s,name
 for marker in markers:assert marker in s,(name,marker)
for p in (root/'engine/astronomica').iterdir():
 if p.is_file():
  assert p.read_bytes()==(work/'scummvm/engines/astronomica'/p.name).read_bytes(),p
  assert p.stat().st_mtime<exe.stat().st_mtime,p
proof=json.loads((work/'p519-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed']
for scene in (505,508,519):
 for src,dst in [('saves.log','saves-runtime.log'),('saves-startup.log','saves-startup.log'),('save-proof.json','save-proof.json')]:
  shutil.copyfile(work/f'p{scene}-{src}',root/'evidence'/f'p{scene}-{dst}')
for scene in (505,508):
 for suffix in ('previous-slot.log','previous-slot-proof.json'):shutil.copyfile(work/f'p{scene}-{suffix}',root/'evidence'/f'p{scene}-{suffix}')
for name,dest in [('help.log','help-native-runtime.log'),('legacy.log','legacy-runtime.log'),('legacy-file-proof.json','legacy-file-proof.json')]:shutil.copyfile(work/name,root/'evidence'/dest)
validation=dict(date='2026-10-16',status='PASS',format_version=5,payload_bytes=2584,scene=519,
 scope='Idle P519 boundaries, including detector selection and solved pair indicators',boundaries=104,gameplay_successor_comparisons=74,resource_compositions=30,detector_target_pairs=25,solve_orders=2,repeated_target=True,unsolved_exit=True,truncations=2584,byte_corruptions=2584,invalid_checksummed_states=18,
 fresh_process_slot=4,fresh_process_fingerprint=proof['fresh_process_fingerprint'],music='Ambient restarts from beginning',compatibility='Exploration v1/v2, P508 v3, P505 v4 retained; previous-build v3/v4 slots tested without modifying their files',limitations=['No saves in the other puzzles','No full manual audiovisual playthrough'])
(root/'evidence/p519-saves-validation.json').write_text(json.dumps(validation,indent=2))
note=('\n\n## P519 native saves, 16 October 2026\n\n'
 'Native v5 now saves idle P519 selections and partial solutions. It retains all script state and RNG, '
 'clock/count, 27 sprite frames and visibility, ten rectangle hover flags and ambient state. '
 'Two original image identities reconstruct the full background: the latest large image and optional subsequent small image. '
 'Image identities change only when display commits; a new large image clears the small record. '
 'Loading skips startup and speech. Foreground audio, queued work, button pulses and staged pictures exclude saving. '
 'Ambient music restarts from its beginning.\n\n'
 'Tests pass 74 gameplay successor comparisons (all 25 detector/target pairs, both solve orders, repeated target and unsolved exit), '
 'plus 30 separate native image-composition round trips. All compare script/RNG, background/screen pixels, '
 'sprite frames, hover state and applicable sound IDs/counts. 2584 truncations, 2584 byte corruptions and '
 '18 checksummed invalid states reject without changing live state. Physical slot 4 loads in a fresh process '
 'with an identical fingerprint and completes five pairings after the wrong Sun selection. '
 'P505/P508 full save tests, previous-build v3/v4 slots, exploration saves, original import, help and full WASAPI suite pass. '
 'This remains automated evidence; manual audiovisual playthrough and other puzzle saves are outstanding.\n')
for name in ('README.md','SAVE-RESEARCH.md','P519-SAVE-PLAN.md'):
 p=root/name;s=p.read_text()
 if '## P519 native saves, 16 October 2026' not in s:s+=note
 if name=='README.md':s=s.replace('Stato verificato: 15 ottobre 2026.','Stato verificato: 16 ottobre 2026.').replace('P505 e P508 supportano ora salvataggi fra le domande.','P505 e P508 supportano salvataggi fra le domande; P519 fra le selezioni.')
 if name=='P519-SAVE-PLAN.md':s=s.replace('P519 saving is not implemented. This contract comes from a fresh parse of','P519 saving is now implemented and verified; see the dated result below.\nThe original implementation contract comes from a fresh parse of')
 p.write_text(s)
p=root/'NEXT-STEPS.md';s=p.read_text()
heading=('# Ripresa: salvataggi P519, 16 ottobre 2026\n\n'
 'P519 v5: 74 confronti di continuazione e 30 composizioni native; 25 abbinamenti, due ordini, uscita e slot reale PASS.\n'
 'P505/P508, vecchi slot v3/v4, esplorazione v1/v2, import, aiuto e suite WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_p519_saves.py. Test: check_p519_saves.py e check_p519_regressions.py.\n'
 'Leggere P519-SAVE-FORMAT.md e P519-SAVE-PLAN.md. Prossimo: P524-SAVE-PLAN.md (animazione e ritorno aiuto), verifica audiovisiva manuale e tipografia aiuto.\n'
 'Nessuna percentuale globale attendibile. Le note successive sono storiche.\n\n')
if not s.startswith('# Ripresa: salvataggi P519'):s=heading+s
p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P519 v5 saves verified 16 October 2026. Matching build, 104 round trips (74 gameplay + 30 resource compositions), corruption/slot/fresh-process tests, P505/P508 compatibility, exploration saves/import, help and full WASAPI suite PASS. No tests running. See NEXT-STEPS.md.\n')
print('P519 save checkpoint PASS')
