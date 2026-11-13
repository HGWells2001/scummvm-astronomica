"""Run the isolated P512 diagnostic and preserve a natural failure as evidence,not a release pass."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;stage=w/'blocking-voice-p512-clock-nov13-stage';out=w/'blocking-voice-p512-clock-native-nov13';out.mkdir(exist_ok=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_DIAGNOSTIC_BUILD')
 while not(stage/'proof.json').exists():
  error=w/'blocking-voice-p512-clock-nov13-build.err'
  if error.exists()and error.stat().st_size:raise RuntimeError(error.read_text())
  time.sleep(1)
 subprocess.run([sys.executable,str(w/'audit_blocking_voice_p512_clock_nov13.py'),stage.name,'blocking-voice-p512-clock-source-review-nov13.json'],check=True)
 saves=out/'saves';saves.mkdir();fixtures={}
 for suffix in ['098','099']:
  source=w/'opening-rgb-general-nov6/slots'/('astro-verify.'+suffix);fixtures[source.name]=sha(source);shutil.copyfile(source,saves/source.name)
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=false\nastronomica_animation=false\nastronomica_sprite_input=false\nastronomica_entry_scripts=false\nastronomica_verify_p512=true\nastronomica_p512_under_end_clock=true\nsavepath='+saves.as_posix()+'\n')
 exe=stage/'bin/scummvm.exe';pin=sha(exe);env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_ISOLATED_P512_MEMORY_DIAGNOSTIC')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
  try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','p512-memory-refusal-isolated-engine','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
  finally:code=child.wait()
 text=log.read_text(errors='replace');assert code==0 and 'P512 isolated diagnostic result:'in text and 'Log closed successfully'in text,text[-3000:]
 assert sha(exe)==pin and fixtures=={name:sha(saves/name)for name in fixtures};prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 passed='P512 isolated diagnostic result: PASS'in text
 receipt=dict(status='P512_ISOLATED_MEMORY_DIAGNOSTIC_PASS'if passed else'P512_ISOLATED_MEMORY_REFUSAL_REPRODUCED',completed_at=datetime.now(timezone.utc).isoformat(),diagnostic_exe_sha256=pin,shipping_candidate_exe_sha256=read(stage/'proof.json')['base_exe_sha256'],native_log_sha256=sha(log),detail_lines=[line for line in text.splitlines()if 'P512 memory refusal detail'in line or 'P512 isolated diagnostic result'in line],native_exited_naturally=True,user_preferences_unchanged=True,fixtures_unchanged=fixtures,production_installed=False,release_gate_satisfied=False,limits=['Additional isolated observation;cannot replace failed full general on exact candidate','No checks weakened;new diagnostic reports failure and returns normally instead of entering debugger','Original stalled general/native38244left untouched;no process termination or computer shutdown'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state(receipt['status']);print(receipt['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
