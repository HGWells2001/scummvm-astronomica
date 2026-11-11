"""Wait all native children naturally;collect actual per-scene script admission evidence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys,time,traceback
from input_support_inventory_source_nov11b import PROBE
w=Path(__file__).resolve().parent;s=w/'input-support-inventory-nov11b-stage';out=w/'input-support-inventory-native-nov11b';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_DIAGNOSTIC_BUILD')
 while not(s/'proof.json').exists():
  e=w/'input-support-inventory-nov11b-build.err'
  if e.exists()and e.stat().st_size:raise RuntimeError(e.read_text())
  time.sleep(1)
 b=read(s/'proof.json');base=w/'contextual-cursors-nov11b-stage';original=read(base/'proof.json');assert b['base_exe_sha256']==original['candidate_exe_sha256'];cpp=s/'source/engines/astronomica/astronomica.cpp';anchor='bool AstronomicaEngine::verifyBuilderPuzzle() {'
 assert cpp.read_text().replace(anchor+'\n'+PROBE,anchor)==(base/'source/engines/astronomica/astronomica.cpp').read_text()
 for name,h in original['candidate_engine_sha256'].items():
  if name!='astronomica.cpp':assert sha(s/'source/engines/astronomica'/name)==h
 exe=s/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256'];(out/'saves').mkdir();cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_builder=true\nastronomica_verify_input_support_inventory=true\nsavepath='+(out/'saves').as_posix()+'\n')
 source=cpp.read_text();assert 'ConfMan.hasKey("astronomica_verify_input_support_inventory")'in source and 'ConfMan.hasKey("astronomica_verify_builder")'in source
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_REAL_ENGINE_ADMISSION_INVENTORY')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
  subprocess.run([sys.executable,str(w/'suite_poweroff_nov11.py'),'register','--pid',str(child.pid),'--label','input-support-inventory-native-engine','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Log closed successfully'in text,text[-4000:]
 assert 'INPUT INVENTORY RESUME GATE PASS (live0,available1,unavailable_refused1,live_unchanged1)'in text
 m=re.search(r'INPUT INVENTORY COMPLETE scenes(\d+) rejected(\d+) lists(\d+) commands(\d+) unsupported(\d+)',text);assert m
 scenes,rejected,lists,commands,unsupported=map(int,m.groups());assert(scenes,rejected)==(420,1)
 rows=[dict(scene=int(m[0]),owner=m[1],index=int(m[2]),commands=int(m[3]),accepted=m[4]=='1',first_offset=int(m[5]))for m in re.findall(r'INPUT INVENTORY LIST P(\d+) owner(\S+) index(\d+) commands(\d+) accepted([01]) offset(\d+)',text)];assert len(rows)==lists and sum(c['commands']for c in rows)==commands and sum(not c['accepted']for c in rows)==unsupported
 (out/'lists-local.json').write_text(json.dumps(rows,indent=2)+'\n');prefs=read(w/'nov11-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256'] and not list((out/'saves').iterdir())
 j=dict(status='REAL_ENGINE_INPUT_SUPPORT_ADMISSION_INVENTORY_PASS',completed_at=datetime.now(timezone.utc).isoformat(),shipping_candidate_exe_sha256=original['candidate_exe_sha256'],diagnostic_exe_sha256=sha(exe),shipping_source_recovered_exactly=True,all_other22engine_files_and_header_identical=True,scenes=scenes,rejected_scenes=re.findall(r'INPUT INVENTORY SCENE REJECTED P(\d+)',text),script_lists=lists,commands=commands,unsupported_lists=unsupported,sole_rejection_classified_as_original_resume_availability=True,isolated_runner_gate_negative_and_positive_controls=True,unsupported=[c for c in rows if not c['accepted']],native_log_sha256=sha(log),lists_sha256=sha(out/'lists-local.json'),native_exited_naturally=True,user_preferences_unchanged=True,limits=['Actual canRun preflight on each scene-configured real engine;original scripts are not executed by this inventory','Admission does not prove correct runtime semantics,reachable input geometry,timing,audio or natural whole-game completion','Original P406data rejected separately;not declared unused/unreachable','Diagnostic not installed;no save files written'])
 (out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');state('PASS');print(j['status'],scenes,lists,commands,unsupported)
except Exception:state('FAILED',error=traceback.format_exc());raise
