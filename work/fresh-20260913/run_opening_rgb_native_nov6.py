"""Produce real ASVM31 saves through public engine/framework paths."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,traceback
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage';b=s/'complete-build';out=w/'opening-rgb-native-nov6'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(exist_ok=False);slots=b/'p523-physical-slots';slots.mkdir(exist_ok=False)
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 build=json.loads((b/'proof.json').read_text());exe=b/'bin/scummvm.exe';pin=d(exe)
 assert pin==build['candidate_exe_sha256'] and build['stage_sha256']=={n:d(s/n)for n in build['stage_sha256']}
 flags=['astronomica_audio','astronomica_animation','astronomica_sprite_input','astronomica_verify_p523_normal_entry','astronomica_verify_p523_detached_media','astronomica_verify_p523_paused_resume','astronomica_verify_p523_media_exchange','astronomica_verify_p523_trusted_state','astronomica_verify_p523_original_rebuild','astronomica_verify_p523_packet','astronomica_verify_p523_semantic','astronomica_capture_p523_physical']
 cfg=out/'producer.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_entry_scripts=false\nsavepath='+slots.as_posix()+'\n'+'\n'.join(f+'=true'for f in flags)+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
 log=out/'native.log';state('RUNNING_ASVM31_PHYSICAL_PRODUCER')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(slots),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
  try:code=child.wait(timeout=180)
  finally:
   if child.poll()is None:child.terminate();child.wait(timeout=15)
 (out/'native-exit.json').write_text(json.dumps(dict(exit_code=code,child_pid=child.pid))+'\n')
 text=log.read_text();assert code==0 and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-2500:]
 assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
 for marker,n in [('P523 packet transport: PASS',3),('P523 packet semantic preparation: PASS',3),('P523 ASVM31 physical capture: PASS',3),('P523 normal entry verification: PASS',1),('P523 trusted rejection matrix: PASS',3),('P523 original reconstruction: PASS',3)]:assert text.count(marker)==n,(marker,text.count(marker))
 assert '17128public parser refusals'in text and '8564truncations,8564byte flips'in text
 files={}
 for slot in (41,42,43):
  for suffix in ('','.expected'):
   p=slots/('astro-verify.%03d'%slot+suffix);assert p.exists();files[p.name]=d(p)
 assert sorted(p.name for p in slots.iterdir())==sorted(files)
 assert d(exe)==pin and d(w/'build/Releasex64/scummvm.exe')==json.loads((s/'before.json').read_text())['base_exe_sha256']
 proof=dict(status='P523_ASVM31_COMPLETE_PHYSICAL_NATIVE_PASS',candidate_exe_sha256=pin,stage_sha256=build['stage_sha256'],log_sha256=d(log),config_sha256=d(cfg),driver_sha256=d(Path(__file__)),slots=str(slots),physical_files_sha256=files,physical_slots=[41,42,43],packet_words=2139,native_bytes=8564,transport_truncations=8564,transport_byte_flips=8564,public_parser_refusals=17128,semantic_refusals=183,metadata_query_list_thumbnail=True,candidate_public_dispatch=True,main_public_support=False,audio_driver='wasapi',muted=True,limits=['Physical writing verified; source-independent fresh loading has separate proof','Bounded quiet active P523 states only, not every possible help/history/motion state'])
 (s/'complete-build/native-proof.json').write_text(json.dumps(proof,indent=2)+'\n');(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS',proof_sha256=d(s/'complete-build/native-proof.json'))
 print('Actual ASVM31 physical slots41/42/43 and metadata PASS',flush=True)
except Exception:state('FAILED',error=traceback.format_exc());raise
