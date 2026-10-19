"""Read the frozen v11 slot before exercising v12 and all older suites."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve();slot=base/'p513-save-regression/astro-verify.010';before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-p513-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'p513-save-regression'),'--logfile='+str(base/'p513-previous-slot.log'),'--debuglevel=1','--save-slot=10','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
s=(base/'p513-previous-slot.log').read_text();assert p.returncode==0 and 'P513 startup save: PASS' in s and 'FAIL' not in s and before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'p513-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',slot_sha256=before,unchanged=True),indent=2));print('Previous P513 v11 slot compatibility PASS',flush=True)
for name in ('check_p517_saves.py','check_builder_boundaries.py','check_p513_regressions.py'):
 print('Starting '+name,flush=True);p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True);print(p.stdout[-4500:]+p.stderr[-1000:],flush=True);assert p.returncode==0,name
print('P517 v12 and all compatible native regression suites PASS',flush=True)
