"""Verify the installed launch-path binary on an isolated genuine ASVM31 save."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,time,traceback
w=Path(__file__).resolve().parent;r=w.parents[1];out=w/'opening-rgb-main-smoke-nov6';out.mkdir(exist_ok=False)
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 integration=read(w/'opening-rgb-integration-nov6-status.json');snap=Path(integration['snapshot']);exe=w/'build/Releasex64/scummvm.exe';pin=d(exe);assert pin==integration['candidate_exe_sha256']
 slots=out/'slots';slots.mkdir();inputs={}
 for suffix in ('','.expected'):
  name='astro-verify.041'+suffix;shutil.copyfile(snap/'physical-slots'/name,slots/name);inputs[name]=d(slots/name)
 user=r/'userdata/astronomica/astronomica.ini';before=d(user)
 cfg=out/'smoke.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=C\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=true\nastronomica_verify_p523_fresh_physical=true\nsavepath='+slots.as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_INSTALLED_BINARY_SMOKE')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(slots),'--logfile='+str(log),'--debuglevel=1','--save-slot=41','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
  try:
   deadline=time.monotonic()+100
   while child.poll()is None:
    text=log.read_text(errors='replace')if log.exists()else''
    if 'FAIL'in text or time.monotonic()>deadline:child.terminate();break
    time.sleep(.5)
   code=child.wait(timeout=15)
  finally:
   if child.poll()is None:child.terminate();child.wait(timeout=15)
 (out/'native-exit.json').write_text(json.dumps(dict(exit_code=code,pid=child.pid))+'\n')
 text=log.read_text();assert code==0 and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.')
 assert text.count('P523 ASVM31 fresh process: PASS')==1 and '3natural callbacks,P117 unsolved'in text and 'Using SDL Audio Driver "wasapi"'in text
 assert d(exe)==pin and d(user)==before
 for name,expected in inputs.items():assert d(slots/name)==expected
 proof=dict(status='P523_INSTALLED_ASVM31_NATIVE_SMOKE_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,log_sha256=d(log),config_sha256=d(cfg),integration_sha256=d(w/'opening-rgb-integration-nov6-status.json'),genuine_slot=41,natural_callbacks=[13,1,3],destination=117,full_state_pixels_and_clock=True,source_files_unchanged=True,user_profile_unchanged=True,main_publication_pending=True)
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'));print('Installed ASVM31 launch-path native smoke PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
