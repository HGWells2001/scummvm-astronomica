"""Run the real startup sequence to its natural boundary with isolated preferences."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
w=Path(__file__).resolve().parent
out=w/'effect-mix-native-nov16';out.mkdir(exist_ok=False)
exe=w/'effect-mix-candidate-nov16-stage/bin/scummvm.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prefs=json.loads((w/'nov12-user-prefs-pin.json').read_text())
rows=[]
for label,override in [('feedback-and-voice',None)]:
 case=out/label;case.mkdir();(case/'saves').mkdir()
 cfg=case/'test.ini'
 cfg.write_text('[scummvm]\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\n[astro-test]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_effect_mix=true\n'+('astronomica_start_place='+str(override)+'\n' if override is not None else ''),encoding='utf-8')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
 log=case/'native.log'
 with (case/'console.log').open('w') as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--logfile='+str(log),'--savepath='+str(case/'saves'),'--extrapath='+str(w/'fonts'),'--debuglevel=1','astro-test'],cwd=case,env=env,stdout=console,stderr=subprocess.STDOUT)
  subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','startup-logo-nov16-'+label,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
  code=child.wait()
 text=log.read_text(errors='replace')
 assert code==0 and 'Effect mix native result: PASS' in text and 'FAIL' not in text,text[-4000:]
 assert not list((case/'saves').iterdir())
 rows.append(dict(profile=label,log_sha256=sha(log),native_exited_naturally=True))
assert sha(Path(prefs['path']))==prefs['sha256']
(out/'proof.json').write_text(json.dumps(dict(status='EFFECT_MIX_NATIVE_PASS',created_at=datetime.now(timezone.utc).isoformat(),exe_sha256=sha(exe),cases=rows,user_preferences_unchanged=True,limitations=['Dummy video with real WASAPI; music/effect overlap and exclusive narration verified','Four identified shared feedback assets and original P517 S1 voice; unclassified clips retain foreground routing']),indent=2)+'\n')
print('EFFECT_MIX_NATIVE_PASS')
