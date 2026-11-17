"""Fresh-process continuation of genuine pre-fix physical P512 files."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,sys,hashlib,json,os,shutil,struct,subprocess,traceback
ap=argparse.ArgumentParser();ap.add_argument('--installed',action='store_true');args=ap.parse_args();w=Path(__file__).resolve().parent
out=w/('audio-restore-main-genuine-nov17'if args.installed else'audio-restore-genuine-nov17');out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,updated_at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n')
try:
 producer=w/'genuine-p512-old-main-nov10';p=read(producer/'proof.json');assert p['status']=='GENUINE_PRE_FIX_MAIN_P512_ASVM29_NORMAL_ROUTES_PASS'
 stage=w/'audio-restore-candidate-nov17-stage';build=read(stage/'proof.json');exe=w/'build/Releasex64/scummvm.exe'if args.installed else stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256']
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');results=[];state('RUNNING_GENUINE_ASVM29_FRESH_PROCESSES')
 for slot,prior in (((29,0),)if args.installed else((29,0),(30,1))):
  source=producer/'saves'/f'astro-verify.{slot:03}';pin=p['physical_slots'][str(slot)]['sha256'];assert sha(source)==pin
  data=source.read_bytes();words=struct.unpack_from('<2481I',data,8);h=2166136261
  for v in words[:-1]:h=((h^v)*16777619)&0xffffffff
  assert data[:4]==b'ASVM' and struct.unpack_from('<I',data,4)[0]==29 and words[-1]==h and words[0]==512 and words[1]==prior and words[4]==0 and words[5]==words[7]==1 and words[24+309]==127 and words[24+28*3]==prior
  for entry in(('false',)if args.installed else('true','false')):
   case=out/f'slot{slot}-{entry}';case.mkdir();saves=case/'saves';saves.mkdir();shutil.copyfile(source,saves/source.name)
   cfg=case/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nsave_slot='+str(slot)+'\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts='+entry+'\nastronomica_verify_p512=true\nsavepath='+saves.as_posix()+'\n')
   log=case/'native.log'
   with(case/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=case,env=env,stdout=console,stderr=subprocess.STDOUT)
    try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','p512-replay-genuine-slot'+str(slot)+'-'+entry,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
    finally:code=child.wait()
   text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'P512 ASVM29 fresh physical continuation: PASS'in text and ('P512 ordinary final continuation: PASS (priorGlobal%d,P157,count1,'%prior)in text,text[-2500:]
   assert 'introduction:'not in text and 'Using SDL Audio Driver "wasapi"'in text
   assert sha(source)==sha(saves/source.name)==pin
   results.append(dict(slot=slot,entry_scripts=entry,prior_global28=prior,final_scene=157,final_counter=1,physical_file_sha256=pin,native_log_sha256=sha(log),no_startup_replay=True))
 assert sha(exe)==build['candidate_exe_sha256']
 prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 receipt=dict(status='INSTALLED_AUDIO_RESTORE_GENUINE_P512_CONTINUATION_PASS'if args.installed else'AUDIO_RESTORE_GENUINE_PRE_FIX_P512_CONTINUATION_PASS',completed_at=datetime.now(timezone.utc).isoformat(),producer_exe_sha256=p['producer_exe_sha256'],consumer_exe_sha256=sha(exe),producer_proof_sha256=sha(producer/'proof.json'),fresh_processes=len(results),results=results,all_processes_exited_naturally=True,actual_audio_driver='wasapi',muted=True,limits=['One genuine pre-fix first-completion ASVM29 file through the actual installed executable'if args.installed else'Two genuine exact pre-fix-main final-question ASVM29 files,first/repeated completion and both entry-script configurations','Declared active ordinary S0 stopped boundary; no all-version or all-boundary compatibility claim'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS');print('Genuine P512 pre-fix fresh continuations PASS:',len(results),'processes')
except Exception:state('FAILED',error=traceback.format_exc());raise
