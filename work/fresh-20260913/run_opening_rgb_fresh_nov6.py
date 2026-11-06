"""Load independently produced physical P523 saves into new native processes."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
import configparser,hashlib,json,os,re,shutil,struct,subprocess,traceback
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage';producer_stage=s;out=w/'opening-rgb-fresh-nov6'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
out.mkdir(exist_ok=False)
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 source=read(producer_stage/'complete-build/native-proof.json');assert source['status']=='P523_ASVM31_COMPLETE_PHYSICAL_NATIVE_PASS'
 exe=s/'complete-build/bin/scummvm.exe';pin=d(exe);build=read(s/'complete-build/proof.json');assert pin==build['candidate_exe_sha256']
 producer=Path(source['slots']);source_pin=d(producer_stage/'complete-build/native-proof.json')
 def validate():
  assert d(exe)==pin and d(producer_stage/'complete-build/native-proof.json')==source_pin
  assert source['stage_sha256']=={n:d(producer_stage/n)for n in source['stage_sha256']} and build['stage_sha256']=={n:d(s/n)for n in build['stage_sha256']}
  for name,expected in source['physical_files_sha256'].items():assert d(producer/name)==expected
 def run(slot,entry):
  validate();label='slot%d-%s'%(slot,entry);folder=out/label;folder.mkdir();slots=folder/'slots';slots.mkdir()
  for suffix in ('','.expected'):
   name='astro-verify.%03d'%slot+suffix;shutil.copyfile(producer/name,slots/name);assert d(slots/name)==source['physical_files_sha256'][name]
  raw=(slots/('astro-verify.%03d'%slot)).read_bytes();assert raw[:4]==b'ASVM'and struct.unpack_from('<I',raw,4)[0]==31
  cfg=folder/'fresh.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts='+entry+'\nastronomica_verify_p523_fresh_physical=true\nsavepath='+slots.as_posix()+'\n')
  env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=folder/'native.log'
  with(folder/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(slots),'--logfile='+str(log),'--debuglevel=1','--save-slot='+str(slot),'astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
   try:code=child.wait(timeout=100)
   finally:
    if child.poll()is None:child.terminate();child.wait(timeout=15)
  (folder/'native-exit.json').write_text(json.dumps(dict(exit_code=code,pid=child.pid))+'\n')
  text=log.read_text();assert code==0 and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-2500:]
  assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
  assert text.count('P523 ASVM31 fresh process: PASS')==1 and 'original file load from P1'in text
  assert 'Astronomica resource explorer: P1;'in text and 'Astronomica resource explorer: P117;'in text
  assert 'P523 ordinary introduction:'not in text and 'P523 ASVM31 physical capture:'not in text
  assert '%unatural callbacks'%(44-slot) in text
  for name in source['physical_files_sha256']:
   if (slots/name).exists():assert d(slots/name)==source['physical_files_sha256'][name]
  assert len(list(slots.iterdir()))==2;validate()
  p=dict(status='PASS',slot=slot,entry_scripts=entry=='true',log_sha256=d(log),config_sha256=d(cfg),source_file_sha256=source['physical_files_sha256']['astro-verify.%03d'%slot],expected_sha256=source['physical_files_sha256']['astro-verify.%03d.expected'%slot],exit_code=code,pid=child.pid,natural_callbacks=44-slot,destination=117,source_owners_available=False,source_startup_replayed=False)
  (folder/'proof.json').write_text(json.dumps(p,indent=2)+'\n');print(label+' genuine ASVM31 fresh process PASS',flush=True);return label,p
 state('RUNNING_SIX_FRESH_ASVM31_PROCESSES');cases={}
 with ThreadPoolExecutor(max_workers=2)as pool:
  futures=[pool.submit(run,slot,entry)for slot in (41,42,43)for entry in ('true','false')]
  for future in as_completed(futures):
   label,p=future.result();cases[label]=p;state('RUNNING_SIX_FRESH_ASVM31_PROCESSES',completed=len(cases),total=6)
 validate();assert len(cases)==6
 proof=dict(status='P523_ASVM31_COMPLETE_SIX_FRESH_PROCESSES_PASS',candidate_exe_sha256=pin,stage_sha256=build['stage_sha256'],producer_exe_sha256=source['candidate_exe_sha256'],source_physical_proof_sha256=source_pin,cases=cases,physical_slots=[41,42,43],fresh_processes=6,entry_true_false=True,original_inputs_unchanged=True,actual_audio_driver='wasapi',muted=True,main_public_support=False,driver_sha256=d(Path(__file__)),limits=['Three genuine ordinary first-failure states only; not every route or source state','Real WASAPI with mute; no listening or original mixer-phase claim','Framework/full regression/source review remain separate gates before promotion'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'))
except Exception:state('FAILED',error=traceback.format_exc());raise
