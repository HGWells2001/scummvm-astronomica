"""Finalize P505 only after matching build and all native regressions pass."""
from pathlib import Path
import json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
required={
 'p505-saves.log':['P505 saves: PASS (38 boundaries and successor comparisons, 38 hover resumptions','P505 save verification: PASS'],
 'p505-saves-startup.log':['P505 startup save: PASS','P505 save verification: PASS'],
 'p508-saves.log':['P508 saves: PASS (63 boundaries, 291 continuation steps','P508 save verification: PASS'],
 'p508-saves-startup.log':['P508 startup save: PASS','P508 save verification: PASS'],
 'p508-previous-slot.log':['P508 startup save: PASS','P508 save verification: PASS'],
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
proof=json.loads((work/'p505-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed']
for scene in (505,508):
 for src,dst in [('saves.log','saves-runtime.log'),('saves-startup.log','saves-startup.log'),('save-proof.json','save-proof.json')]:
  shutil.copyfile(work/f'p{scene}-{src}',root/'evidence'/f'p{scene}-{dst}')
for name,dest in [('help.log','help-native-runtime.log'),('legacy.log','legacy-runtime.log'),('legacy-file-proof.json','legacy-file-proof.json')]:shutil.copyfile(work/name,root/'evidence'/dest)
for name in ('p508-previous-slot.log','p508-previous-slot-proof.json'):shutil.copyfile(work/name,root/'evidence'/name)
validation=dict(date='2026-10-15',status='PASS',format_version=4,payload_bytes=2472,scene=505,
 scope='Settled questions with idle scripts, static sprites and no foreground audio',boundaries=38,successor_comparisons=38,hover_resumptions=38,seeds=[1,48879],routes=['eight correct','three wrong','eight questions with two errors'],truncations=2472,byte_corruptions=2472,invalid_checksummed_states=16,fresh_process_slot=3,fresh_process_fingerprint=proof['fresh_process_fingerprint'],music='Ambient restarts from beginning',compatibility='Exploration v1/v2 and P508 v3 retained and retested',limitations=['Other puzzle saves unsupported','No full manual audiovisual playthrough'])
(root/'evidence/p505-saves-validation.json').write_text(json.dumps(validation,indent=2))
note=('\n\n## P505 settled question saves, 15 October 2026\n\n'
 'Native v4 saves P505 between questions. It retains all script state, RNG, completion count, '
 'sprite visibility/frame selection, ambient state and entered flags for four sprite and ten rectangle hover targets. '
 'The original eight opaque 135x86 pictures at (254,362) reconstruct the current question. '
 'Loading skips startup and speech; remaining on a highlighted target does not replay its entry event. '
 'Foreground speech, queued work, staged pictures and button pulses exclude saving. Music restarts from its beginning.\n\n'
 'Two seeds and correct/wrong/mixed routes verify 38 saved boundaries and their 38 successor states against uninterrupted play, '
 'including screen, script/RNG, sound count/ID and hover exit. All 38 unchanged-hover checks pass. '
 '2472 truncations, 2472 byte corruptions and 16 checksummed invalid states reject atomically. '
 'Physical slot 3 restores in a fresh process with the same fingerprint and finishes six remaining answers. '
 'P508 v3 (63 boundaries, 291 resumed steps), exploration v1/v2, original GAMESTAT import, help and full WASAPI regressions pass on the matching build. '
 'These are automated tests; manual audiovisual verification and saves in other puzzles remain outstanding.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=root/name;s=p.read_text()
 if '## P505 settled question saves, 15 October 2026' not in s:s+=note
 if name=='README.md':s=s.replace('P508 supporta ora salvataggi fra le domande.','P505 e P508 supportano ora salvataggi fra le domande.')
 p.write_text(s)
p=root/'NEXT-STEPS.md';s=p.read_text()
heading=('# Ripresa: salvataggi P505 e P508, 15 ottobre 2026\n\n'
 'P505 v4: 38 punti e confronti del passo successivo, hover, slot reale e nuovo processo PASS.\n'
 'P508 v3: 63 punti e 291 passi ripristinati PASS. Compatibilita v1/v2, import, aiuto e suite WASAPI PASS.\n'
 'Checkpoint: finish_p505_saves.py. Test: check_p505_saves.py e check_p508_saves.py.\n'
 'Prossimo: P519-SAVE-PLAN.md (due immagini originali bastano per lo sfondo; implementazione ancora assente), verifica audiovisiva manuale e tipografia aiuto.\n'
 'Nessuna percentuale globale attendibile. Le note successive sono storiche.\n\n')
if not s.startswith('# Ripresa: salvataggi P505'):s=heading+s
p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P505/P508 settled-question saves verified 15 October 2026. Matching build, native continuation/hover/corruption/slot/fresh-process tests, exploration saves/import, help and full WASAPI suite PASS. No tests running. See NEXT-STEPS.md.\n')
print('P505 save checkpoint PASS')
