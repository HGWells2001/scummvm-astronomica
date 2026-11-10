"""Continue two frozen pre-cache physical motion-puzzle saves through actual original controls."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,struct,subprocess,time,traceback
w=Path(__file__).resolve().parent;s=w/'motion-geometry-cache-nov10b-stage';out=w/'motion-geometry-old-saves-nov10b';out.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 b=read(s/'proof.json');assert b['status']=='MOTION_GEOMETRY_CACHE_REAL_ENGINE_BUILD_PASS';exe=s/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256']
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');rows=[]
 fixtures=[('p501-025e82d8bd3b',26,27,501,'astronomica_verify_p501_saves','Astronomica P501 startup save: PASS'),('p504-2a305b134662',25,26,504,'astronomica_verify_p504_saves','Astronomica P504 startup save: PASS')]
 for frozen,slot,version,place,option,expected in fixtures:
  folder=w/'verified-checkpoints'/frozen;origin=read(folder/f'frozen-slot{slot}.json');source=folder/f'frozen-slot{slot}'/f'astro-verify.{slot:03}';assert sha(folder/'scummvm.exe')==origin['producing_exe_sha256']and sha(source)==origin['slot_sha256'];data=source.read_bytes();assert data[:4]==b'ASVM'and struct.unpack_from('<II',data,4)==(version,place)
  for entry in(False,True):
   case=out/f'v{version}-entry{int(entry)}';case.mkdir();(case/'saves').mkdir();shutil.copyfile(source,case/'saves'/source.name)
   cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts='+str(entry).lower()+'\nsave_slot='+str(slot)+'\n'+option+'=true\nsavepath='+(case/'saves').as_posix()+'\n')
   log=case/'native.log';state('RUNNING_FROZEN_MOTION_SAVE_CONTINUATION',version=version,scene=place,entry_scripts=entry)
   with(case/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+600
    while child.poll()is None:
     text=log.read_text(errors='replace')if log.exists()else''
     if 'FAIL'in text or time.monotonic()>deadline:child.terminate();break
     time.sleep(.25)
    code=child.wait(timeout=15)
   text=log.read_text(errors='replace');assert code==0 and expected in text and 'FAIL'not in text,text[-3000:]
   assert sha(source)==sha(case/'saves'/source.name)==origin['slot_sha256']
   rows.append(dict(version=version,scene=place,initial_entry_scripts=entry,producing_exe_sha256=origin['producing_exe_sha256'],frozen_slot_sha256=sha(source),origin_receipt_sha256=sha(folder/f'frozen-slot{slot}.json'),native_log_sha256=sha(log),full_future_asserted=True))
 assert len(rows)==4 and sha(exe)==b['candidate_exe_sha256'];prefs=read(w/'nov10b-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='MOTION_GEOMETRY_FROZEN_ASVM26_27_FUTURES_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),cases=rows,source_files_unchanged=True,user_preferences_unchanged=True,limits=['Two frozen physical files produced by accepted earlier cleanroom engine verifiers, not original Windows save files','Four fresh processes/entry configurations with existing actual-control full-future assertions','No arbitrary all-version/all-history or manual whole-game playthrough claim'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print('Four frozen ASVM26/27 motion-puzzle futures PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
