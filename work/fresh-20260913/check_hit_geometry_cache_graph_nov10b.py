"""Observe real engine original-control entry interleavings; no Windows execution claim."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,time,traceback
w=Path(__file__).resolve().parent;s=w/'hit-geometry-cache-graph-nov10b-stage';out=w/'hit-geometry-cache-graph-nov10b';out.mkdir(exist_ok=False);(out/'saves').mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 state('WAITING_TRACE_BUILD');deadline=time.monotonic()+900
 while not(s/'proof.json').exists():
  assert time.monotonic()<deadline;time.sleep(1)
 b=read(s/'proof.json');assert b['status']=='P536_DEFAULT_GRAPH_REAL_ENGINE_BUILD_PASS';exe=s/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256']
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=true\nastronomica_verify_builder=true\nastronomica_verify_p536_graph=true\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_ORIGINAL_EXPOSED_ENTRY_CLICKS')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+2400
  while child.poll()is None:
   text=log.read_text(errors='replace')if log.exists()else''
   if 'FAIL'in text or time.monotonic()>deadline:child.terminate();break
   time.sleep(.25)
  code=child.wait(timeout=15)
 text=log.read_text(errors='replace');assert code==0 and 'P536 default settled graph: PASS'in text and 'FAIL'not in text,text[-3000:]
 case=None;place=None;observations=[];targets=[];clicks=[];ends=[]
 original=read(w/'original-branches-nov6/inventory.json');commands={(c['scene'],c['file_offset']):c for c in original['commands']if c['opcode']==31}
 for line in text.splitlines():
  m=re.search(r'resource explorer: P(\d+);',line)
  if m:place=int(m[1])
  m=re.search(r'P536 ENTRY CASE BEGIN q(\d+) ticks(\d+)',line)
  if m:case=tuple(map(int,m.groups()))
  m=re.search(r'P536 ENTRY CLICK q(\d+) ticks(\d+) pending(\d+) xy(\d+),(\d+)',line)
  if m:clicks.append(list(map(int,m.groups())))
  m=re.search(r'P536 ENTRY CASE END q(\d+) ticks(\d+) project(-?\d+) phase(-?\d+) height(-?\d+)',line)
  if m:ends.append(list(map(int,m.groups())))
  m=re.search(r'condition trace: offset=(\d+) scope=(-?\d+) id=(-?\d+) value=(-?\d+) low=(-?\d+) high=(-?\d+) cmp=(-?\d+) result=(\d+) pending=(\d+)',line)
  if not m:continue
  offset,scope,ident,value,low,high,cmp_,result,pending=map(int,m.groups());source=commands[(place,offset)];assert source['args'][:5]==[scope,ident,low,high,cmp_]
  expected=value==low if cmp_==0 else value<low if cmp_==1 else value>low if cmp_==2 else low<=value<=high;assert bool(result)==expected
  row=dict(case=case,scene=place,offset=offset,original_id=source['id'],scope=scope,id=ident,value=value,low=low,high=high,comparison=cmp_,result=bool(result),pending=pending);observations.append(row)
  if place==536 and offset==350661:targets.append(row)
 graph=re.search(r'P536 default settled graph: PASS \((\d+) nodes,(\d+) original exposed-control edges,(\d+) selected-project terminals;',text);assert graph
 nodes,edges,terminals=map(int,graph.groups());assert len(re.findall(r'P536 GRAPH NODE ',text))==nodes
 assert len(re.findall(r'P536 GRAPH EDGE ',text))+len(re.findall(r'P536 GRAPH TERMINAL ',text))==edges
 assert sha(exe)==b['candidate_exe_sha256'] and sha(w/'build/Releasex64/scummvm.exe')==b['base_exe_sha256']
 assert not list((out/'saves').iterdir());prefs=read(w/'nov10b-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 (out/'observations-local.json').write_text(json.dumps(observations,indent=2)+'\n')
 proof=dict(status='P536_REAL_ENGINE_DEFAULT_SETTLED_GRAPH_OBSERVATION_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),installed_exe_sha256=b['base_exe_sha256'],native_log_sha256=sha(log),observations_sha256=sha(out/'observations-local.json'),observations=len(observations),settled_nodes=nodes,original_control_edges=edges,selected_project_terminals=terminals,target_observations=targets,native_target_observed=bool(targets),main_unchanged=True,preferences_unchanged=True,limits=['Actual real engine settled control graph; reached node paths replayed from original startup, no local injection; inclusive original rectangular hit geometry with visibility ignored','No scalar local mutation; global reset and deterministic seed isolate cases','Program-load epoch and inert sprite frame/move epochs normalized; no original Windows or arbitrary timing proof','Exact original instruction comparison of the observed path is a separate gate'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS',target_observations=len(targets));print('P536 default graph PASS:',nodes,'nodes;',edges,'edges;',len(targets),'target evaluations')
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
