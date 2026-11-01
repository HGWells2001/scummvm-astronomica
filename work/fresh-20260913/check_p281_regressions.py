"""Same-main genuine v29,v28,all prior natives,then actual P281 paths."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,traceback
from p281_integration_gate import validated_p281_integration
w=Path(__file__).resolve().parent;r=w.parents[1];os.chdir(r);d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();exe=w/'build/Releasex64/scummvm.exe';expected=d(exe);state=w/'p281-regressions-status.json'
assert os.environ.get('ASTRONOMICA_REVIEWED_DESCENDANT')=='p281-sealed29'
def journal(status,**kw):
    tmp=state.with_suffix('.tmp');tmp.write_text(json.dumps(dict(status=status,exe_sha256=expected,updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n');tmp.replace(state)
try:
    for name,args in [('check_frozen_p512_v29.py',['--exe',exe,'--out',w/'p281-main-frozen-v29']),('check_p512_regressions.py',[]),('check_p281_gateway.py',['--exe',exe,'--out',w/'p281-main-gateway'])]:
        validated_p281_integration(r,w,expected);assert d(exe)==expected;journal('RUNNING',step=name)
        print('Starting '+name,flush=True);subprocess.run([sys.executable,str(w/name),*map(str,args)],cwd=r,check=True)
        if name=='check_p512_regressions.py' and 'clock_revision' in json.loads((w/'p281-integration.json').read_text()):
            from p512_clock_revision import validate_native
            validate_native(w/'p512-save-proof.json',w/'p512-save-regression',expected)
    validated_p281_integration(r,w,expected)
    journal('PASS',full_suite=True,native_save_scenes=33,source_context_sha256=d(w/'p281-integration.json'),gateway_proof_sha256=d(w/'p281-main-gateway/gateway-proof.json'),genuine_v29_proof_sha256=d(w/'p281-main-frozen-v29/frozen-v29-proof.json'))
except Exception:
    journal('FAILED',error=traceback.format_exc());raise
