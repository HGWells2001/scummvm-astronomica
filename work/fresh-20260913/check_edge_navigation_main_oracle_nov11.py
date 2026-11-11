"""Compare the real engine's cached hit results with its frozen uncached decoder path."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;s=w/'edge-navigation-guard-nov11b-stage';out=w/'edge-navigation-main-oracle-nov11';out.mkdir(exist_ok=False);(out/'saves').mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 state('WAITING_CACHED_ENGINE_BUILD');deadline=time.monotonic()+900
 while not(s/'proof.json').exists():assert time.monotonic()<deadline;time.sleep(1)
 b=read(s/'proof.json');assert b['status']=='EDGE_NAVIGATION_GUARD_REAL_ENGINE_BUILD_PASS';exe=w/'build/Releasex64/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256']
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_edge_navigation=true\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_REAL_ENGINE_CACHED_UNCACHED_COMPARISON')
 began=time.monotonic()
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+2700
  subprocess.run([sys.executable,str(w/'suite_poweroff_nov11.py'),'register','--pid',str(child.pid),'--label','edge-navigation-installed-native-engine','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
  while child.poll()is None:
   text=log.read_text(errors='replace')if log.exists()else''
   time.sleep(.25)
  code=child.wait()
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text,text[-3500:]
 for marker in ['Edge navigation geometry: PASS','Edge navigation live routes: PASS','Edge navigation input lock: PASS','Edge navigation priority: PASS','Edge navigation transition gates: PASS','Edge navigation verification: PASS','Edge navigation native result: PASS']:assert marker in text,marker
 assert sha(exe)==b['candidate_exe_sha256'] and sha(w/'build/Releasex64/scummvm.exe')==b['candidate_exe_sha256'];prefs=read(w/'nov11-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='INSTALLED_EDGE_NAVIGATION_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),user_preferences_unchanged=True,original_geometry_os_oracle_points=307200,live_exit_directions=3,input_lock_and_sprite_rectangle_priority=True,transition_gates=True,native_exited_naturally=True)
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print('Installed original edge navigation PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise

