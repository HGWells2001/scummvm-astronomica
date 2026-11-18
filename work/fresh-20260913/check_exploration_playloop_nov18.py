"""Check every mode1 room through the unmodified normal frame pump of an observer build."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys,traceback
w=Path(__file__).resolve().parent;stage=w/'exploration-playloop-observer-nov18b-stage';out=w/'exploration-playloop-native-nov18';out.mkdir(exist_ok=False);(out/'saves').mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n')
try:
 build=read(stage/'proof.json');assert build['status']=='EXPLORATION_PLAYLOOP_OBSERVER_B_BUILD_PASS';exe=stage/'bin/scummvm.exe';pin=build['candidate_exe_sha256'];assert sha(exe)==pin
 original=read(w/'p513-control-music-seal-nov17.json');assert build['base_exe_sha256']==sha(w/'build/Releasex64/scummvm.exe')==original['exe_sha256']
 from exploration_playloop_source_nov18b import observe
 source=w.parents[1]/'outputs/astronomica-cleanroom/engine/astronomica';cpp,header=observe((source/'astronomica.cpp').read_text(),(source/'astronomica.h').read_text());assert cpp==(stage/'source/engines/astronomica/astronomica.cpp').read_text() and header==(stage/'source/engines/astronomica/astronomica.h').read_text()
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\nmusic_volume=128\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_start_place=103\nastronomica_observe_exploration_frames=true\n');log=out/'native.log'
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');state('RUNNING_NORMAL_FRAME_SWEEP',candidate_exe_sha256=pin)
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
  try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','all-mode1-normal-frame-loop-nov18','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
  finally:code=child.wait()
 text=log.read_text(errors='replace');rows=[tuple(map(int,row))for row in re.findall(r'Exploration frame room: P(\d+) expected(\d+) actual(\d+) active(\d) advancing(\d) paused(\d) volume(\d+) muted(\d)',text)]
 inventory=read(w/'scene-audio-mode-inventory-nov17.json');expected=[(r['place'],r['normal_loop'])for r in inventory['rows']if r['mode']==1]
 assert code==0 and len(rows)==len(expected)==306 and 'Exploration frame sweep complete: passed306 total306'in text,text[-2600:]
 assert [(r[0],r[1])for r in rows]==expected and all(r[1]==r[2] and r[3:]==(1,1,0,128,1)for r in rows)
 assert 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.') and not list((out/'saves').iterdir())
 assert sha(exe)==pin and sha(w/'build/Releasex64/scummvm.exe')==original['exe_sha256']
 receipt=dict(status='ALL_MODE1_NORMAL_FRAME_MUSIC_PASS',at=datetime.now(timezone.utc).isoformat(),observer_exe_sha256=pin,canonical_exe_sha256=original['exe_sha256'],observer_build_proof_sha256=sha(stage/'proof.json'),native_log_sha256=sha(log),rooms=306,active_and_advancing_streams=306,configuration_defaults_used_for_engine_options=True,normal_frame_pump_preserved=True,canonical_engine_changed=False,header_unchanged=True,native_exited_naturally=True,mute=True,music_volume=128,audio_driver='wasapi',limits=['Controlled direct room loads followed by the actual frame loop;global60 reset0,mouse at dummy-backend position','Music stream ownership and elapsed progress;not an acoustic recording or complete route/playthrough certificate','Only mode1 exploration rooms;observer executable is not deployed as the canonical game build'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS');print(receipt['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
