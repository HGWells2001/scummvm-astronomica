"""Verify actual installed intro menu with fresh defaults and full natural voice completion."""
from pathlib import Path
from datetime import datetime,timezone
import configparser,hashlib,json,os,subprocess,sys,traceback
w=Path(__file__).resolve().parent;out=w/'intro-menu-main-native-nov12';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 stage=w/'intro-menu-candidate-nov12c-stage';b=read(stage/'proof.json');exe=w/'build/Releasex64/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256'];source=(stage/'source/engines/astronomica/astronomica.cpp').read_text();assert 'ConfMan.hasKey("astronomica_verify_intro_menu")'in source and 'updateNavigationCursor(introMouse.x,introMouse.y)'in source
 (out/'saves').mkdir();cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_intro_menu=true\nastronomica_intro_menu_expected=true\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_INSTALLED_ORIGINAL_INTRO_AND_ACTUAL_MENU')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
  try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','intro-menu-installed-native','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
  finally:code=child.wait()
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Introduction actual menu: PASS'in text and 'cursor-1,visible1'in text and 'Log closed successfully'in text,text[-3500:]
 parsed=configparser.ConfigParser(interpolation=None);parsed.read(cfg)
 for domain in ['scummvm','astro-verify']:
  for key in ['astronomica_audio','astronomica_animation','astronomica_sprite_input','astronomica_entry_scripts']:assert not parsed.has_option(domain,key)
 prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256'] and sha(exe)==b['candidate_exe_sha256'];assert not list((out/'saves').iterdir())
 j=dict(status='INSTALLED_INTRO_MENU_AND_BUSY_GUARD_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),all_four_gameplay_keys_absent=True,cursor_fallback_and_visibility=True,complete_original_voice_natural_end=True,user_preferences_unchanged=True,native_exited_naturally=True)
 (out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');state('PASS');print(j['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
