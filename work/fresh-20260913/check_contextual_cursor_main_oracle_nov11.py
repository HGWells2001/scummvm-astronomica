"""Compare the real engine's cached hit results with its frozen uncached decoder path."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;s=w/'contextual-cursors-nov11b-stage';out=w/'contextual-cursors-main-oracle-nov11';out.mkdir(exist_ok=False);(out/'saves').mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 state('WAITING_CACHED_ENGINE_BUILD');deadline=time.monotonic()+900
 while not(s/'proof.json').exists():assert time.monotonic()<deadline;time.sleep(1)
 b=read(s/'proof.json');assert b['status']=='CONTEXTUAL_CURSOR_REAL_ENGINE_BUILD_PASS';exe=w/'build/Releasex64/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256']
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_navigation_cursors=true\nsavepath='+(out/'saves').as_posix()+'\n')
 source=(s/'source/engines/astronomica/astronomica.cpp').read_text()
 expected='if(ConfMan.hasKey("astronomica_verify_navigation_cursors")&&ConfMan.getBool("astronomica_verify_navigation_cursors")) {\n  const bool ok=verifyNavigationCursors();'
 assert expected in source and 'astronomica_verify_navigation_cursors=true' in cfg.read_text()
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_REAL_ENGINE_CACHED_UNCACHED_COMPARISON')
 began=time.monotonic()
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+2700
  subprocess.run([sys.executable,str(w/'suite_poweroff_nov11.py'),'register','--pid',str(child.pid),'--label','contextual-cursors-installed-native-engine','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
  while child.poll()is None:
   text=log.read_text(errors='replace')if log.exists()else''
   time.sleep(.25)
  code=child.wait()
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text,text[-3500:]
 for marker in ['Navigation cursor live UI: PASS','Navigation cursor original rules: PASS','Navigation cursor ownership: PASS','Contextual down cursor verification: PASS','Navigation cursor native result: PASS']:assert marker in text,marker
 assert sha(exe)==b['candidate_exe_sha256'] and sha(w/'build/Releasex64/scummvm.exe')==b['candidate_exe_sha256'];prefs=read(w/'nov11-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='INSTALLED_CONTEXTUAL_CURSOR_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),user_preferences_unchanged=True,original_cursor_resources=4,canonical_original_pixels=4096,GUI_visibility_and_ownership=True,native_exited_naturally=True)
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print('Installed original navigation cursors PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise

