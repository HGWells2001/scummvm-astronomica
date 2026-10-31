"""Serial native/evidence closure of a reviewed P512 descendant, no publication."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,traceback
from p512_integration_gate import validated_integration
w=Path(__file__).resolve().parent;r=w.parents[1];os.chdir(r)
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();exe=w/'build/Releasex64/scummvm.exe';expected=d(exe);state=w/'p512-checkpoint-status.json'
def journal(status,**kw):
    temporary=state.with_suffix('.tmp');temporary.write_text(json.dumps(dict(status=status,exe_sha256=expected,**kw),indent=2)+'\n');temporary.replace(state)
try:
    for name in ['check_p512_regressions.py','finish_p512_saves.py','finish_local_launcher.py']:
        validated_integration(r,w,expected);assert d(exe)==expected
        journal('RUNNING',step=name);subprocess.run([sys.executable,str(w/name)],check=True,cwd=r)
    validated_integration(r,w,expected)
    journal('PASS',full_suite=True,native_save_scenes=33,local_only=True,publication=False)
except Exception:
    journal('FAILED',error=traceback.format_exc());raise
