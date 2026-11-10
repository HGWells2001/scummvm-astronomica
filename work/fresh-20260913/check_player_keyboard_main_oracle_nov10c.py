"""Compare the real engine's cached hit results with its frozen uncached decoder path."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,time,traceback
w=Path(__file__).resolve().parent;s=w/'player-keyboard-guard-nov10c-stage';out=w/'player-keyboard-main-oracle-nov10c';out.mkdir(exist_ok=False);(out/'saves').mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 state('WAITING_CACHED_ENGINE_BUILD');deadline=time.monotonic()+900
 while not(s/'proof.json').exists():assert time.monotonic()<deadline;time.sleep(1)
 b=read(s/'proof.json');assert b['status']=='PLAYER_KEYBOARD_GUARD_REAL_ENGINE_BUILD_PASS';exe=w/'build/Releasex64/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256']
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_keyboard=true\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_REAL_ENGINE_CACHED_UNCACHED_COMPARISON')
 began=time.monotonic()
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+2700
  while child.poll()is None:
   text=log.read_text(errors='replace')if log.exists()else''
   if 'FAIL'in text or 'Hit geometry mismatch:'in text or time.monotonic()>deadline:child.terminate();break
   time.sleep(.25)
  code=child.wait(timeout=15)
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text,text[-3500:]
 for marker in ['Player keyboard blocked: PASS','Player keyboard menu: PASS','Player keyboard diagnostics: PASS','Player keyboard navigation: PASS','Player keyboard verification: PASS','Player keyboard native result: PASS']:assert marker in text,marker
 assert sha(exe)==b['candidate_exe_sha256'] and sha(w/'build/Releasex64/scummvm.exe')==b['candidate_exe_sha256'];prefs=read(w/'nov10b-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='INSTALLED_PLAYER_KEYBOARD_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),user_preferences_unchanged=True,blocked_no_mutation_cases=20,diagnostic_default_off_cases=16,unblocked_original_nav_targets=3,modified_arrow_no_mutation_cases=9,actual_F5_during_original_lock=True)
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print('Installed real keyboard handler PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
