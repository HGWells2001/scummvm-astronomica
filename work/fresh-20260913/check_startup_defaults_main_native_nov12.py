"""Verify the actual installed executable with a genuinely fresh target configuration."""
from pathlib import Path
from datetime import datetime,timezone
import configparser,hashlib,json,os,subprocess,sys,traceback
w=Path(__file__).resolve().parent;out=w/'startup-defaults-main-native-nov12';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 b=read(w/'startup-defaults-candidate-nov12c-stage/proof.json');exe=w/'build/Releasex64/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256'];source=(w/'startup-defaults-candidate-nov12c-stage/source/engines/astronomica/astronomica.cpp').read_text();assert 'ConfMan.hasKey("astronomica_verify_startup_defaults")'in source
 (out/'saves').mkdir();cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_startup_defaults=true\nastronomica_expected_startup_mask=15\nastronomica_expected_explicit_mask=0\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_INSTALLED_FRESH_TARGET')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
  subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','startup-defaults-installed-native','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text
 for marker in ['Startup defaults configuration: PASS (observed15,expected15,explicit0,expectedExplicit0,P1pending1)','Startup defaults animation: PASS','Startup defaults actual input: PASS','Startup defaults actual audio: PASS (S0played1)','Startup defaults native result: PASS']:assert marker in text,marker
 parsed=configparser.ConfigParser(interpolation=None);parsed.read(cfg)
 for domain in ['scummvm','astro-verify']:
  for key in ['astronomica_audio','astronomica_animation','astronomica_sprite_input','astronomica_entry_scripts']:assert not parsed.has_option(domain,key)
 prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256'] and sha(exe)==b['candidate_exe_sha256']
 j=dict(status='INSTALLED_STARTUP_DEFAULTS_FRESH_TARGET_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),no_gameplay_keys_created=True,original_entry_animation_input_and_audio_dispatch=True,user_preferences_unchanged=True,native_exited_naturally=True)
 (out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');state('PASS');print(j['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
