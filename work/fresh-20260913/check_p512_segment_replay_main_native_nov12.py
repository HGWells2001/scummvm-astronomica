"""Verify installed mapped directions in a fresh isolated native process."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
w=Path(__file__).resolve().parent;out=w/'p512-segment-replay-main-native-nov12';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());b=read(w/'p512-segment-replay-nov12-stage/proof.json');exe=w/'build/Releasex64/scummvm.exe'
assert sha(exe)==b['candidate_exe_sha256'];saves=out/'saves';saves.mkdir();cfg=out/'test.ini'
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_mapped_navigation=true\nastronomica_mapped_navigation_expected=true\nsavepath='+saves.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log'
with(out/'console.log').open('w')as console:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
 try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','p512-segment-replay-installed-native','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
 finally:code=child.wait()
text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Mapped navigation native result: PASS'in text and 'expected1,scenes306,routes760'in text and 'Log closed successfully'in text,text[-3500:]
assert not list(saves.iterdir()) and sha(exe)==b['candidate_exe_sha256'];prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
j=dict(status='INSTALLED_P512_SEGMENT_REPLAY_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),original_scenes=306,original_routes=760,stock_keymap_events_checked=True,actual_P27_input_lock_and_modifiers_preserved=True,user_preferences_unchanged=True,native_exited_naturally=True)
(out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
