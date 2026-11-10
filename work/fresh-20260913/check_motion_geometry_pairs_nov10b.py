"""Compare old/cached animation geometry across seven existing real-engine puzzle verifiers."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,time,traceback
w=Path(__file__).resolve().parent;out=w/'motion-geometry-pairs-nov10b';out.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 state('WAITING_PAIRED_ANIMATION_BUILDS');deadline=time.monotonic()+14400
 while not all((w/f'motion-geometry-{v}-probe-nov10b-stage/proof.json').exists()for v in('baseline','cached')):assert time.monotonic()<deadline;time.sleep(1)
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');cases=[]
 modes=[('comet','astronomica_verify_comet','Astronomica comet interaction verification: PASS'),('ball','astronomica_verify_p501','Astronomica P501 interaction verification: PASS'),('jupiter','astronomica_verify_p516','Astronomica P516 interaction verification: PASS'),('photon','astronomica_verify_p513','Astronomica P513 interaction verification: PASS'),('probe','astronomica_verify_p522','Astronomica P522 interaction verification: PASS'),('rendezvous','astronomica_verify_p514','Astronomica P514 interaction verification: PASS'),('orbit','astronomica_verify_p526','Astronomica P526 interaction verification: PASS')]
 for name,option,expected in modes:
  records={};stats={}
  for variant in('baseline','cached'):
   stage=w/f'motion-geometry-{variant}-probe-nov10b-stage';build=read(stage/'proof.json');assert build['status']==f'MOTION_GEOMETRY_{variant.upper()}_DIAGNOSTIC_BUILD_PASS';exe=stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256']
   case=out/(name+'-'+variant);case.mkdir();(case/'saves').mkdir();cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\n'+option+'=true\nastronomica_trace_motion_geometry=true\nsavepath='+(case/'saves').as_posix()+'\n')
   log=case/'native.log';state('RUNNING_ACTUAL_ANIMATION_PAIR',puzzle=name,variant=variant,completed=len(cases));began=time.monotonic()
   with(case/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+1800
    while child.poll()is None:
     text=log.read_text(errors='replace')if log.exists()else''
     if 'FAIL'in text or time.monotonic()>deadline:child.terminate();break
     time.sleep(.25)
    code=child.wait(timeout=15)
   text=log.read_text(errors='replace');assert code==0 and expected in text and 'FAIL'not in text,text[-3000:]
   rows=[tuple(map(int,m))for m in re.findall(r'Motion dimension trace: P(\d+) id(\d+) offset(\d+) size(\d+) width(\d+) height(\d+) time(\d+) misses(\d+)',text)];assert rows
   records[variant]=[row[:-1]for row in rows];stats[variant]=dict(exe_sha256=sha(exe),log_sha256=sha(log),rows=len(rows),geometry_cache_misses=sum(r[-1]for r in rows),elapsed_seconds=time.monotonic()-began,scenes=sorted({r[0]for r in rows}))
   assert sha(exe)==build['candidate_exe_sha256']
  if records['baseline']!=records['cached']:
   mismatch=next((i for i,(a,b)in enumerate(zip(records['baseline'],records['cached']))if a!=b),min(len(records['baseline']),len(records['cached'])))
   raise AssertionError((name,'animation trace differs',mismatch,records['baseline'][mismatch:mismatch+3],records['cached'][mismatch:mismatch+3]))
  assert stats['cached']['geometry_cache_misses']<stats['cached']['rows'];trace_hash=hashlib.sha256(json.dumps(records['cached'],separators=(',',':')).encode()).hexdigest();cases.append(dict(puzzle=name,exact_geometry_and_tick_trace_sha256=trace_hash,baseline=stats['baseline'],cached=stats['cached']))
 shipping=read(w/'motion-geometry-cache-nov10b-stage/proof.json');prefs=read(w/'nov10b-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='MOTION_GEOMETRY_SEVEN_REAL_ENGINE_PATH_PAIRS_PASS',completed_at=datetime.now(timezone.utc).isoformat(),shipping_exe_sha256=shipping['candidate_exe_sha256'],cases=cases,total_motion_geometry_requests=sum(c['cached']['rows']for c in cases),total_motion_cache_misses=sum(c['cached']['geometry_cache_misses']for c in cases),user_preferences_unchanged=True,limits=['Two diagnostic real-engine builds; exact production-source binding is checked separately','Existing original-resource interaction verifiers include documented controlled edge/composition cases; not a manual natural whole-game playthrough','Exact source-image reference/dimensions/logical-tick sequence compared; trajectories and completion additionally asserted by the existing verifiers','Elapsed times are descriptive, not a controlled benchmark or FPS guarantee'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print('Seven actual old/cached animation paths match exactly')
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
