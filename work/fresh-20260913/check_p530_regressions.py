"""Retain the prior v8 slot, then test v9 and every earlier compatible suite."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve();slot=base/'p528-save-regression/astro-verify.007'
before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-p528-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'p528-save-regression'),'--logfile='+str(base/'p528-previous-slot.log'),'--debuglevel=1','--save-slot=7','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
log=(base/'p528-previous-slot.log').read_text()
assert p.returncode==0 and 'P528 startup save: PASS' in log and 'FAIL' not in log and before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'p528-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',slot_sha256=before,unchanged=True),indent=2))
print('Previous P528 v8 slot compatibility PASS',flush=True)
for name in ('check_p530_saves.py','check_p528_regressions.py'):
 print('Starting '+name,flush=True)
 p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True)
 print(p.stdout[-4500:]+p.stderr[-1000:],flush=True)
 assert p.returncode==0,name
print('P530 v9 and full compatible regression suite PASS',flush=True)
