"""Compare real original P517 controls through separate native input polls."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;out=w/'double-click-native-nov12';out.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_TWO_FRESH_BUILDS')
 for role in ['candidate','baseline']:
  stage=w/('double-click-'+role+'-nov12-stage')
  while not(stage/'proof.json').exists():time.sleep(1)
  subprocess.run([sys.executable,str(w/('audit_double_click_'+role+'_nov12.py')),stage.name,'double-click-'+role+'-source-review-nov12.json'],check=True)
 rows=[];state('RUNNING_REAL_POLL_LOOP')
 for name,role,video,kind in [('baseline','baseline','dummy','double'),('candidate','candidate','dummy','double'),('candidate-windows','candidate','windows','double'),('candidate-backlog','candidate','dummy','backlog')]:
  folder=out/name;folder.mkdir();saves=folder/'saves';saves.mkdir();stage=w/('double-click-'+role+'-nov12-stage');exe=stage/'bin/scummvm.exe';build=read(stage/'proof.json');pin=sha(exe);assert pin==build['candidate_exe_sha256']
  cfg=folder/'test.ini';flag='astronomica_verify_double_click=true\nastronomica_double_click_expected='+('false'if role=='baseline'else'true')+'\n'if kind=='double'else'astronomica_verify_input_backlog=true\nastronomica_input_backlog_expected=true\n'
  cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\n'+flag+'savepath='+saves.as_posix()+'\n')
  env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER=video,SDL_AUDIODRIVER='wasapi');log=folder/'native.log'
  with(folder/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=folder,env=env,stdout=console,stderr=subprocess.STDOUT)
   try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','double-click-native-'+name,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
   finally:code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text,text[-3000:]
  if kind=='double':
   marker='Double click native result: PASS (expected0,cases6,differences6,tripleMatches0,delayed1,separate1)'if role=='baseline'else'Double click native result: PASS (expected1,cases6,differences0,tripleMatches6,delayed1,separate1)'
   assert marker in text,text[-3000:]
  else:assert 'Click backlog native result: PASS (expected1,cases12,differences0)'in text and 'Click backlog host controls: PASS (keyboard1,menu1,quit1)'in text,text[-3000:]
  assert sha(exe)==pin and not list(saves.iterdir());rows.append(dict(name=name,role=role,video=video,kind=kind,exe_sha256=pin,log_sha256=sha(log),native_exited_naturally=True))
 prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 result=dict(status='DOUBLE_CLICK_REAL_POLLS_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=read(w/'double-click-candidate-nov12-stage/proof.json')['candidate_exe_sha256'],cases=rows,baseline_double_actions_reproduced=6,candidate_pairs_match_first_only=6,candidate_third_click_is_new=6,delayed_and_separate_clicks_preserved=True,accepted_backlog_and_host_controls_preserved=True,all_processes_exited_naturally=True,user_preferences_unchanged=True,limits=['Actual P517 original scripts,100globals and two original locals/gauge positions;finite six pairs per double-click profile','Configured isolated double-click interval and portable virtual-pixel tolerance;not identical arbitrary host rectangle settings','No original Windows runtime or whole-game completion claim'])
 (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');state('PASS');print(result['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
