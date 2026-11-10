"""Capture genuine pre-fix ASVM29 files after natural original P512 routes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,struct,subprocess,traceback
w=Path(__file__).resolve().parent;out=w/'genuine-p512-old-main-nov10';out.mkdir(exist_ok=False);(out/'saves').mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,updated_at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n')
try:
 seal=read(w/'builder-mask-guard-seal-nov9-status.json');exe=w/'build/Releasex64/scummvm.exe';assert sha(exe)==seal['exe_sha256']
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p512=true\nastronomica_verify_p512_normal_routes=true\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_GENUINE_PRE_FIX_P512_NORMAL_ROUTES')
 with(out/'console.log').open('w')as console:p=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT,timeout=900)
 text=log.read_text(errors='replace');assert p.returncode==0 and 'FAIL'not in text and 'P512 all-normal Music/file verification: PASS'in text,text[-2500:]
 slots={}
 for number in(29,30):
  path=out/'saves'/f'astro-verify.{number:03}';data=path.read_bytes();assert data[:4]==b'ASVM' and struct.unpack_from('<2I',data,4)==(29,512)
  slots[str(number)]=dict(sha256=sha(path),bytes=len(data),version=29,scene=512)
 assert sha(exe)==seal['exe_sha256']
 receipt=dict(status='GENUINE_PRE_FIX_MAIN_P512_ASVM29_NORMAL_ROUTES_PASS',completed_at=datetime.now(timezone.utc).isoformat(),producer_exe_sha256=sha(exe),native_log_sha256=sha(log),physical_slots=slots,all12_original_natural_questions_pass=True,first_and_repeated_completion=True,actual_audio_driver='wasapi',muted=True,limits=['Exact pre-fix installed main produced these actual physical files','Declared final-question stopped boundaries with ordinary active S0; not all historical saves or every P512 boundary'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS');print('Genuine old-main P512 native ASVM29 routes and slots PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
