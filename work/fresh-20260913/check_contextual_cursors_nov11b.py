"""Validate original cursor decode/UI on four GUI profiles;never terminate suites."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;stage=w/'contextual-cursors-nov11b-stage';out=w/'contextual-cursors-native-nov11b';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_ORIGINAL_CURSOR_REAL_ENGINE_BUILD')
 while not(stage/'proof.json').exists():
  error=w/'contextual-cursors-nov11b.err'
  if error.exists()and error.stat().st_size:raise RuntimeError(error.read_text())
  time.sleep(1)
 build=read(stage/'proof.json');exe=stage/'bin/scummvm.exe';assert build['status']=='CONTEXTUAL_CURSOR_REAL_ENGINE_BUILD_PASS'and sha(exe)==build['candidate_exe_sha256']
 subprocess.run([sys.executable,str(w/'audit_contextual_cursors_nov11b.py'),stage.name,'contextual-cursors-source-review-nov11b.json'],check=True,stdout=subprocess.DEVNULL)
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');rows=[]
 cases=[('cursor-'+locale+'-'+scale,'astronomica_verify_navigation_cursors',locale,scale)for locale in('en','C')for scale in('true','false')]+[('edges','astronomica_verify_edge_navigation','en','true'),('keyboard','astronomica_verify_keyboard','en','true')]
 for label,option,locale,scale in cases:
  case=out/label;case.mkdir();(case/'saves').mkdir();cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language='+locale+'\ngui_theme=builtin\ngui_disable_fixed_font_scaling='+scale+'\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\n'+option+'=true\nsavepath='+(case/'saves').as_posix()+'\n');log=case/'native.log'
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
   subprocess.run([sys.executable,str(w/'suite_poweroff_nov11.py'),'register','--pid',str(child.pid),'--label','navigation-cursor-native-'+label,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
   state('RUNNING_ORIGINAL_CURSOR_PROFILE',profile=label,native_pid=child.pid);code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text,text[-4500:]
  if option=='astronomica_verify_navigation_cursors':
   for marker in ['Contextual down cursor verification: PASS','Navigation cursor live UI: PASS','Navigation cursor original rules: PASS','Navigation cursor ownership: PASS','Navigation cursor verification: PASS','Navigation cursor native result: PASS']:assert marker in text,marker
   assert text.count('Navigation cursor resource: PASS')==4
  else:assert ('Edge navigation native result: PASS'if label=='edges'else'Player keyboard native result: PASS')in text
  rows.append(dict(profile=label,gui_language=locale,disable_fixed_font_scaling=scale,option=option,native_log_sha256=sha(log),exited_naturally=True))
 prefs=read(w/'nov11-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='ORIGINAL_CONTEXTUAL_CURSOR_DECODE_GUI_AND_INPUT_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),cases=rows,original_cursor_fact_sha256=sha(w/'original-navigation-cursors-nov11/proof.json'),original_groups_by_role=[2,1,3,4],canonical_class_hashes=['8cf023af','565522f7','11480b87','51cc9907'],native_gui_profiles=4,edge_and_keyboard_regressions=True,all_processes_exited_naturally=True,user_preferences_unchanged=True,limits=['Original cursor resource classes/hotspots verified against independent offline bit decoder','Actual CursorMan/menu calls on SDL dummy,not manual physical hardware pointer inspection','Controlled rectangle overlaps/fallback path and ownership cycles;no original Win16execution or human whole-game playthrough'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print(proof['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
