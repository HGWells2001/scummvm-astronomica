"""Observe native file compatibility with fresh target settings,without cancelling processes."""
from pathlib import Path
from datetime import datetime,timezone
import configparser,hashlib,json,os,re,shutil,struct,subprocess,sys,time,traceback
from intro_physical_save_source_nov12 import PROBE
w=Path(__file__).resolve().parent;stage=w/'click-backlog-physical-saves-nov12-stage';out=w/'click-backlog-physical-saves-native-nov12';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_AUDITED_SHIPPING_CANDIDATE')
 while not(stage/'proof.json').exists():
  err=w/'click-backlog-physical-saves-nov12-build.err'
  if err.exists()and err.stat().st_size:raise RuntimeError(err.read_text())
  time.sleep(1)
 subprocess.run([sys.executable,str(w/'audit_click_backlog_physical_saves_nov12.py'),stage.name,'click-backlog-physical-saves-source-review-nov12.json'],check=True,stdout=subprocess.DEVNULL)
 base=w/'click-backlog-candidate-nov12b-stage';shipping=read(base/'proof.json');build=read(stage/'proof.json');assert build['base_exe_sha256']==shipping['candidate_exe_sha256']
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }';assert(stage/'source/engines/astronomica/astronomica.cpp').read_text().replace(anchor+'\n'+PROBE,anchor)==(base/'source/engines/astronomica/astronomica.cpp').read_text()
 for name,h in shipping['candidate_engine_sha256'].items():
  if name!='astronomica.cpp':assert sha(stage/'source/engines/astronomica'/name)==h
 exe=stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256'];rows=[]
 fixtures=[('room-v2',w/'verified-checkpoints/windows-cursor-loop-523b2d1f0816/native/new-room-only/saves/astro-verify.060',103,2,'dummy'),('p501-v27',w/'verified-checkpoints/p501-025e82d8bd3b/frozen-slot26/astro-verify.026',501,27,'dummy'),('p504-v26',w/'verified-checkpoints/p504-2a305b134662/frozen-slot25/astro-verify.025',504,26,'dummy'),('p501-windows',w/'verified-checkpoints/p501-025e82d8bd3b/frozen-slot26/astro-verify.026',501,27,'windows')]
 for label,source,scene,version,video in fixtures:
  voice=Path('D:/astro/PLACES/P501/S302.WAV');voice_hash=sha(voice)
  raw=source.read_bytes();original=sha(source);assert raw[:4]==b'ASVM'and struct.unpack_from('<II',raw,4)==(version,scene)
  case=out/label;case.mkdir();saves=case/'saves';saves.mkdir();alias=saves/'astro-verify.097';shutil.copyfile(source,alias);cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\nfullscreen=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_default_save_load=true\nastronomica_default_save_slot=97\nastronomica_default_save_scene='+str(scene)+'\nsavepath='+saves.as_posix()+'\n');initial_cfg=sha(cfg)
  env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER=video,SDL_AUDIODRIVER='wasapi');log=case/'native.log';state('RUNNING_FRESH_CONFIG_PHYSICAL_SAVE',profile=label)
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
   subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','space-physical-save-'+label,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Fresh default physical save: PASS'in text and 'Fresh physical after original introduction: PASS'in text and 'Log closed successfully'in text,text[-4000:]
  fresh=saves/'astro-verify.060';assert fresh.read_bytes()[:4]==b'ASVM' and struct.unpack_from('<II',fresh.read_bytes(),4)==(version,scene)
  assert sha(source)==sha(alias)==original and sha(voice)==voice_hash
  parsed=configparser.ConfigParser(interpolation=None);parsed.read(cfg)
  for domain in ['scummvm','astro-verify']:
   for key in ['astronomica_audio','astronomica_animation','astronomica_sprite_input','astronomica_entry_scripts']:assert not parsed.has_option(domain,key)
  rows.append(dict(profile=label,scene=scene,version=version,source_slot_sha256=original,new_slot_sha256=sha(fresh),video_driver=video,all_four_options_absent=True,introduction_completed_before_old_load=True,intro_voice_sha256=voice_hash,all100_globals_and_completion_roundtrip=True,native_log_sha256=sha(log),native_exited_naturally=True))
 prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='CLICK_BACKLOG_PHYSICAL_NATIVE_SAVE_ROUNDTRIPS_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=shipping['candidate_exe_sha256'],diagnostic_exe_sha256=sha(exe),shipping_source_recovered_exactly=True,all_other22engine_files_and_header_identical=True,cases=rows,user_preferences_unchanged=True,all_processes_exited_naturally=True,limits=['Physical earlier accepted-engine ASVM2/26/27loads,resaves and reloads with all four feature keys absent;not original Windows saves','Compares scene,all100globals and completion count;not all historical full futures or human playthrough','Optional diagnostic only;not installed. Original source files and fixture aliases unchanged'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print(proof['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
