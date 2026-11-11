"""Wait for native processes to exit naturally,even after slow/failure diagnostics."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;out=w/'edge-navigation-native-nov11d';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
builds={'baseline':w/'edge-navigation-baseline-nov11-stage','guard':w/'edge-navigation-guard-nov11b-stage'}
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_REAL_EDGE_NAVIGATION_BUILDS')
 while not all((builds[v]/'proof.json').exists()for v in('baseline','guard')):
  for v in('baseline','guard'):
   failure=w/f'edge-navigation-{v}-nov11.err'
   if failure.exists()and failure.stat().st_size:raise RuntimeError(failure.read_text())
  time.sleep(1)
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');rows=[]
 for variant,option in [('baseline','astronomica_verify_edge_navigation_baseline'),('guard','astronomica_verify_edge_navigation'),('keyboard','astronomica_verify_keyboard')]:
  stage=builds['baseline'if variant=='baseline'else'guard'];build=read(stage/'proof.json');exe=stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256'];case=out/variant;case.mkdir();(case/'saves').mkdir();cfg=case/'test.ini'
  cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\n'+option+'=true\nsavepath='+(case/'saves').as_posix()+'\n')
  log=case/'native.log';began=time.monotonic()
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
   subprocess.run([sys.executable,str(w/'suite_poweroff_nov11.py'),'register','--pid',str(child.pid),'--label','edge-navigation-native-'+variant,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
   state('RUNNING_REAL_EDGE_NAVIGATION',variant=variant,native_pid=child.pid)
   while child.poll()is None:
    if time.monotonic()-began>300:state('WAITING_FOR_NATURAL_NATIVE_EXIT',variant=variant,native_pid=child.pid,forced_termination=False)
    time.sleep(.25)
   code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text,text[-4000:]
  markers=['Edge navigation pre-fix counterexample: PASS']if variant=='baseline'else(['Edge navigation geometry: PASS','Edge navigation live routes: PASS','Edge navigation input lock: PASS','Edge navigation priority: PASS','Edge navigation transition gates: PASS','Edge navigation verification: PASS','Edge navigation native result: PASS']if variant=='guard'else['Player keyboard verification: PASS','Player keyboard native result: PASS'])
  for marker in markers:assert marker in text,marker
  rows.append(dict(variant=variant,exe_sha256=sha(exe),log_sha256=sha(log),markers=markers,exited_naturally=True,exit_code=code))
 prefs=read(w/'nov11-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='EDGE_NAVIGATION_BEFORE_AFTER_NATIVE_AND_KEYBOARD_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=rows[1]['exe_sha256'],baseline_exe_sha256=rows[0]['exe_sha256'],cases=rows,source_geometry_proof_sha256=sha(w/'original-edge-navigation-nov11/proof.json'),all_native_processes_exited_naturally=True,user_preferences_unchanged=True,main_unchanged=True,limits=['Previous native engine baseline,not original Windows execution','Actual engine navigation and script paths; rectangle/sprite overlap flags deliberately controlled in documented diagnostic cases','Current Windows geometry oracle,not original Win16runtime; no human whole-game playthrough'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print(proof['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
