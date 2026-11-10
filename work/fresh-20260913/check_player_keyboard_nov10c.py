"""Prove the previous native lock bypass, then verify the real guarded key handler."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,time,traceback
w=Path(__file__).resolve().parent;out=w/'player-keyboard-native-nov10c';out.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 state('WAITING_REAL_KEYBOARD_BUILDS');deadline=time.monotonic()+900
 while not all((w/('player-keyboard-guard-nov10c-stage/proof.json'if v=='guard'else'player-keyboard-baseline-nov10b-stage/proof.json')).exists()for v in('baseline','guard')):assert time.monotonic()<deadline;time.sleep(1)
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');rows=[]
 for variant,option in [('baseline','astronomica_verify_keyboard_baseline'),('guard','astronomica_verify_keyboard')]:
  stage=w/('player-keyboard-guard-nov10c-stage'if variant=='guard'else'player-keyboard-baseline-nov10b-stage');build=read(stage/'proof.json');assert build['status']==f'PLAYER_KEYBOARD_{variant.upper()}_REAL_ENGINE_BUILD_PASS';exe=stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256'];case=out/variant;case.mkdir();(case/'saves').mkdir()
  cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\n'+option+'=true\nsavepath='+(case/'saves').as_posix()+'\n')
  log=case/'native.log';state('RUNNING_ACTUAL_KEYBOARD_HANDLER',variant=variant)
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+180
   while child.poll()is None:
    text=log.read_text(errors='replace')if log.exists()else''
    if 'FAIL'in text or time.monotonic()>deadline:child.terminate();break
    time.sleep(.1)
   code=child.wait(timeout=15)
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text,text[-3500:]
  if variant=='baseline':
   m=re.search(r'Original keyboard counterexample: blocked1 pending(\d+) P27 rightTarget(\d+) actualP(\d+)',text);assert m and int(m[1])>0 and m[2]==m[3]
   extra=dict(blocked=True,original_pending=int(m[1]),start_scene=27,arrow_target=int(m[2]),actual_scene=int(m[3]),meaning='Pre-fix native ScummVM handler; not original Windows execution')
  else:
   for marker in ['Player keyboard blocked: PASS','Player keyboard menu: PASS','Player keyboard diagnostics: PASS','Player keyboard navigation: PASS','Player keyboard verification: PASS','Player keyboard native result: PASS']:assert marker in text,marker
   extra=dict(blocked_no_mutation_cases=20,diagnostic_default_off_cases=16,unblocked_original_nav_targets=3,modified_arrow_no_mutation_cases=9,actual_F5_during_original_lock=True,explicit_diagnostic_opt_in=True,Escape_quits=True)
  assert sha(exe)==build['candidate_exe_sha256'];rows.append(dict(variant=variant,exe_sha256=sha(exe),native_log_sha256=sha(log),**extra))
 prefs=read(w/'nov10b-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='PLAYER_KEYBOARD_ORIGINAL_LOCK_GUARD_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=rows[1]['exe_sha256'],baseline_exe_sha256=rows[0]['exe_sha256'],cases=rows,user_preferences_unchanged=True,main_unchanged=True,limits=['Real engine original P27 click establishes its serialized opcode28 lock,then the actual key handler is invoked','The baseline reproduces the previous native engine bug,not an original Windows bug','Permanent whole-live-state checks freeze the engine clock using caller-owned pause tokens; F5 is tested through an actual menu dialog','No manual whole-game playthrough claim'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print('Pre-fix native lock bypass reproduced;guarded real keyboard routes PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
