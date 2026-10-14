"""Finalize only after the current transition and complete native suites pass."""
from pathlib import Path
import json,subprocess,sys,shutil
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
for name in ('runtime.log','transitions.log'):
 text=(work/name).read_text()
 assert 'FAIL' not in text,name
 for marker in ('transition original comparison: PASS','transition integration verification: PASS',
                'denial interludes verification: PASS','credits images verification: PASS'):
  assert marker in text,(name,marker)
 if name=='runtime.log':assert 'Astronomica script verification: PASS' in text
note='''

## Scene progression checkpoint, 4 October 2026

Original transition rules are integrated: nine directed world gates, consumed
permit, puzzle-entry prerequisite, and global denial/unsolved-exit voices.
47,520 original instruction cases and native comparison pass. P429's five
denial movie segments, P427, P426/P428 timed exits and seven P425 credit images
are tested. The complete native regression suite passes. See
PROGRESSION-RESEARCH.md. This does not establish a complete game route:
custom26 inventory/state transfers remain unimplemented. Independent original
research now covers2436 custom26 cases and42 resume/memory boundaries.
The35 verified puzzle-route scenes and manual confirmation scope are unchanged.
'''
for name in ('README.md','INTERPRETER.md','PROGRESSION-RESEARCH.md'):
 p=root/name
 if b'## Scene progression checkpoint, 4 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
(root/'evidence/transitions-validation.json').write_text(json.dumps(dict(status='PASS',
 original_cases=47520,comparison_fnv='03a3e23b',world_gates=9,denial_segments=5,
 scene_exits=[426,427,428,429],credit_images=7,full_suite=True,
 manual_confirmation=False,whole_game_completion_percent=None,
 remaining='custom26 state transfers, other exploration movies, Windows help, full playthrough'),indent=2))
p=root/'NEXT-STEPS.md';s=p.read_text()
s=s.replace('# Ripresa: salvataggi esplorazione integrati, 4 ottobre 2026',
 '# Ripresa: regole di progressione integrate, 4 ottobre 2026')
s=s.replace('Proseguire con aiuto Windows (custom22/process_help), ripresa interna ai puzzle\ne percorso generale.',
 '''Proseguire dal comando custom26: inventario/stato generale ancora mancante.
Leggere PROGRESSION-RESEARCH.md, progression-inventory.json e game-state.json.
probe_game_state.py:2436 casi originali, FNVd253e90a; nessun supporto nativo
ancora abilitato per custom26. Restano inoltre filmati di esplorazione,
aiuto Windows, ripresa interna ai puzzle e percorso integrale.
Regole transizione:47520 casi originali/native PASS; nove passaggi condizionati,
voci S10/S11, P429->P427->P425 e immagini crediti verificati automaticamente.''')
s=s.replace('Checkpoint:record_saves_checkpoint.py;',
 'Test progressione:check_transitions.py. Checkpoint:record_transitions_checkpoint.py;')
p.write_text(s,encoding='utf-8')
p=work/'refresh_research_evidence.py';s=p.read_text()
if "'PROGRESSION-RESEARCH.md'" not in s:
 s=s.replace('files.update(root/name for name in (',
 "files.update(root/name for name in ('PROGRESSION-RESEARCH.md','evidence/transitions.json','evidence/transitions-validation.json','evidence/progression-inventory.json','evidence/game-state.json',",1)
 s=s.replace("{'PLACES/P510/FLATPLOT.MOV'", "{'SOUNDS/S10.WAV','SOUNDS/S11.WAV','PLACES/P429/F21G.MOV','PLACES/P427/END_BOOM.MOV','PLACES/P426/F23B.MOV','PLACES/P428/F23A.MOV','PLACES/P510/FLATPLOT.MOV'",1)
p.write_text(s)
p=work/'save_development_evidence.py';s=p.read_text()
guard="assert 'transition integration verification: PASS' in log"
if guard not in s:s=s.replace("for name in ['runtime.log'",guard+"\nfor name in ['runtime.log'",1)
p.write_text(s)
shutil.copyfile(work/'transitions.log',root/'evidence/transitions-runtime.log')
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
print('Scene progression checkpoint saved and verified')
