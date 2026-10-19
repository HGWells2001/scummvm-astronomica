"""Retain the previous-build v9 slot, then run v10 and compatible suites."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve();slot=base/'p530-save-regression/astro-verify.008'
before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-p530-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'p530-save-regression'),'--logfile='+str(base/'p530-previous-slot.log'),'--debuglevel=1','--save-slot=8','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
log=(base/'p530-previous-slot.log').read_text()
assert p.returncode==0 and 'P530 startup save: PASS' in log and 'FAIL' not in log and before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'p530-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',slot_sha256=before,unchanged=True),indent=2))
print('Previous P530 v9 slot compatibility PASS',flush=True)
for name in ('check_save_entry_history.py','check_variant_saves.py','check_p530_regressions.py','check_local_launcher.py'):
 print('Starting '+name,flush=True)
 p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True)
 print(p.stdout[-4500:]+p.stderr[-1000:],flush=True)
 assert p.returncode==0,name
print('Custom17 v10, normal launcher startup and full compatible regression suite PASS',flush=True)
