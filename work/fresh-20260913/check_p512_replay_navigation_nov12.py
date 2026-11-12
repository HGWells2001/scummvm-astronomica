"""Compare actual stock keymap direction events over all original mode1 navigation routes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;out=w/'p512-replay-navigation-native-nov12';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,updated_at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n')
try:
 state('WAITING_REAL_ENGINE_BUILDS');stages={'baseline':w/'mapped-navigation-baseline-nov12b-stage','candidate':w/'p512-segment-replay-nov12-stage'}
 for role,stage in stages.items():
  while not(stage/'proof.json').exists():
   error=w/('mapped-navigation-'+role+'-nov12b-build.err')
   if error.exists()and error.stat().st_size:raise RuntimeError(error.read_text())
   time.sleep(1)
  if role=='candidate':subprocess.run([sys.executable,str(w/'audit_p512_segment_replay_nov12.py'),stage.name,'p512-segment-replay-source-review-nov12.json'],check=True)
  else:
   audit=read(w/'mapped-navigation-baseline-source-review-nov12b.json');build=read(stage/'proof.json');assert audit['candidate_exe_sha256']==build['candidate_exe_sha256']==sha(stage/'bin/scummvm.exe')
   assert audit['engine_sha256']=={n:sha(stage/'source/engines/astronomica'/n)for n in audit['engine_sha256']}
 rows=[];resources={p:sha(Path('D:/astro/PLACES')/p/'MEGAFILE.HYP')for p in ['P27','P103','P106']}
 for label,role,video in [('baseline-ignored-directions','baseline','dummy'),('candidate-directions','candidate','dummy'),('candidate-windows-directions','candidate','windows')]:
  expected=role=='candidate';case=out/label;case.mkdir();saves=case/'saves';saves.mkdir();cfg=case/'test.ini'
  cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\nfullscreen=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=false\nastronomica_animation=false\nastronomica_sprite_input=false\nastronomica_entry_scripts=false\nastronomica_verify_mapped_navigation=true\nastronomica_mapped_navigation_expected='+str(expected).lower()+'\nsavepath='+saves.as_posix()+'\n')
  env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER=video,SDL_AUDIODRIVER='wasapi');stage=stages[role];exe=stage/'bin/scummvm.exe';log=case/'native.log';before=sha(exe)
  state('RUNNING_ORIGINAL_ROUTE_MATRIX',profile=label)
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=case,env=env,stdout=console,stderr=subprocess.STDOUT)
   try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','mapped-navigation-'+label,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
   finally:code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Mapped navigation native result: PASS'in text and 'Log closed successfully'in text,text[-4500:]
  assert all('Mapped navigation '+x+': PASS'in text for x in ['default keymap','original routes','actual lock','modifiers'])
  m=re.search(r'Mapped navigation original routes: PASS \(expected([01]),scenes(\d+),routes(\d+),hash([0-9a-f]+)\)',text);assert m and bool(int(m[1]))==expected and (int(m[2]),int(m[3]))==(306,760)
  assert sha(exe)==before and not list(saves.iterdir())
  rows.append(dict(profile=label,role=role,video_driver=video,expected_direction_support=expected,original_scenes=306,original_routes=760,route_digest=m[4],stock_keymap_events_checked=True,all100_globals_match_arrow_reference=expected,actual_P27_input_lock_preserved=True,ctrl_alt_meta_ignored=True,native_exe_sha256=before,native_log_sha256=sha(log),native_exited_naturally=True))
 assert resources=={p:sha(Path('D:/astro/PLACES')/p/'MEGAFILE.HYP')for p in resources}
 prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 assert rows[1]['route_digest']==rows[2]['route_digest']
 j=dict(status='MAPPED_NAVIGATION_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(stages['candidate']/'bin/scummvm.exe'),baseline_diagnostic_exe_sha256=sha(stages['baseline']/'bin/scummvm.exe'),cases=rows,original_resource_sha256=resources,user_preferences_unchanged=True,all_processes_exited_naturally=True,limits=['Actual MetaEngine standard keymap action events and JOY direction defaults checked;no claim of physical controller hardware testing','760original NAV routes in306scenes compare mapped keypad events with existing arrow destination/all100globals;not complete game or puzzle coverage','Original P27 script input lock and modified directional keys checked;no game state or save schema changes'])
 (out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');state('PASS');print(j['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
