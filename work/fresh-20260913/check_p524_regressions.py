"""P524 compatibility checks, using only previously generated test slots."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve()
slot=base/'p519-save-regression/astro-verify.004'
before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-p519-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'p519-save-regression'),'--debuglevel=1','--logfile='+str(base/'p519-previous-slot.log'),'--save-slot=4','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=120)
log=(base/'p519-previous-slot.log').read_text()
assert p.returncode==0 and 'P519 startup save: PASS' in log and 'FAIL' not in log
assert before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'p519-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-18',status='PASS',slot_sha256=before,unchanged=True),indent=2))
print('Previous P519 v5 slot compatibility PASS',flush=True)
for name in ('check_p519_saves.py','check_p519_regressions.py'):
 print('Starting '+name,flush=True)
 p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True)
 print(p.stdout[-2500:]+p.stderr[-600:],flush=True)
 assert p.returncode==0,name
print('P524 compatibility and full regression suite PASS',flush=True)
