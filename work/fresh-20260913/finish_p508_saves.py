"""Finalize P508 saves only after all matching native regression evidence passes."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
required={'p508-saves.log':['P508 saves: PASS (63 boundaries, 291 continuation steps, 2464 truncations, 2464 corruptions','P508 save verification: PASS'],
 'p508-saves-startup.log':['P508 startup save: PASS','P508 save verification: PASS'],
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
proof=json.loads((work/'p508-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed']
for src,dst in [('p508-saves.log','p508-saves-runtime.log'),('p508-saves-startup.log','p508-saves-startup.log'),('p508-save-proof.json','p508-save-proof.json'),('help.log','help-native-runtime.log'),('legacy.log','legacy-runtime.log'),('legacy-file-proof.json','legacy-file-proof.json')]:
 shutil.copyfile(work/src,root/'evidence'/dst)
validation=dict(date='2026-10-15',status='PASS',format_version=3,payload_bytes=2464,scene=508,
 scope='Settled question boundaries only; no foreground speech, queued work, staged image, button pulse or motion',
 boundaries=63,continuation_steps=291,seeds=[1,48879,65535],routes=['eight correct','three wrong','eight correct with two interleaved errors'],
 truncations=2464,byte_corruptions=2464,invalid_checksummed_states=14,
 fresh_process_slot=2,fresh_process_fingerprint=proof['fresh_process_fingerprint'],
 music='Ambient loop resumes from its beginning; exact sample phase is not saved',
 compatibility='Exploration writes v2; v1/v2 loads retained',
 limitations=['Other puzzles still cannot be saved mid-puzzle','Full manual audiovisual playthrough remains outstanding'])
(root/'evidence/p508-saves-validation.json').write_text(json.dumps(validation,indent=2))
note=('\n\n## P508 settled question saves, 15 October 2026\n\n'
 'Native version3 now saves P508 between questions, including six locals, '
 'all global/local values and their known/width metadata, full32-bit RNG, '
 'program epoch, branch state, previous place, completion count, sprite '
 'visibility/frame selection and ambient audio state. Pending actions, '
 'foreground speech, staged images, moving sprites and button pulses are '
 'excluded. Original data confirms18 opaque508x108 pictures at(67,354); '
 'the selected picture reconstructs the background without storing media. '
 'Startup scripts and introduction are skipped on load. Ambient music '
 'restarts at the beginning, not at the exact saved sample.\n\n'
 'Three seeds and correct/wrong/mixed routes cover63 saved boundaries and '
 '291 resumed answer steps, comparing screen pixels, script data, RNG, '
 'sound IDs/counts, destination and completion count with uninterrupted '
 'runs. Save/load/save data is stable except for the advancing clock. '
 '2464 truncations,2464 byte corruptions and14 invalid checksummed states '
 'are rejected without changing the live state. Physical slot2 loads in '
 'a fresh process with the identical state/screen fingerprint and completes '
 'the seven remaining correct answers. Music/foreground guards and slot '
 'metadata pass. Exploration v1/v2 regressions, help and full WASAPI suite '
 'pass on the matching executable. Other puzzle saves remain unsupported.\n')
for name in ('README.md','SAVE-RESEARCH.md','P508-SAVE-PLAN.md'):
 p=root/name;s=p.read_text()
 if '## P508 settled question saves, 15 October 2026' not in s:s+=note
 if name=='README.md':
  s=s.replace('Stato verificato: 14 ottobre 2026.','Stato verificato: 15 ottobre 2026.')
  s=s.replace('Restano salvataggi durante i puzzle, fedelta tipografica e','P508 supporta ora salvataggi fra le domande. Restano salvataggi negli altri puzzle, fedelta tipografica e')
 if name=='P508-SAVE-PLAN.md':s=s.replace('This is implementation preparation, not newly supported saving. The current\nsave gate must remain unchanged until restoration and continuation pass.',
  'The plan below is retained as the pre-implementation contract. P508 settled\nquestion saving is now implemented and verified; see the dated result below.')
 p.write_text(s)
p=root/'NEXT-STEPS.md';s=p.read_text()
heading=('# Ripresa: salvataggi P508 fra le domande, 15 ottobre 2026\n\n'
 'Formato nativo v3: 63 punti, 291 continuazioni, slot reale e nuovo processo PASS.\n'
 'Build, salvataggi v1/v2, aiuto, import GAMESTAT e suite WASAPI PASS.\n'
 'Leggere SAVE-RESEARCH.md e p508-saves-validation.json. Test: check_p508_saves.py.\n'
 'Checkpoint: finish_p508_saves.py; verifica: verify_development_evidence.py.\n'
 'Prossimo: salvataggi negli altri puzzle e verifica audiovisiva integrale.\n'
 'Le note precedenti sotto sono storiche: P508 ora fa eccezione al divieto di\n'
 'salvare nei puzzle; gli altri restano esclusi. Nessuna percentuale globale.\n\n')
if not s.startswith('# Ripresa: salvataggi P508'):s=heading+s
p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P508 settled-question save checkpoint verified 15 October 2026. Matching build, 63 boundaries, 291 continuation steps, corruption/slot/fresh-process checks, native exploration saves/import, help and full WASAPI suite PASS. No tests running. See NEXT-STEPS.md.\n')
print('P508 save checkpoint PASS')
