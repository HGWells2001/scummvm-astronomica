"""Sequential audio regressions, retaining a previous-build P508 slot check."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
base=Path('work/fresh-20260913').resolve()
# Run before regenerating the P508 fixture: this slot was written by the last
# verified build. Never copy or inspect user saves; this directory is test-only.
slot=base/'p508-save-regression/astro-verify.002'
before=hashlib.sha256(slot.read_bytes()).hexdigest()
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(base/'verify-p508-saves.ini'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base/'p508-save-regression'),'--debuglevel=1','--logfile='+str(base/'p508-previous-slot.log'),'--save-slot=2','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=120)
log=(base/'p508-previous-slot.log').read_text()
assert p.returncode==0 and 'P508 startup save: PASS' in log and 'FAIL' not in log
assert before==hashlib.sha256(slot.read_bytes()).hexdigest()
(base/'p508-previous-slot-proof.json').write_text(json.dumps(dict(status='PASS',slot_sha256=before,unchanged=True),indent=2))
print('Previous P508 v3 slot compatibility PASS',flush=True)
for name,extra in [('check_p508_saves.py',[]),('check_help.py',[]),('check_saves.py',[]),('check_legacy.py',[]),('runtime_test.py',['--real-audio'])]:
 print('Starting '+name,flush=True)
 p=subprocess.run([sys.executable,str(base/name)]+extra,capture_output=True,text=True)
 print(p.stdout[-1800:]+p.stderr[-600:],flush=True)
 assert p.returncode==0,name
print('Question-save regression suite PASS',flush=True)
