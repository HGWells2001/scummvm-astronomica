"""Replay newly serialized data from 185 preserved native captures, not old saves."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,time,traceback
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage';out=w/'opening-rgb-recipients-nov6'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
out.mkdir(exist_ok=False)
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 build=read(s/'complete-build/proof.json');exe=s/'complete-build/bin/scummvm.exe';pin=d(exe);assert pin==build['candidate_exe_sha256']
 source=w/'p523-file-nov5-stage/p523-physical-slots/astro-verify.041';source_pin=d(source)
 data=out/'source.asvm';data.write_bytes(source.read_bytes());assert d(data)==source_pin
 slots=out/'slots';slots.mkdir();cfg=out/'recipients.ini'
 cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p523_recipients=true\nastronomica_p523_source='+data.as_posix()+'\nsavepath='+slots.as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_21_ACTIVE_RECEIVER_LOADS')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(slots),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
  try:
   deadline=time.monotonic()+900
   while child.poll()is None:
    text=log.read_text(errors='replace')if log.exists()else''
    if 'FAIL'in text or time.monotonic()>deadline:child.terminate();break
    time.sleep(.5)
   code=child.wait(timeout=15)
  finally:
   if child.poll()is None:child.terminate();child.wait(timeout=15)
 (out/'native-exit.json').write_text(json.dumps(dict(exit_code=code,pid=child.pid))+'\n')
 text=log.read_text();assert code==0 and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-2500:]
 rows=re.findall(r'P523 ASVM31 recipient: PASS \(P(\d+),pause(\d+),pending(\d+),',text)
 assert [(int(p),int(m))for p,m,_ in rows]==[(p,m)for p in (1,117,519,510,512,525,523)for m in range(3)]
 assert text.count('P523 ASVM31 recipient matrix: PASS')==1 and '21 commits,42 invalid-input refusals,12 live movie fixtures'in text
 assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi'] and not list(slots.iterdir())
 assert d(exe)==pin and build['stage_sha256']=={n:d(s/n)for n in build['stage_sha256']} and d(source)==d(data)==source_pin
 proof=dict(status='P523_ASVM31_COMPLETE_CROSS_SCENE_21_RECIPIENTS_PASS',candidate_exe_sha256=pin,stage_sha256=build['stage_sha256'],log_sha256=d(log),config_sha256=d(cfg),driver_sha256=d(Path(__file__)),source_physical_sha256=source_pin,rows=rows,actual_public_load_commits=21,atomic_invalid_refusals=42,active_receiver_movies=12,receiver_original_scripts_queued=True,receiver_foreground_pending_image_hover_retired=True,caller_pause_levels=[0,1,2],recipient_preferences_retained=True,recipient_telemetry_retained=True,audio_driver='wasapi',muted=True,main_modified=False,limits=['Explicit native active-recipient ownership fixtures, not ordinary gameplay in every recipient','Physical source comes from the earlier actual public ASVM31 producer; producer/consumer executable identities are separate'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'));print('21 active receivers and42atomic invalid-input refusals PASS',flush=True)
except Exception:state('FAILED',error=traceback.format_exc());raise
