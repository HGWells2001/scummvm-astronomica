"""Commit local evidence only after native game-state checks and full suite pass."""
from pathlib import Path
import json,subprocess,sys,shutil
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
markers=('game state original comparison: PASS','game state boundary verification: PASS',
 'game state interaction verification: PASS','P407 keypad verification: PASS','P422 keypad verification: PASS')
for name in ('runtime.log','game_state.log'):
 text=(work/name).read_text();assert 'FAIL' not in text,name
 for marker in markers:assert marker in text,(name,marker)
 if name=='runtime.log':assert 'Astronomica script verification: PASS' in text
text=(work/'transitions.log').read_text()
assert 'transition integration verification: PASS' in text and 'FAIL' not in text
note='''

## Game-wide state checkpoint, 4 October 2026

Custom26 is integrated and matches2436 original instruction cases plus42
resume/memory boundaries. Cabinet/item persistence, world-door flag, live
completion count, hub indicators, credit bookkeeping and the P407/P422
keypad sequences pass native checks. Global voices and zero-layer exploration
images now support those original scripts. Full regression passes. See
GAME-STATE-RESEARCH.md for explicit legacy resume/memory adaptations.
P409 custom27 research covers34800 cases; it is not integrated yet. No new
whole-game percentage or manual completion is claimed.
'''
for name in ('README.md','INTERPRETER.md','PROGRESSION-RESEARCH.md','GAME-STATE-RESEARCH.md'):
 p=root/name
 if b'## Game-wide state checkpoint, 4 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
(root/'evidence/game-state-validation.json').write_text(json.dumps(dict(status='PASS',
 original_cases=2436,comparison_fnv='d253e90a',boundary_cases=42,boundary_fnv='662a3a5a',
 world_interaction_scenes=[35,85,98,352,359,388,407,422,425],full_suite=True,
 manual_confirmation=False,legacy_resume=False,p409_advice_integrated=False),indent=2))
p=root/'NEXT-STEPS.md';s=p.read_text()
s=s.replace('# Ripresa: regole di progressione integrate, 4 ottobre 2026',
 '# Ripresa: stato generale e pannelli mondo integrati, 4 ottobre 2026')
a=s.index('Proseguire dal comando custom26:');b=s.index('Regole transizione:',a)
s=s[:a]+'''Custom26 integrato:2436 casi e42 limiti originali/native PASS.
P359/P352 oggetto persistente, P35/P85 porta, P98 contatore, P388 indicatori,
P407/P422 tastiere e P425 crediti verificati. Leggere GAME-STATE-RESEARCH.md.
Proseguire con P409: probe_p409_advice.py,34800 casi originali, FNVbcb8ca85.
Custom27/32 non ancora integrati. Custom32:108 casi, FNVbf6ea917, clock
MMSYSTEM607 confermato. Verificare ciclo globale8 e ritorno/permesso57.
Restano filmati esplorazione, aiuto Windows, resume originale, salvataggi
interni ai puzzle e percorso integrale. I pannelli mondo non aumentano la
metrica delle35 scene di puzzle; conferma manuale sempre soloP508.
'''+s[b:]
s=s.replace('Checkpoint:record_transitions_checkpoint.py;',
 'Test stato:check_game_state.py. Checkpoint:record_game_state_checkpoint.py;')
p.write_text(s,encoding='utf-8')
p=work/'refresh_research_evidence.py';s=p.read_text()
if "'GAME-STATE-RESEARCH.md'" not in s:
 s=s.replace('files.update(root/name for name in (',
 "files.update(root/name for name in ('GAME-STATE-RESEARCH.md','evidence/game-state-validation.json','evidence/p409-advice.json','evidence/p409-clock.json','evidence/p409-return.json',",1)
p.write_text(s)
p=work/'save_development_evidence.py';s=p.read_text()
guard="assert 'game state interaction verification: PASS' in log"
if guard not in s:s=s.replace("for name in ['runtime.log'",guard+"\nfor name in ['runtime.log'",1)
p.write_text(s)
shutil.copyfile(work/'game_state.log',root/'evidence/game-state-runtime.log')
shutil.copyfile(work/'transitions.log',root/'evidence/transitions-runtime.log')
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
print('Game-wide state checkpoint saved and verified')
