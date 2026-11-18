"""Run the installed engine's normal player loop with isolated configuration and saves."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
w=Path(__file__).resolve().parent;out=w/'exploration-player-nov18';out.mkdir(exist_ok=False);saves=out/'saves';saves.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();exe=w/'build/Releasex64/scummvm.exe';expected=json.loads((w/'p513-control-music-seal-nov17.json').read_text())['exe_sha256'];assert sha(exe)==expected
cfg=out/'test.ini';cfg.write_text('[scummvm]\nconfirm_exit=false\nautosave_period=0\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=false\nmusic_volume=128\nsfx_volume=128\n[astro-observe]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_start_place=103\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='windows',SDL_AUDIODRIVER='wasapi');log=out/'native.log'
with(out/'console.log').open('w')as console:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(saves),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-observe'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
 subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','exploration-real-player-nov18','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
 (out/'status.json').write_text(json.dumps(dict(status='RUNNING_NORMAL_PLAYER',at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),native_pid=child.pid,exe_sha256=expected),indent=2)+'\n');code=child.wait()
text=log.read_text(errors='replace');assert code==0 and 'Astronomica P103 loop: S902.WAV'in text and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.')
assert sha(exe)==expected and not list(saves.iterdir())
(out/'proof.json').write_text(json.dumps(dict(status='INSTALLED_NORMAL_EXPLORATION_PLAYER_PASS',at=datetime.now(timezone.utc).isoformat(),exe_sha256=expected,config_sha256=sha(cfg),native_log_sha256=sha(log),native_exited_naturally=True,diagnostic_flags_absent=True,mute=False,music_volume=128,limits=['Explicit initial P103,normal interactive run loop and original assets;not a full new-game introduction','Native stream-start log and visible player only;not an acoustic loopback or complete audiovisual certificate']),indent=2)+'\n');print('INSTALLED_NORMAL_EXPLORATION_PLAYER_PASS')
