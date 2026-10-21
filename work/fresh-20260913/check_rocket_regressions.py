"""Read the frozen v13 slot before exercising v14 and all older suites."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve();slot=base/'builder-save-regression/astro-verify.012';before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-builder-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'builder-save-regression'),'--logfile='+str(base/'builder-previous-slot.log'),'--debuglevel=1','--save-slot=12','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
s=(base/'builder-previous-slot.log').read_text();assert p.returncode==0 and 'builder startup save: PASS' in s and 'FAIL' not in s and before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'builder-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-21',status='PASS',slot_sha256=before,unchanged=True),indent=2));print('Previous builder v13 slot compatibility PASS',flush=True)
for name in ('check_rocket_saves.py','check_rocket_boundaries.py','check_builder_regressions.py'):
 print('Starting '+name,flush=True);p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True);print(p.stdout[-4500:]+p.stderr[-1000:],flush=True);assert p.returncode==0,name
print('Rocket v14 and all compatible native regression suites PASS',flush=True)
