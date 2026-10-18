"""P526 compatibility on the same executable; preserve prior test-only v6 slot."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve();slot=base/'p524-save-regression/astro-verify.005'
before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-p524-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'p524-save-regression'),'--debuglevel=1','--logfile='+str(base/'p524-previous-slot.log'),'--save-slot=5','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
log=(base/'p524-previous-slot.log').read_text()
assert p.returncode==0 and 'P524 startup save: PASS' in log and 'FAIL' not in log
assert before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'p524-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-18',status='PASS',slot_sha256=before,unchanged=True),indent=2))
print('Previous P524 v6 slot compatibility PASS',flush=True)
for name in ('check_p526_boundaries.py','check_p524_saves.py','check_p524_regressions.py'):
 print('Starting '+name,flush=True)
 p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True)
 print(p.stdout[-2500:]+p.stderr[-600:],flush=True)
 assert p.returncode==0,name
print('P526 compatibility and full regression suite PASS',flush=True)
