"""Exercise the unchanged navigation/input verifier with progress presentation enabled."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
w=Path(__file__).resolve().parent;out=w/'all-effects-navigation-nov19';out.mkdir(exist_ok=False);(out/'saves').mkdir();s=w/'all-effects-candidate-nov19-stage';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((s/'proof.json').read_text());exe=s/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256']
cfg=out/'test.ini';log=out/'native.log';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_mapped_navigation=true\nastronomica_mapped_navigation_expected=true\n',encoding='utf-8')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
    try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','progress-indicator-760-navigation-routes','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
    finally:code=child.wait()
text=log.read_text(errors='replace');assert code==0 and 'Mapped navigation original routes: PASS (expected1,scenes306,routes760,'in text and 'Mapped navigation native result: PASS'in text and 'FAIL'not in text,text[-2500:]
assert text.rstrip().endswith('--- Log closed successfully.')and not list((out/'saves').iterdir())
(out/'proof.json').write_text(json.dumps(dict(status='PROGRESS_INDICATOR_NAVIGATION_REGRESSION_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),scenes=306,routes=760,native_exited_naturally=True,limits=['Existing arrow/keypad,input-lock,modifier tests while the new presentation layer executes','Controlled source loads,not proof of every route natural reachability']),indent=2)+'\n',encoding='utf-8');print('PROGRESS_INDICATOR_NAVIGATION_REGRESSION_PASS')
