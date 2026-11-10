"""Record actual global-menu open/close behavior in four isolated GUI profiles."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,time,traceback
w=Path(__file__).resolve().parent;s=w/'hit-geometry-menu-probe-nov10b-stage';out=w/'global-menu-probe-nov10b';out.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 state('WAITING_GLOBAL_MENU_BUILD');deadline=time.monotonic()+900
 while not(s/'proof.json').exists():assert time.monotonic()<deadline;time.sleep(1)
 b=read(s/'proof.json');assert b['status']=='GLOBAL_MENU_REAL_ENGINE_PROBE_BUILD_PASS';exe=s/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256'];rows=[]
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
 for language in('en','C'):
  for fixed in(False,True):
   case=out/(language+'-fixed'+str(int(fixed)));case.mkdir();(case/'saves').mkdir();cfg=case/'test.ini'
   cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language='+language+'\ngui_theme=builtin\ngui_disable_fixed_font_scaling='+str(fixed).lower()+'\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_global_menu=true\nsavepath='+(case/'saves').as_posix()+'\n')
   log=case/'native.log';state('RUNNING_ACTUAL_GLOBAL_MENU',language=language,disable_fixed_scaling=fixed)
   with(case/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+45
    while child.poll()is None:
     if time.monotonic()>deadline:child.terminate();break
     time.sleep(.1)
    code=child.wait(timeout=15)
   text=log.read_text(errors='replace');ok=code==0 and 'Global menu actual open-close: PASS'in text and 'CRITICAL:'not in text and 'FAIL'not in text
   rows.append(dict(language=language,disable_fixed_scaling=fixed,exit_code=code,passed=ok,font_probe=[line.split('] ',1)[-1]for line in text.splitlines()if 'Global menu font probe:'in line],log_sha256=sha(log),font_load_failure="Couldn't load font"in text))
 assert sha(exe)==b['candidate_exe_sha256'];prefs=read(w/'nov10b-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='GLOBAL_MENU_POSITIVE_NATIVE_PASS'if all(r['passed']for r in rows)else'GLOBAL_MENU_POSITIVE_NATIVE_FAILURE_REPRODUCED',completed_at=datetime.now(timezone.utc).isoformat(),diagnostic_exe_sha256=sha(exe),shipping_exe_sha256=read(w/'hit-geometry-cache-nov10b-stage/proof.json')['candidate_exe_sha256'],cases=rows,user_preferences_unchanged=True,main_unchanged=True,limits=['Actual Engine global-menu dialog with queued Escape; no human visual review','SDL dummy video/WASAPI muted and isolated GUI profiles','Diagnostic real-engine build shares shipping production source; global-menu instrumentation only'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state(proof['status']);print(proof['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
