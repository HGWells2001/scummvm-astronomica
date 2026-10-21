"""Read frozen v14, audit v15, then run all existing native regression suites."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
b=Path('work/fresh-20260913').resolve();exe=b/'build/Releasex64/scummvm.exe';slot=b/'verified-checkpoints/rocket-e1c05225769c/frozen-slot13/astro-verify.013'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((b/'verified-checkpoints/rocket-e1c05225769c/frozen-slot13.json').read_text())
assert frozen['producing_exe_sha256']=='e1c05225769cb9411a1b849abe7530cb36ee24114a3cf65bac446c587b903d3c' and frozen['slot_sha256']==d(slot)
before=d(slot);env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
log=b/'rocket-previous-slot.log'
p=subprocess.run([str(exe),'--config='+str(b/'verify-rocket-saves.ini'),'--extrapath='+str(b/'fonts'),'--savepath='+str(slot.parent),'--logfile='+str(log),'--debuglevel=1','--save-slot=13','astro-verify'],env=env,cwd=b,capture_output=True,text=True,timeout=180)
s=log.read_text();assert p.returncode==0 and 'rocket startup save: PASS' in s and 'FAIL' not in s and 'Log closed successfully' in s and before==d(slot),s[-3000:]
(b/'rocket-previous-slot-proof.json').write_text(json.dumps(dict(date='2026-10-21',status='PASS',exe_sha256=d(exe),slot_sha256=before,producing_exe_sha256=frozen['producing_exe_sha256'],origin_commit=frozen['origin_commit'],unchanged=True),indent=2));print('Previous rocket v14 slot compatibility PASS',flush=True)
for name,extra in [('check_universe_boundaries.py',[]),('check_universe_saves.py',['--frame-audit-proof',str(b/'universe-boundaries-proof.json')]),('check_rocket_regressions.py',[])]:
 print('Starting '+name,flush=True)
 p=subprocess.run([sys.executable,str(b/name),*extra],text=True)
 assert p.returncode==0,name
print('Universe v15 and all compatible native regression suites PASS',flush=True)
