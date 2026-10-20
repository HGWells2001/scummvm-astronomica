"""Read the frozen v12 slot before exercising v13 and all older suites."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve();slot=base/'p517-save-regression/astro-verify.011';before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-p517-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'p517-save-regression'),'--logfile='+str(base/'p517-previous-slot.log'),'--debuglevel=1','--save-slot=11','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
s=(base/'p517-previous-slot.log').read_text();assert p.returncode==0 and 'P517 startup save: PASS' in s and 'FAIL' not in s and before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'p517-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',slot_sha256=before,unchanged=True),indent=2));print('Previous P517 v12 slot compatibility PASS',flush=True)
for name in ('check_builder_saves.py','check_p537_readout.py','check_p517_regressions.py'):
 print('Starting '+name,flush=True);p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True);print(p.stdout[-4500:]+p.stderr[-1000:],flush=True);assert p.returncode==0,name
print('Builder v13 and all compatible native regression suites PASS',flush=True)
