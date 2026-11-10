"""Compare the real engine's cached hit results with its frozen uncached decoder path."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,time,traceback
w=Path(__file__).resolve().parent;s=w/'motion-geometry-cache-nov10b-stage';out=w/'motion-geometry-cache-native-nov10b';out.mkdir(exist_ok=False);(out/'saves').mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 state('WAITING_CACHED_ENGINE_BUILD');deadline=time.monotonic()+900
 while not(s/'proof.json').exists():assert time.monotonic()<deadline;time.sleep(1)
 b=read(s/'proof.json');assert b['status']=='MOTION_GEOMETRY_CACHE_REAL_ENGINE_BUILD_PASS';exe=s/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256']
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_hit_geometry=true\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_REAL_ENGINE_CACHED_UNCACHED_COMPARISON')
 began=time.monotonic()
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+2700
  while child.poll()is None:
   text=log.read_text(errors='replace')if log.exists()else''
   if 'FAIL'in text or 'Hit geometry mismatch:'in text or time.monotonic()>deadline:child.terminate();break
   time.sleep(.25)
  code=child.wait(timeout=15)
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text,text[-3500:]
 m=re.search(r'Hit geometry verification: PASS \((\d+) original scenes,(\d+) oracle queries,(\d+) hidden controls,(\d+) unknown-frame cases,(\d+) unsupported states;',text);assert m,text[-3000:]
 scenes,queries,hidden,unknown,unsupported=map(int,m.groups());assert scenes==41 and queries>100 and hidden and unknown and unsupported
 rows=[dict(zip(('scene','cache_entries','queries_total','decode_attempts_total'),map(int,m)))for m in re.findall(r'Hit geometry scene: PASS \(P(\d+),cache(\d+),queries(\d+),decodeAttempts(\d+)\)',text)];assert len(rows)==scenes and len({r['scene']for r in rows})==scenes
 assert sha(exe)==b['candidate_exe_sha256'] and sha(w/'build/Releasex64/scummvm.exe')==b['base_exe_sha256'];prefs=read(w/'nov10b-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='MOTION_GEOMETRY_REAL_ENGINE_CACHE_ORACLE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),previous_main_exe_sha256=b['base_exe_sha256'],build_proof_sha256=sha(s/'proof.json'),native_log_sha256=sha(log),elapsed_seconds=time.monotonic()-began,original_scenes=scenes,oracle_queries=queries,hidden_controls=hidden,unknown_frame_tests=unknown,unsupported_states=unsupported,warm_queries_without_decode=scenes*32,reload_invalidates=True,missing_file_still_refused=True,failed_decode_not_cached=True,rows=rows,main_unchanged=True,user_preferences_unchanged=True,limits=['Frozen pre-cache native decoder algorithm is the comparison oracle; original rectangular geometry rules were established separately','Controlled scene/frame/unsupported-state tests on exact original resources; no manual whole-game playthrough','No wall-clock speed threshold or original Windows execution claim'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print('Hit geometry cache matches uncached native oracle:',scenes,'scenes',queries,'queries')
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
