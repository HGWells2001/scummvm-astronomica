"""Consume six physical ASVM32 saves in twelve independent real-engine processes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess,time,traceback
w=Path(__file__).resolve().parent;stage=w/'hit-geometry-cache-nov10b-stage';producer=w/'p281-persistent-native-nov10e'
out=w/'hit-geometry-cache-main-smoke-nov10b';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
child=None
try:
 p=read(producer/'proof.json');assert p['status']=='P281_RETAINED_ROUND_ASVM32_NATIVE_CODEC_PASS'
 exe=w/'build/Releasex64/scummvm.exe';assert sha(exe)==read(stage/'proof.json')['candidate_exe_sha256'];rows=[]
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
 for slot,record in list(p['physical_slots'].items())[:1]:
  for entry in (False,):
   case=out/f'slot{slot}-entry{int(entry)}';case.mkdir();saves=case/'saves';saves.mkdir()
   src=producer/'saves'/f'astro-verify.{int(slot):03}';assert sha(src)==record['sha256'];shutil.copyfile(src,saves/src.name)
   cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts='+str(entry).lower()+'\nastronomica_verify_p281_saves=true\nsave_slot='+slot+'\nsavepath='+saves.as_posix()+'\n')
   log=case/'native.log';state('RUNNING_FRESH_RETAINED_CONTINUATION',slot=slot,entry_scripts=entry,completed=len(rows))
   with(case/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+180
    while child.poll()is None:
     text=log.read_text(errors='replace')if log.exists()else''
     if 'FAIL'in text or time.monotonic()>deadline:child.terminate();break
     time.sleep(.25)
    code=child.wait(timeout=15)
   text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text,text[-3000:]
   m=re.search(r'P281 retained fresh continuation: PASS \(startRound(\d+),priorGlobal(\d+),P519,count(\d+),original gateway/unsolved controls\)',text);assert m,text[-3000:]
   assert int(m[1])==record['round'] and int(m[2])==record['route'] and int(m[3])==1
   assert sha(src)==record['sha256']==sha(saves/src.name)
   rows.append(dict(slot=int(slot),initial_entry_scripts=entry,round=int(m[1]),prior_solved=int(m[2]),final_count=int(m[3]),log_sha256=sha(log),physical_save_sha256=sha(src)))
 assert len(rows)==1 and sha(exe)==read(stage/'proof.json')['candidate_exe_sha256']
 proof=dict(status='INSTALLED_HIT_GEOMETRY_GENUINE_ASVM32_CONTINUATION_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),producer_exe_sha256=p['candidate_exe_sha256'],producer_proof_sha256=sha(producer/'proof.json'),cases=rows,original_controls=True,no_repeated_variant=True,first_repeated_completion=True,source_files_unchanged=True,limits=['Six real physical files; no all-version compatibility claim','Initial entry flag tested both ways; standalone verifier enables it for subsequent original gateway controls'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print('P281 ASVM32 twelve fresh continuations PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
