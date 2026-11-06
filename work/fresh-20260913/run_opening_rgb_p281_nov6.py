"""Verify the existing P281 release routes on the exact P525 candidate."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,traceback
w=Path(__file__).resolve().parent;status=w/'opening-rgb-p281-nov6-status.json'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**kw):status.write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
    p=json.loads((w/'opening-rgb-fresh-nov6/proof.json').read_text());assert p['status']=='P523_ASVM31_COMPLETE_SIX_FRESH_PROCESSES_PASS'
    exe=w/'opening-rgb-nov6-stage/complete-build/bin/scummvm.exe';assert d(exe)==p['candidate_exe_sha256']
    original=w/'check_p281_gateway.py';text=original.read_text();old='[scummvm]'+chr(92)+'n';new=old+'mute=true'+chr(92)+'n'
    assert text.count(old)==1;modified=text.replace(old,new,1);assert modified.replace(new,old,1)==text
    helper=w/'check_opening_rgb_p281_muted_nov6.py';assert not helper.exists();helper.write_text(modified)
    out=w/'opening-rgb-p281-nov6';state('RUNNING_P281_GATEWAY_ON_CANDIDATE',exe_sha256=d(exe),parent_checker_sha256=d(original),only_delta='Global mute=true')
    subprocess.run([sys.executable,str(helper),'--exe',str(exe),'--out',str(out)],cwd=w.parents[1],check=True)
    result=json.loads((out/'gateway-proof.json').read_text());assert result['status']=='PASS' and result['exe_sha256']==p['candidate_exe_sha256']
    state('PASS',proof_sha256=d(out/'gateway-proof.json'))
except Exception:state('FAILED',error=traceback.format_exc());raise
