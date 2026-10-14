from pathlib import Path
import json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
marker='post-credits verification: PASS'
assert marker in (work/'postcredits.log').read_text()
try:
 subprocess.run([sys.executable,str(work/'runtime_test.py')],check=True)
 log=(work/'runtime.log').read_text();assert marker in log and 'FAIL' not in log and 'Astronomica script verification: PASS' in log
 (root/'evidence/postcredits-validation.json').write_text(json.dumps(dict(status='PASS',scenes=[432,433],movie_frames_decoded=True,motion_and_stop=True,timed_transitions=True,destination=0,logo_implemented=False,full_suite=True,manual_confirmation=False),indent=2))
 shutil.copyfile(work/'postcredits.log',root/'evidence/postcredits-runtime.log')
 note="\n\n## Post-credits checkpoint, 5 October 2026\n\nP432 RMC2.MOV and P433 FX.MOV are integrated. Original entry scripts\nreach433 after10000ms; in433 sprites move vertically after7000ms, stop\nafter15500ms, and enter0 after17000ms. Native boundary/movement tests\nand full regression PASS. Command19 now accepts the original disabled\ntimer(-1) with zero frame increment; active modes remain restricted to\nthe reconstructed forward cycle. The original parameters are retained.\nOriginal evidence: world-movie-inventory.json and command19 at15:0827-08b8.\nP0 logo/exit remains unsupported; no complete ending or manual playback\nclaim. Continuous playback of these two movies is not yet verified.\n"
 for name in ('README.md','INTERPRETER.md','P409-RESEARCH.md'):
  p=root/name
  if b'## Post-credits checkpoint, 5 October 2026' not in p.read_bytes():
   with p.open('ab') as f:f.write(note.encode('ascii'))
 p=root/'NEXT-STEPS.md';s=p.read_text();s=s.replace('Prossimo:coda432/433/0 e introduzione2/4; restano da integrare.','P432/P433 integrati:filmati, movimento/stop e tempi fino aP0 verificati.\nTest mirato:check_postcredits.py; checkpoint:finish_postcredits.py.\nProssimo:P0 logo/uscita e introduzione2/4; restano da integrare.\nVerificare anche playback continuo P432/P433. P0 ha quit in un ramo,\nancora rifiutato dalla validazione che richiede quit come ultimo comando.')
 s=s.replace('Checkpoint:record_advice_checkpoint.py','Checkpoint:finish_postcredits.py');p.write_text(s,encoding='utf-8')
 for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
  subprocess.run([sys.executable,str(work/name)],check=True)
 (root/'RUN-IN-PROGRESS.md').write_text('Complete suite and checkpoint integrity PASS, including post-credits P432/P433. Resume from NEXT-STEPS.md.\n')
 print('Post-credits full suite and checkpoint PASS')
except Exception:
 (root/'RUN-IN-PROGRESS.md').write_text('Post-credits targeted test PASS, but final suite/checkpoint failed. Inspect runtime.log and finish_postcredits.py before continuing.\n')
 raise
