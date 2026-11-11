"""Verify actual Windows SDL backend beyond the earlier dummy-screen cursor checks."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,traceback
w=Path(__file__).resolve().parent;stage=w/'contextual-cursors-nov11b-stage';out=w/'contextual-cursors-windows-native-nov11';out.mkdir(exist_ok=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 build=read(stage/'proof.json');exe=stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256'];(out/'saves').mkdir();cfg=out/'test.ini'
 cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\nfullscreen=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_navigation_cursors=true\nsavepath='+(out/'saves').as_posix()+'\n')
 assert 'ConfMan.hasKey("astronomica_verify_navigation_cursors")'in(stage/'source/engines/astronomica/astronomica.cpp').read_text()
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='windows',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_ACTUAL_WINDOWS_CURSOR_BACKEND')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
  subprocess.run([sys.executable,str(w/'suite_poweroff_nov11.py'),'register','--pid',str(child.pid),'--label','contextual-cursor-windows-backend','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text,text[-4000:]
 for marker in ['Using SDL Video Driver "windows"','Contextual down cursor verification: PASS','Navigation cursor live UI: PASS','Navigation cursor original rules: PASS','Navigation cursor ownership: PASS','Navigation cursor native result: PASS']:assert marker in text,marker
 assert text.count('Navigation cursor resource: PASS')==4 and sha(exe)==build['candidate_exe_sha256'];prefs=read(w/'nov11-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 j=dict(status='CONTEXTUAL_CURSOR_ACTUAL_WINDOWS_BACKEND_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),video_driver='windows',audio_driver='wasapi',original_groups=4,native_exited_naturally=True,forced_termination=False,user_preferences_unchanged=True,limits=['Actual SDLWindows graphics backend and actual F5menu/GUI/cursor-manager API calls,not SDLdummy','Controlled internal cursor samples,not a human physical pointer/audiovisual inspection;no human-playthrough criterion claimed'])
 (out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');state('PASS');print(j['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
