from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;out=w/'double-pair-batches-native-nov12';out.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_DIAGNOSTIC_BUILD');stage=w/'double-pair-batches-nov12-stage'
 while not(stage/'proof.json').exists():time.sleep(1)
 subprocess.run([sys.executable,str(w/'audit_double_pair_batches_nov12.py'),stage.name,'double-pair-batches-source-review-nov12.json'],check=True)
 exe=stage/'bin/scummvm.exe';pin=sha(exe);rows=[];state('RUNNING_NATIVE_MIXED_BATCHES')
 for video in ['dummy','windows']:
  folder=out/video;folder.mkdir();saves=folder/'saves';saves.mkdir();cfg=folder/'test.ini';log=folder/'native.log'
  cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_double_pair_batches=true\nsavepath='+saves.as_posix()+'\n')
  env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER=video,SDL_AUDIODRIVER='wasapi')
  with(folder/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=folder,env=env,stdout=console,stderr=subprocess.STDOUT)
   try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','double-pair-batches-'+video,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
   finally:code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Double pair batch result: PASS (cases4)'in text and 'Log closed successfully'in text,text[-3000:]
  rows.append(dict(video=video,cases=4,log_sha256=sha(log),native_exited_naturally=True));assert not list(saves.iterdir())
 assert sha(exe)==pin
 prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 j=dict(status='DOUBLE_PAIR_BATCHES_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),shipping_candidate_exe_sha256=read(w/'double-click-candidate-nov12-stage/proof.json')['candidate_exe_sha256'],diagnostic_exe_sha256=pin,profiles=rows,exact_original_controls=True,third_click_after_ignored_second_admitted=True,discarded_presses_update_pairing=True,configured_and_zero_fallback_intervals=True,user_preferences_unchanged=True,all_processes_exited_naturally=True,limits=['Four finite actual poll sequences per profile,original P517 controls/locals;not all physical hardware timings','Optional observer only;production source and installed main unchanged'])
 (out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');state('PASS');print(j['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
