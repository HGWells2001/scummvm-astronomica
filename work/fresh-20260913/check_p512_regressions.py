"""ASVM29 main closure with an explicit reviewed descendant source context.

Historical check_p510_regressions.py keeps its original whole-file hashes.
This successor independently checks the P512-only source merge, both genuine
v28 identities, genuine v27, P510 native contract, and the entire prior chain.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,traceback
from p512_integration_gate import validated_integration,active_context_path
from p510_ordinary_gate import validated_ordinary

w=Path(__file__).resolve().parent;root=w.parents[1];os.chdir(root)
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();exe=w/'build/Releasex64/scummvm.exe';expected=d(exe)
state=w/'p512-regressions-status.json'
def journal(path,status,**kw):
    pending=path.with_suffix('.tmp');pending.write_text(json.dumps(dict(status=status,exe_sha256=expected,updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n');pending.replace(path)
def run(name,*args):
    validated_integration(root,w,expected);assert d(exe)==expected
    journal(state,'RUNNING',step=name);print('Starting '+name,flush=True)
    subprocess.run([sys.executable,str(w/name),*map(str,args)],cwd=root,check=True)
try:
    integration,_=validated_integration(root,w,expected)
    ordinary=w/'p510-main-ordinary-entry'
    validated_ordinary(ordinary/'ordinary-entry-gate-proof.json',ordinary,expected,ordinary/'astro-verify.027')
    run('check_frozen_p510_v28.py','--exe',exe,'--out',w/'p512-main-frozen-v28')
    # Real historical v27 input, independently preserved by its sealed owner.
    snapshot=w/'verified-checkpoints/p501-025e82d8bd3b';slot=snapshot/'frozen-slot26/astro-verify.026'
    frozen=json.loads((snapshot/'frozen-slot26.json').read_text())
    assert frozen['status']=='FROZEN_VERIFIED_V27' and frozen['origin_commit']=='ad2ec32fa658919c65e920c2c2609d3610061acd'
    assert frozen['slot_sha256']==d(slot)=='adcc9b9be47d0b7153a94eb3b9883b85a12090fbd64e8793e32e61daeeea81fa'
    env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
    log=w/'p501-v27-previous-slot.log'
    result=subprocess.run([str(exe),'--config='+str(w/'verify-p501-saves.ini'),'--extrapath='+str(w/'fonts'),'--savepath='+str(slot.parent),'--logfile='+str(log),'--debuglevel=1','--save-slot=26','astro-verify'],cwd=w,env=env,capture_output=True,text=True,timeout=240)
    text=log.read_text();assert result.returncode==0 and 'P501 startup save: PASS' in text and 'FAIL' not in text and 'Using SDL Audio Driver "wasapi"' in text and text.rstrip().endswith('--- Log closed successfully.')
    assert d(slot)==frozen['slot_sha256'] and d(exe)==expected
    (w/'p501-v27-previous-slot-proof.json').write_text(json.dumps(dict(status='PASS',date=datetime.now().date().isoformat(),exe_sha256=expected,slot_sha256=d(slot),producing_exe_sha256=frozen['producing_exe_sha256'],origin_commit=frozen['origin_commit'],unchanged=True,audio_driver='wasapi',log_sha256=d(log)),indent=2)+'\n')
    # The complete general fixture consumes the existing read-only aliases.
    assert d(w/'astro-verify.098')==d(slot)
    assert d(w/'astro-verify.099')=='2cb6bf34b1e42c895a9aa4ddddafd931253545d5f59d802b4458946787f8b92a'
    run('check_p510_saves.py')
    run('check_p501_regressions.py')
    validated_integration(root,w,expected)
    journal(w/'p510-regressions-status.json','PASS',full_suite=True,native_save_scenes=32,descendant_context=active_context_path(w).name,genuine_v28_proof_sha256=d(w/'p512-main-frozen-v28/frozen-v28-proof.json'))
    run('check_p512_saves.py')
    validated_integration(root,w,expected);assert d(exe)==expected
    journal(state,'PASS',full_suite=True,native_save_scenes=33,descendant_context_sha256=d(active_context_path(w)),genuine_v28_proof_sha256=d(w/'p512-main-frozen-v28/frozen-v28-proof.json'))
    print('ASVM29 exact-main P512,real v28/v27 and full inherited native chain PASS',flush=True)
except Exception:
    journal(state,'FAILED',error=traceback.format_exc());raise
