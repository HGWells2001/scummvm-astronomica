from pathlib import Path
import json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
markers=('advice original comparison: PASS','advice clock comparison: PASS','countdown original comparison: PASS','advice continuous playback: PASS','advice/countdown interaction verification: PASS')
for name in ('runtime.log','advice.log'):
 text=(work/name).read_text();assert 'FAIL' not in text,name
 for marker in markers:assert marker in text,(name,marker)
 if name=='runtime.log':assert 'Astronomica script verification: PASS' in text
for name in ('runtime.log','endings.log'):
 text=(work/name).read_text();assert 'FAIL' not in text
 assert 'endings interaction verification: PASS' in text and 'ending continuous playback: PASS' in text
for name in ('saves.log','saves-startup.log'):
 text=(work/name).read_text();assert 'save verification: PASS' in text and 'FAIL' not in text
(root/'evidence/endings-validation.json').write_text(json.dumps(dict(status='PASS',scenes=[423,424,435,436,437],original_choices=4,decoded_movies=5,continuous_lead_in=True,credit_transitions=True,full_suite=True,manual_confirmation=False),indent=2))
(root/'evidence/advice-validation.json').write_text(json.dumps(dict(status='PASS',advice_cases=34800,advice_fnv='bcb8ca85',clock_cases=108,clock_fnv='bf6ea917',countdown_cases=10530,countdown_fnv='0ae350b7',native_scenarios=8,continuous_movie=True,world_timer_sounds=7,saved_clock_wrap=True,full_suite=True,manual_confirmation=False),indent=2))
p=root/'evidence/game-state-validation.json';d=json.loads(p.read_text());d['p409_advice_integrated']=True;p.write_text(json.dumps(d,indent=2))
p=root/'evidence/saves-validation.json';d=json.loads(p.read_text());d.update(native_version=2,native_prefix_bytes=424,truncations=424,corruptions=424,legacy_inactive_version1=True,saved_clock=True);p.write_text(json.dumps(d,indent=2))
p=root/'NEXT-STEPS.md';s=p.read_text();s=s.replace('# Ripresa: stato generale e pannelli mondo integrati, 4 ottobre 2026','# Ripresa: P409 e conto alla rovescia integrati, 5 ottobre 2026')
a=s.index('Proseguire con P409:');b=s.index('Restano filmati esplorazione',a)
s=s[:a]+"P409 custom27/32 integrati:34800+108 casi originali/native PASS.\nConto alla rovescia:10530 casi, sette WAV e passaggio427 verificati.\nSalvataggi versione2 conservano il clock; versione1 inattiva compatibile.\nLeggere P409-RESEARCH.md. Test consigli:check_advice.py.\nFinali423/424/435..437:quattro scelte, cinque filmati e crediti verificati.\nProssimo:coda432/433/0 e introduzione2/4; restano da integrare.\nInventario originale:probe_world_movies.py; P4 legge il filmato daP2.\nP2 richiede opcode50 palette:ricerca avviata, non implementato.\n"+s[b:]
s=s.replace('record_game_state_checkpoint.py','record_advice_checkpoint.py');p.write_text(s,encoding='utf-8')
for name in ('README.md','INTERPRETER.md','SAVE-RESEARCH.md','GAME-STATE-RESEARCH.md'):
 p=root/name
 if b'## Advice checkpoint, 5 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(b'\n\n## Advice checkpoint, 5 October 2026\n\nP409 custom27/32 and world countdown are integrated and verified against\n34800/108/10530 original cases. Native interaction, seven warning sounds,\nexpiry and continuous advice playback pass. Saves now use version2 (424\nbyte prefix) with clock epoch; inactive version1 remains readable. See\nP409-RESEARCH.md. Four ending routes423/424/435..437 now play five movies and reach credits.\nFull suite PASS; no global completion percentage claimed.\n')
for src,dst in [('advice.log','advice-runtime.log'),('endings.log','endings-runtime.log'),('saves.log','saves-runtime.log'),('saves-startup.log','saves-startup.log'),('saves-list.log','saves-list.log')]:shutil.copyfile(work/src,root/'evidence'/dst)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Complete native suite PASS; advice/countdown checkpoint finalized and integrity verified. Resume from NEXT-STEPS.md.\n')
print('Advice/countdown checkpoint saved and verified')
