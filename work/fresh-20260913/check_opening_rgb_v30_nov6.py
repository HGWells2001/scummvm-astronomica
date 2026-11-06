"""Eight genuine sealed ASVM30 continuations on the complete ASVM31 binary."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,os,re,shutil,struct,subprocess,traceback
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage';out=w/'opening-rgb-genuine-v30-nov6'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
out.mkdir(exist_ok=False);slots=out/'physical-slots';slots.mkdir()
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 full=read(s/'complete-build/proof.json');exe=s/'complete-build/bin/scummvm.exe';pin=d(exe);assert pin==full['candidate_exe_sha256']
 seal=read(w/'p525-seal-nov4-status.json');snapshot=Path(seal['verified_snapshot']);manifest=read(snapshot/'snapshot-manifest.json')
 assert d(snapshot/'snapshot-manifest.json')==seal['snapshot_manifest_sha256'] and d(snapshot/'scummvm.exe')==seal['exe_sha256']
 frozen={}
 for slot in range(31,35):
  for suffix in ('','.expected'):
   name='astro-verify.%03d'%slot+suffix;assert d(snapshot/name)==manifest[name]
   shutil.copyfile(snapshot/name,slots/name);frozen[name]=d(slots/name)
 original=w/'check_p525_physical_fresh_nov3c.py';tree=ast.parse(original.read_text())
 # Reuse only its independently tested strict payload/metadata readers;
 # the old launching/preflight code never executes in this process.
 defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ('fnv','expected_file','physical_file')]
 assert len(defs)==3;exec(compile(ast.Module(body=defs,type_ignores=[]),str(original),'exec'))
 rows=[physical_file(expected_file(slot))for slot in range(31,35)]
 oldproof=read(w/'p525-physical-nov3c-stage/candidate-build/proof.json');assert oldproof['candidate_exe_sha256']==seal['exe_sha256']
 for name,expected in frozen.items():assert d(w/'p525-physical-nov3c-stage/candidate-build/physical-slots'/name)==expected
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');runs=[];state('RUNNING_EIGHT_GENUINE_V30_PROCESSES')
 for row in rows:
  for entry in ('false','true'):
   label='slot%d-%s'%(row['slot'],entry);cfg=out/(label+'.ini');log=out/(label+'.log')
   cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\nmusic_volume=0\nsfx_volume=0\nspeech_volume=0\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts='+entry+'\nastronomica_verify_p525_fresh_physical=true\nsavepath='+slots.as_posix()+'\n')
   with(out/(label+'-console.log')).open('w')as console:result=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(slots),'--logfile='+str(log),'--debuglevel=1','--save-slot='+str(row['slot']),'astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT,timeout=120)
   text=log.read_text();assert result.returncode==0 and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-2000:]
   expected=tuple([str(row['slot'])]+['%08x'%value for value in (row['source'][-1],row['pixels'],row['background'],row['future'][-1],row['future_pixels'],row['future_background'])])
   actual=re.findall(r'P525 ASVM30 fresh physical: PASS \(slot(\d+),source([0-9a-f]{8}),pixels([0-9a-f]{8}),bg([0-9a-f]{8}),future([0-9a-f]{8}),futurePixels([0-9a-f]{8}),futureBg([0-9a-f]{8}),',text)
   assert actual==[expected] and re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
   assert 'P525 introduction:'not in text and 'P525 ASVM30 physical capture:'not in text
   for name,expected_hash in frozen.items():assert d(slots/name)==d(snapshot/name)==expected_hash
   runs.append(dict(label=label,slot=row['slot'],entry_scripts=entry=='true',log_sha256=d(log),config_sha256=d(cfg),original_selector_successor=True));print(label+' genuine ASVM30 PASS',flush=True)
   state('RUNNING_EIGHT_GENUINE_V30_PROCESSES',completed=len(runs),total=8)
 assert d(exe)==pin and len(runs)==8
 proof=dict(status='P523_COMPLETE_GENUINE_ASVM30_EIGHT_PROCESSES_PASS',candidate_exe_sha256=pin,stage_sha256=full['stage_sha256'],producer_exe_sha256=seal['exe_sha256'],producer_commit=seal['published_commit'],producer_snapshot_manifest_sha256=d(snapshot/'snapshot-manifest.json'),original_metadata_reader_sha256=d(original),frozen_inputs_sha256=frozen,cases=runs,physical_slots=[31,32,33,34],fresh_processes=8,entry_true_false=True,payload_version=30,original_selector_successor=True,full_original_packet_and_rgb=True,metadata_validated=True,original_inputs_unchanged=True,audio_driver='wasapi',muted=True,main_modified=False,driver_sha256=d(Path(__file__)),limits=['Genuine four sealed ASVM30 files, initial/postvideo with/without S0; S0 restarts from beginning as original supported policy','Silent real-device continuation checks; no listening or sample-phase parity'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'))
except Exception:state('FAILED',error=traceback.format_exc());raise
