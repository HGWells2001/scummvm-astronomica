"""Replay newly serialized data from 185 preserved native captures, not old saves."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,time,traceback
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage';out=w/'opening-rgb-recorded-nov6'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
out.mkdir(exist_ok=False)
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 build=read(s/'complete-build/proof.json');exe=s/'complete-build/bin/scummvm.exe';pin=d(exe);assert pin==build['candidate_exe_sha256']
 data=w/'p523-recorded-captures-nov4-to-asvm31-nov5.bin';origin=read(w/'p523-recorded-captures-nov5-provenance.json')
 assert len(origin['records'])==185 and d(data)==origin['manifest_sha256'] and not origin['genuine_historical_asvm31_save_files']
 assert d(w/'p523-original-rebuild-full-nov4/native.log')==origin['source_log_sha256']
 slots=out/'slots';slots.mkdir();cfg=out/'replay.ini'
 cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p523_recorded=true\nastronomica_p523_replay='+data.as_posix()+'\nsavepath='+slots.as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_RECORDED185_PUBLIC_LOADS')
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
 rows=list(map(int,re.findall(r'P523 recorded ASVM31 row: PASS \(row(\d+),',text)))
 assert rows==[r['row']for r in origin['records']] and len(rows)==185
 assert text.count('P523 recorded ASVM31 replay: PASS')==1 and '185 expired-input atomic refusals'in text
 assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi'] and not list(slots.iterdir())
 assert pin==d(exe) and build['stage_sha256']=={n:d(s/n)for n in build['stage_sha256']} and d(data)==origin['manifest_sha256']
 proof=dict(status='P523_ASVM31_COMPLETE_RECORDED185_PUBLIC_LOAD_REWRITE_PASS',candidate_exe_sha256=pin,stage_sha256=build['stage_sha256'],log_sha256=d(log),config_sha256=d(cfg),driver_sha256=d(Path(__file__)),source_manifest_sha256=d(data),source_provenance_sha256=d(w/'p523-recorded-captures-nov5-provenance.json'),source_native_exe_sha256=origin['source_candidate_exe_sha256'],rows=rows,actual_public_load_commits=185,new_capture_rewrites=185,expired_input_atomic_refusals=185,donor_objects_available=False,startup_replayed=False,genuine_historical_asvm31_save_files=False,audio_driver='wasapi',muted=True,main_modified=False,limits=['New serialized fixtures from genuine historical native observations; not genuine historical save files','Paused data/state/renderer/clock adoption and rewrite; future gameplay has separate genuine physical-file tests','Failed timing-dependent old source diagnostic remains preserved, never counted as this PASS'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'));print('185 recorded packets public loads/rewrites/expired refusals PASS',flush=True)
except Exception:state('FAILED',error=traceback.format_exc());raise
