"""Timed same-thread key source observes actual menu/audio pause during complete original voice."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;out=w/'space-pause-native-nov12';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_SPACE_PAUSE_REAL_ENGINE_BUILDS');stages={role:w/('space-pause-'+role+'-nov12-stage')for role in ['baseline','candidate']}
 for role,s in stages.items():
  while not(s/'proof.json').exists():
   err=w/('space-pause-'+role+'-nov12-build.err')
   if err.exists()and err.stat().st_size:raise RuntimeError(err.read_text())
   time.sleep(1)
  subprocess.run([sys.executable,str(w/('audit_space_pause_'+role+'_nov12.py')),s.name,'space-pause-'+role+'-source-review-nov12.json'],check=True,stdout=subprocess.DEVNULL)
 resources={n:sha(Path('D:/astro')/n)for n in ['PLACES/P501/MEGAFILE.HYP','PLACES/P501/S302.WAV','PLACES/P27/MEGAFILE.HYP','PLACES/P103/MEGAFILE.HYP']};rows=[]
 for label,role,expected,video in [('baseline-unhandled-space','baseline',False,'dummy'),('paused-original-voice','candidate',True,'dummy'),('paused-original-voice-windows','candidate',True,'windows')]:
  stage=stages[role];b=read(stage/'proof.json');exe=stage/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256'];case=out/label;case.mkdir();(case/'saves').mkdir();cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\nfullscreen=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=true\nastronomica_verify_space_pause=true\nastronomica_space_pause_expected='+str(expected).lower()+'\nsavepath='+(case/'saves').as_posix()+'\n')
  env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER=video,SDL_AUDIODRIVER='wasapi');log=case/'native.log';state('RUNNING_COMPLETE_ORIGINAL_INTRODUCTION',profile=label)
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=case,env=env,stdout=console,stderr=subprocess.STDOUT)
   subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','intro-menu-native-'+label,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text,text[-4000:]
  m=re.search(r'Space spoken pause: PASS \(expected([01]),paused([01]),saveBlocked([01]),loadBlocked([01]),held(\d+),audio(\d+)/(\d+),wall(\d+),cursor(-?\d+),visible([01]),pending(\d+)\)',text);assert m and bool(int(m[1]))==expected
  assert 'Space pause native result: PASS'in text
  rooms=re.findall(r'Space room pause: PASS \(P(103|27),expected([01]),paused([01]),held(\d+),clock(\d+),modifiers1,stable1\)',text);assert len(rooms)==2 and all(bool(int(x[1]))==expected for x in rooms)
  rows.append(dict(room_checks=rooms,profile=label,role=role,video_driver=video,expected_menu=expected,saw_actual_engine_pause=bool(int(m[2])),save_blocked_during_intro=bool(int(m[3])),load_blocked_during_intro=bool(int(m[4])),paused_millis=int(m[5]),audio_millis_at_pause=int(m[6]),audio_millis_at_escape=int(m[7]),wall_millis=int(m[8]),cursor_during_intro=int(m[9]),cursor_visible=bool(int(m[10])),original_pending_after_intro=int(m[11]),native_log_sha256=sha(log),native_exited_naturally=True))
  assert not list((case/'saves').iterdir())
 assert resources=={n:sha(Path('D:/astro')/n)for n in resources};prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 j=dict(status='SPACE_PAUSE_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(stages['candidate']/'bin/scummvm.exe'),baseline_diagnostic_exe_sha256=sha(stages['baseline']/'bin/scummvm.exe'),cases=rows,original_resources_sha256=resources,user_preferences_unchanged=True,all_processes_exited_naturally=True,limits=['Actual EventSource/native F5menu,real Engine/mixer pause and complete original P501S302playback,including Windows backend;mute is enabled','Space resumes the real pause dialog after300ms;complete original voice ends naturally','Save/load deliberately unavailable until introduction ends to prevent reentrant scene restoration/startup replay;derived UIflag is not serialized','Not a human audiovisual playthrough or global completion claim'])
 (out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');state('PASS');print(j['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
