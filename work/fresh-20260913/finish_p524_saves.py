"""Finalize P524 only after the targeted tests and complete compatible build pass."""
from pathlib import Path
import ast,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
# Reuse the prior required log list as data, without executing an old finalizer.
tree=ast.parse((work/'finish_p519_saves.py').read_text())
required=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='required' for t in n.targets))
required.update({'p524-saves.log':['P524 saves: PASS (72 boundaries, 48 animation cases, 2612 truncations, 2612 corruptions, 21 invalid states','P524 save verification: PASS'],
 'p524-saves-startup.log':['P524 startup save: PASS'], 'p519-previous-slot.log':['P519 startup save: PASS']})
for name,markers in required.items():
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime,name
 assert 'FAIL' not in s and 'Log closed successfully' in s,name
 for marker in markers:assert marker in s,(name,marker)
for p in (root/'engine/astronomica').iterdir():
 if p.is_file():
  assert p.read_bytes()==(work/'scummvm/engines/astronomica'/p.name).read_bytes(),p
  assert p.stat().st_mtime<exe.stat().st_mtime,p
proof=json.loads((work/'p524-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed']
for scene in (505,508,519,524):
 for src,dst in [('saves.log','saves-runtime.log'),('saves-startup.log','saves-startup.log'),('save-proof.json','save-proof.json')]:
  shutil.copyfile(work/f'p{scene}-{src}',root/'evidence'/f'p{scene}-{dst}')
for scene in (505,508,519):
 for suffix in ('previous-slot.log','previous-slot-proof.json'):shutil.copyfile(work/f'p{scene}-{suffix}',root/'evidence'/f'p{scene}-{suffix}')
for name,dest in [('help.log','help-native-runtime.log'),('legacy.log','legacy-runtime.log'),('legacy-file-proof.json','legacy-file-proof.json')]:shutil.copyfile(work/name,root/'evidence'/dest)
validation=dict(date='2026-10-18',status='PASS',format_version=6,payload_bytes=2612,scene=524,boundaries=72,gameplay_successor_comparisons=23,post_help_identity=1,animation_cases=48,
 solve_routes=2,moon_last=True,third_error_exit=True,voluntary_exit=True,mentor_return=True,truncations=2612,byte_corruptions=2612,invalid_checksummed_states=21,
 fresh_process_slot=5,fresh_process_fingerprint=proof['fresh_process_fingerprint'],music='Ambient restarts from beginning',compatibility='Exploration v1/v2, P508 v3, P505 v4 and P519 v5 retained; prior-build v3/v4/v5 slots unchanged',limitations=['Other puzzle saves remain unsupported','No complete manual audiovisual playthrough'])
(root/'evidence/p524-saves-validation.json').write_text(json.dumps(validation,indent=2))
note=('\n\n## P524 native saves, 18 October 2026\n\n'
 'Native v6 saves settled P524 questions with all script/RNG state, previous scene, clock/count, '
 '32 sprite frames/visibility and the continuing Triton animation epoch and parameters. '
 'Mentor return preserves the additional known local values. The original committed picture is reconstructed. '
 'The Moon follows all eight random choices; the earlier preparation calling it an initial stage was incorrect. '
 'Startup and foreground speech are skipped on load; ambient music restarts from the beginning.\n\n'
 'Validation: 72 round trips (23 gameplay successors, one post-help identity, 48 animation cases), '
 'all eight animation frames at 199/200/2200ms with ordinary and wrapping clocks, '
 'two solve routes, third-error exit, voluntary exit, mentor return and fresh-process slot5 completion. '
 '2612 truncations, 2612 byte corruptions and 21 checksummed invalid states reject atomically. '
 'Full P505/P508/P519 saves, prior-build v3/v4/v5 slots, exploration v1/v2, import, help and WASAPI suite pass on the same build. '
 'These are automated results, not manual audiovisual confirmation.\n')
for name in ('README.md','SAVE-RESEARCH.md','P524-SAVE-PLAN.md'):
 p=root/name;s=p.read_text()
 if '## P524 native saves, 18 October 2026' not in s:s+=note
 if name=='README.md':s=s.replace('Stato verificato: 16 ottobre 2026.','Stato verificato: 18 ottobre 2026.')
 p.write_text(s)
p=root/'NEXT-STEPS.md';s=p.read_text();heading=('# Ripresa: salvataggi P524, 18 ottobre 2026\n\n'
 'P524 v6: 72 ripristini, 48 casi animazione Tritone, ritorno aiuto e nuovo processo PASS.\n'
 'P505/P508/P519, precedenti slot v3/v4/v5, esplorazione v1/v2, import, aiuto e suite WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_p524_saves.py. Test: check_p524_saves.py e check_p524_regressions.py.\n'
 'Leggere P524-SAVE-FORMAT.md. Prossimo: P526-SAVE-PLAN.md (tre animazioni e orbita), verifica audiovisiva manuale e tipografia aiuto.\n'
 'Correzione alla preparazione P524: la Luna segue le otto scelte casuali, non le precede.\n'
 'Nessuna percentuale globale attendibile. Le note successive sono storiche.\n\n')
if not s.startswith('# Ripresa: salvataggi P524'):s=heading+s
p.write_text(s)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P524 v6 saves verified 18 October 2026. Matching build, 72 round trips, animation/corruption/physical-slot/fresh-process tests, compatibility v1-v5 and full WASAPI suite PASS. No tests running. See NEXT-STEPS.md.\n')
print('P524 save checkpoint PASS')
