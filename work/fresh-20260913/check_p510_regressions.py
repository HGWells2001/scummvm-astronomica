"""Same-main P510, genuine frozen v27, then the entire existing P501 chain."""
from pathlib import Path
from datetime import datetime
import hashlib,json,os,shutil,subprocess,sys,traceback
root=Path(__file__).resolve().parents[2];os.chdir(root);w=root/'work/fresh-20260913';exe=w/'build/Releasex64/scummvm.exe';d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(exe);state=w/'p510-regressions-status.json'
def journal(status,**kw):
 temporary=state.with_suffix('.tmp');temporary.write_text(json.dumps(dict(status=status,exe_sha256=expected,**kw),indent=2));temporary.replace(state)
try:
 from p510_ordinary_gate import validated_ordinary
 ordinary=w/'p510-main-ordinary-entry'
 validated_ordinary(ordinary/'ordinary-entry-gate-proof.json',ordinary,expected,ordinary/'astro-verify.027')
 integration=json.loads((w/'p510-integration.json').read_text());assert integration['status']=='SOURCE_PROMOTED_AWAITING_BUILD_AND_NATIVE_SUITE' and expected!=integration['base_exe']
 for name,sha in integration['stage_sha256'].items():assert d(root/'outputs/astronomica-cleanroom/engine/astronomica'/name)==sha
 journal('RUNNING',step='genuine_frozen_v27')
 snapshot=w/'verified-checkpoints/p501-025e82d8bd3b';slot=snapshot/'frozen-slot26/astro-verify.026';frozen=json.loads((snapshot/'frozen-slot26.json').read_text())
 assert frozen['status']=='FROZEN_VERIFIED_V27' and frozen['origin_commit']=='ad2ec32fa658919c65e920c2c2609d3610061acd' and frozen['producing_exe_sha256']==integration['base_exe']
 assert frozen['slot_sha256']==d(slot)=='adcc9b9be47d0b7153a94eb3b9883b85a12090fbd64e8793e32e61daeeea81fa'
 env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None);log=w/'p501-v27-previous-slot.log'
 result=subprocess.run([str(exe),'--config='+str(w/'verify-p501-saves.ini'),'--extrapath='+str(w/'fonts'),'--savepath='+str(slot.parent),'--logfile='+str(log),'--debuglevel=1','--save-slot=26','astro-verify'],env=env,cwd=w,capture_output=True,text=True,timeout=240)
 text=log.read_text();assert result.returncode==0 and 'P501 startup save: PASS' in text and 'FAIL' not in text and 'Using SDL Audio Driver "wasapi"' in text and text.rstrip().endswith('--- Log closed successfully.')
 assert d(slot)==frozen['slot_sha256'] and d(exe)==expected
 (w/'p501-v27-previous-slot-proof.json').write_text(json.dumps(dict(status='PASS',date=datetime.now().date().isoformat(),exe_sha256=expected,slot_sha256=d(slot),producing_exe_sha256=frozen['producing_exe_sha256'],origin_commit=frozen['origin_commit'],unchanged=True,audio_driver='wasapi',log_sha256=d(log)),indent=2))
 # General runtime also invokes the exact staged P510 verifier. Its new
 # cross-scene diagnostic consumes aliases98/99 without touching frozen slots.
 for alias,source in [(98,slot),(99,w/'variant-save-regression/astro-verify.009')]:
  target=w/('astro-verify.%03d'%alias)
  if target.exists():
   # The general legacy test regenerates slot9, including dated metadata.
   # Retain the exact earlier verified alias99 instead of overwriting it.
   assert d(target)==d(source) or (alias==99 and d(target)=='2cb6bf34b1e42c895a9aa4ddddafd931253545d5f59d802b4458946787f8b92a'),'Unexpected existing diagnostic alias'
  else:shutil.copyfile(source,target)
 for name in ['check_p510_saves.py','check_p501_regressions.py']:
  journal('RUNNING',step=name);assert d(exe)==expected;subprocess.run([sys.executable,str(w/name)],check=True)
 assert d(exe)==expected and d(slot)==frozen['slot_sha256'];journal('PASS',full_suite=True,native_save_scenes=32)
 print('P510v28,genuine frozen v27,entire prior native chain PASS',flush=True)
except Exception:journal('FAILED',error=traceback.format_exc());raise
