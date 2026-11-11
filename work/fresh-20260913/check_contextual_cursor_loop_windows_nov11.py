"""Observe actual player-loop mouse/key/menu/file tests until natural native exit."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,struct,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;stage=w/'contextual-cursor-loop-nov11b-stage';out=w/'contextual-cursor-loop-windows-native-nov11';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_ACTUAL_PLAYER_LOOP_DIAGNOSTIC_BUILD')
 while not(stage/'proof.json').exists():
  error=w/'contextual-cursor-loop-nov11b.err'
  if error.exists()and error.stat().st_size:raise RuntimeError(error.read_text())
  time.sleep(1)
 prior=read(w/'contextual-cursor-loop-source-review-nov11b.json');assert prior['status'].endswith('PASS') and prior['candidate_exe_sha256']==sha(stage/'bin/scummvm.exe')
 from contextual_cursor_loop_source_nov11b import SETUP,OBSERVER
 shipping=w/'contextual-cursors-nov11b-stage';ship=read(shipping/'proof.json');build=read(stage/'proof.json');cpp=(shipping/'source/engines/astronomica/astronomica.cpp').read_text();anchor='  // Cursor movement must be presented even when no scene pixels changed.\n  _system->updateScreen();\n  _system->delayMillis(10);'
 expected=cpp.replace(' while (!shouldQuit()) {',SETUP+'\n while (!shouldQuit()) {').replace(anchor,anchor.replace('  _system->delayMillis(10);',OBSERVER+'\n  _system->delayMillis(10);'))
 assert(stage/'source/engines/astronomica/astronomica.cpp').read_text()==expected
 for n,h in ship['candidate_engine_sha256'].items():
  if n!='astronomica.cpp':assert sha(stage/'source/engines/astronomica'/n)==h
 exe=stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256'];env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='windows',SDL_AUDIODRIVER='wasapi');rows=[]
 cases=[('new-room-only',None,None,None,'en','true'),('old-v27-p501','p501-025e82d8bd3b',26,501,'C','true'),('old-v26-p504','p504-2a305b134662',25,504,'en','false')]
 for label,frozen,slot,scene,locale,scale in cases:
  case=out/label;case.mkdir();saves=case/'saves';saves.mkdir();old=None
  if frozen:
   folder=w/'verified-checkpoints'/frozen;origin=read(folder/f'frozen-slot{slot}.json');source=folder/f'frozen-slot{slot}'/f'astro-verify.{slot:03}';assert sha(folder/'scummvm.exe')==origin['producing_exe_sha256']and sha(source)==origin['slot_sha256'];raw=source.read_bytes();assert raw[:4]==b'ASVM'and struct.unpack_from('<I',raw,8)[0]==scene
   shutil.copyfile(source,saves/'astro-verify.097');old=dict(source_file=str(source),version=struct.unpack_from('<I',raw,4)[0],scene=scene,slot_sha256=sha(source),producing_exe_sha256=origin['producing_exe_sha256'],origin_receipt_sha256=sha(folder/f'frozen-slot{slot}.json'))
  extra='astronomica_navcursor_old_slot=97\nastronomica_navcursor_old_scene='+str(scene)+'\n'if old else''
  cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language='+locale+'\ngui_theme=builtin\ngui_disable_fixed_font_scaling='+scale+'\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_navigation_cursor_loop=true\n'+extra+'savepath='+saves.as_posix()+'\n');log=case/'native.log'
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
   subprocess.run([sys.executable,str(w/'suite_poweroff_nov11.py'),'register','--pid',str(child.pid),'--label','navigation-cursor-real-loop-'+label,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
   state('RUNNING_ACTUAL_PLAYER_EVENT_LOOP',profile=label,native_pid=child.pid);code=child.wait()
  text=log.read_text(errors='replace');assert 'Using SDL Video Driver "windows"'in text;assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text and 'Navigation cursor player loop: PASS'in text,text[-5000:]
  frames=re.findall(r'Navigation cursor player frame: PASS \(phase(\d+),P(\d+),cursor(-?\d+),visible1\)',text);assert len(frames)==(17 if old else 16)and[int(x[0])for x in frames]==list(range(len(frames)))
  new_file=saves/'astro-verify.060';data=new_file.read_bytes();assert data[:4]==b'ASVM'and struct.unpack_from('<II',data,4)==(2,103)
  if old:assert sha(Path(old['source_file']))==sha(saves/'astro-verify.097')==old['slot_sha256']
  rows.append(dict(profile=label,frames=frames,checked_phases=len(frames),deferred_wait_frames=text.count("Contextual cursor deferred frame: WAIT"),actual_observed_loop_iterations=len(frames)+text.count("Contextual cursor deferred frame: WAIT"),video_driver="windows",new_physical_save_version=2,new_room_save_sha256=sha(new_file),original_ne_cursor_owners_retained=True,old_fixture=old,native_log_sha256=sha(log),exited_naturally=True))
 prefs=read(w/'nov11-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='ORIGINAL_CONTEXTUAL_CURSOR_WINDOWS_EVENT_LOOP_AND_PHYSICAL_SAVES_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=ship['candidate_exe_sha256'],diagnostic_exe_sha256=sha(exe),shipping_source_recovered_exactly_after_removing_observers=True,all_other22engine_files_identical=True,diagnostic_source_review_sha256=sha(w/'contextual-cursor-loop-source-review-nov11b.json'),cases=rows,all_processes_exited_naturally=True,user_preferences_unchanged=True,limits=['Actual SDLWindows backend,not SDLdummy. Frame rows describe checked phases;deferred wait frames counted separately','Actual production pollEvent/main loop/per-frame cursor update/raw mouse exit/raw keyboard exit/actual F5dialog','Three new physical ordinary ASVM2room roundtrips,two frozen earlier accepted-engine ASVM26/27file loads;historical full futures not claimed here','Controlled scene setup and synthetic input events;no human full-game physical pointer/audio validation','Diagnostic observers are not installed;no original Windows executable run'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print(proof['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
