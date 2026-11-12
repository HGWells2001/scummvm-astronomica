"""Compare standard global-menu permission before/after;do not attempt unsafe baseline loading."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;out=w/'intro-global-menu-native-nov12';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_GLOBAL_MENU_DIAGNOSTIC_BUILDS');stages={r:w/('intro-global-menu-'+r+'-nov12-stage')for r in['baseline','candidate']}
 for role,s in stages.items():
  while not(s/'proof.json').exists():
   err=w/('intro-global-menu-'+role+'-nov12-build.err')
   if err.exists()and err.stat().st_size:raise RuntimeError(err.read_text())
   time.sleep(1)
  subprocess.run([sys.executable,str(w/('audit_intro_global_menu_'+role+'_nov12.py')),s.name,'intro-global-menu-'+role+'-source-review-nov12.json'],check=True,stdout=subprocess.DEVNULL)
 fixture=w/'verified-checkpoints/p501-025e82d8bd3b/frozen-slot26/astro-verify.026';original=sha(fixture);voice=Path('D:/astro/PLACES/P501/S302.WAV');voice_hash=sha(voice);rows=[]
 for role,expected in [('baseline',False),('candidate',True)]:
  s=stages[role];b=read(s/'proof.json');exe=s/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256'];case=out/role;case.mkdir();saves=case/'saves';saves.mkdir();alias=saves/'astro-verify.097';shutil.copyfile(fixture,alias)
  cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=true\nastronomica_verify_intro_menu=true\nastronomica_intro_menu_expected='+str(expected).lower()+'\nsavepath='+saves.as_posix()+'\n');env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=case/'native.log';state('RUNNING_GLOBAL_MENU_COMPLETE_ORIGINAL_VOICE',role=role)
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=case,env=env,stdout=console,stderr=subprocess.STDOUT)
   try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','intro-global-menu-'+role,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
   finally:code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text,text[-3500:]
  m=re.search(r'Introduction global menu: PASS \(expected([01]),paused([01]),saveBlocked([01]),loadBlocked([01]),held(\d+),audio(\d+)/(\d+),wall(\d+),cursor(-?\d+),visible([01]),pending(\d+)\)',text);assert m and bool(int(m[1]))==expected and int(m[2])==1
  assert sha(fixture)==sha(alias)==original and sha(voice)==voice_hash and set(p.name for p in saves.iterdir())=={'astro-verify.097'}
  rows.append(dict(role=role,global_menu_paused=True,load_blocked_during_intro=bool(int(m[4])),save_blocked_during_intro=bool(int(m[3])),held_millis=int(m[5]),audio_millis_at_pause=int(m[6]),audio_millis_at_escape=int(m[7]),cursor_during_intro=int(m[9]),voice_completed_naturally=True,valid_native_slot_present_but_not_loaded=True,fixture_sha256=original,native_log_sha256=sha(log),native_exited_naturally=True))
 assert rows[0]['load_blocked_during_intro']is False and rows[1]['load_blocked_during_intro']is True
 prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='INTRO_GLOBAL_MENU_REENTRANT_LOAD_GUARD_CAUSAL_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=read(w/'intro-menu-candidate-nov12c-stage/proof.json')['candidate_exe_sha256'],candidate_diagnostic_exe_sha256=sha(stages['candidate']/'bin/scummvm.exe'),baseline_diagnostic_exe_sha256=sha(stages['baseline']/'bin/scummvm.exe'),cases=rows,all_processes_exited_naturally=True,user_preferences_unchanged=True,limits=['Standard EVENT_MAINMENUhandled by actual core event manager,corresponding to global CtrlF5/controller menu;not an engine-only F5shortcut','Valid physical earlier engine ASVM27slot present;unsafe baseline permission observed but no load selected and no file changed','Baseline global menu already pauses audio,but permits reentrant loading and retains previous exit arrow;candidate gates loading/saving and resets cursor','Observer-only diagnostic variants,not installed;both original voices run to natural end;no human/global completion claim'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print(proof['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
