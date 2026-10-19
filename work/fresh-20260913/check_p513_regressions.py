"""Retain a previous-build v10 family slot, then test v11 and all older suites."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve();slot=base/'variant-save-regression/astro-verify.009';before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-variant-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'variant-save-regression'),'--logfile='+str(base/'variant-previous-slot.log'),'--debuglevel=1','--save-slot=9','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
s=(base/'variant-previous-slot.log').read_text();assert p.returncode==0 and 'variant startup save: PASS' in s and 'FAIL' not in s and before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'variant-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',slot_sha256=before,unchanged=True),indent=2));print('Previous custom17 v10 slot compatibility PASS',flush=True)
for name in ('check_p513_saves.py','check_variant_regressions.py'):
 print('Starting '+name,flush=True);p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True);print(p.stdout[-4500:]+p.stderr[-1000:],flush=True);assert p.returncode==0,name
print('P513 v11 and all compatible native regression suites PASS',flush=True)
