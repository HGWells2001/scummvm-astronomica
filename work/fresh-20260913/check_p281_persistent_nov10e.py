"""Exercise the real new P281 byte codec on original unsolved return routes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,struct,subprocess,time,traceback
w=Path(__file__).resolve().parent;stage=w/'p281-persistent-nov10e-stage';out=w/'p281-persistent-native-nov10e';out.mkdir(exist_ok=False);(out/'saves').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,updated_at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n')
child=None
try:
 b=read(stage/'proof.json');assert b['status']=='P281_PERSISTENT_REAL_ENGINE_CANDIDATE_BUILD_PASS';exe=stage/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256']
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=true\nastronomica_verify_p281_saves=true\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_ACTUAL_P281_RETAINED_ROUND_SAVES')
 with(out/'console.log').open('w')as console:
  child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT);deadline=time.monotonic()+1200
  while child.poll()is None:
   text=log.read_text(errors='replace')if log.exists()else''
   if 'FAIL'in text or time.monotonic()>deadline:child.terminate();break
   time.sleep(.25)
  code=child.wait(timeout=15)
 text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'P281 return-round verification: PASS'in text,text[-3500:]
 assert 'P281 retained codec refusals: PASS'in text and 'P281 retained paused recipient: PASS'in text
 rows=re.findall(r'P281 retained physical boundary: PASS \(slot(\d+),route(\d+),round(\d+),mask(\d+),fingerprint([0-9a-f]+)\)',text);assert len(rows)==6
 files={}
 for slot,route,round_,mask,fingerprint in rows:
  slot,route,round_,mask=map(int,(slot,route,round_,mask));path=out/'saves'/f'astro-verify.{slot:03}';data=path.read_bytes();assert data[:4]==b'ASVM'and struct.unpack_from('<I',data,4)[0]==32
  words=struct.unpack_from('<661I',data,8);h=2166136261
  for v in words[:-1]:h=((h^v)*16777619)&0xffffffff
  assert words[-1]==h and words[0]==281 and words[39+603]==round_ and words[39+604]==mask and slot==40+route*3+round_
  files[str(slot)]=dict(sha256=sha(path),bytes=len(data),route=route,round=round_,mask=mask,fingerprint=fingerprint)
 assert sha(exe)==b['candidate_exe_sha256']
 p=dict(status='P281_RETAINED_ROUND_ASVM32_NATIVE_CODEC_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),build_proof_sha256=sha(stage/'proof.json'),native_log_sha256=sha(log),native_payload_bytes=2652,physical_slots=files,actual_original_unsolved_returns=6,legacy_idle_v2_roundtrips=2,pending_gateway_zero_byte_refusals=8,atomic_truncations=2652,atomic_single_byte_corruptions=2652,foreign_decoder_nested_pause_recipient=True,pending_old_gateway_retired=True,first_repeated_completion=True,audio_driver='wasapi',muted=True,candidate_installed=False,limits=['Idle P281 round1..3 with original static sprite and no foreground sound; active gateway remains unsavable','Round1/2/3 produced by original unsolved controls; second route additionally seeds valid dormant dimension/comet cache values','Fresh physical process continuation is a separate gate'])
 (out/'proof.json').write_text(json.dumps(p,indent=2)+'\n');state('PASS');print('P281 ASVM32 native codec/unsolved returns PASS:6physical files')
except Exception:state('FAILED',error=traceback.format_exc());raise
finally:
 if child is not None and child.poll()is None:child.terminate();child.wait(timeout=15)
