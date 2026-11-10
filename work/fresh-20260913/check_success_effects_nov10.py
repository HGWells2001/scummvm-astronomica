"""Compare real completion callbacks/voices with original instruction expectations."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,struct,subprocess,traceback
w=Path(__file__).resolve().parent;stage=w/'success-effects-nov10-stage';out=w/'success-effects-native-nov10';out.mkdir(exist_ok=False);(out/'saves').mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def status(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 build=read(stage/'proof.json');assert build['status']=='SUCCESS_EFFECTS_REAL_ENGINE_CANDIDATE_BUILD_PASS'
 exe=stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256']
 oracle=w/'original-success-effects-nov10';proof=read(oracle/'proof.json');fixture=oracle/'fixture.bin';assert sha(fixture)==proof['fixture_sha256']
 raw=fixture.read_bytes();assert raw[:8]==b'SCFX0001';cases=struct.unpack_from('<I',raw,8)[0];pos=12;expected={}
 for row in range(cases):
  scene,source,counter,repeats=struct.unpack_from('<4I',raw,pos);pos+=16+400
  for repeat in range(repeats):
   after,voices,voiceCounter,voiceHash=struct.unpack_from('<4I',raw,pos);pos+=16+400
   expected[row,repeat]=dict(scene=scene,voices=voices,voice_counter=voiceCounter,voice_hash=voiceHash)
 assert pos==len(raw) and len(expected)==proof['invocations']
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_builder=true\nastronomica_verify_success_effects=true\nastronomica_success_effects_reference='+fixture.as_posix()+'\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
 log=out/'native.log';status('RUNNING_REAL_COMPLETION_CALLBACKS',candidate_exe_sha256=sha(exe),cases=cases)
 with(out/'console.log').open('w')as console:
  result=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT,timeout=900)
 text=log.read_text(errors='replace');assert result.returncode==0 and 'FAIL'not in text and 'Custom effects full native: PASS (300 cases'in text,text[-2500:]
 assert 'Using SDL Audio Driver "wasapi"'in text
 current=None;voices={key:[]for key in expected};passed=set()
 for line in text.splitlines():
  m=re.search(r'Custom effects begin: case(\d+) repeat(\d+) scene(\d+)',line)
  if m:
   current=(int(m[1]),int(m[2]));assert current in expected and int(m[3])==expected[current]['scene'];continue
  m=re.search(r'Custom effects voice: counter(\d+) hash([0-9a-f]+) sound(\d+)',line)
  if m:
   assert current is not None;voices[current].append((int(m[1]),int(m[2],16),int(m[3])));continue
  m=re.search(r'Custom effects result: PASS case(\d+) repeat(\d+)',line)
  if m:
   key=(int(m[1]),int(m[2]));assert key==current and key not in passed;passed.add(key)
 assert passed==set(expected)
 for key,p in expected.items():
  assert len(voices[key])==p['voices']
  if p['voices']:assert voices[key]==[(p['voice_counter'],p['voice_hash'],912)],(key,voices[key],p)
 assert sha(exe)==build['candidate_exe_sha256'] and sha(fixture)==proof['fixture_sha256'] and not list((out/'saves').iterdir())
 seal=read(w/'builder-mask-guard-seal-nov9-status.json');assert sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
 receipt=dict(status='ORIGINAL_COMPLETION_REAL_ENGINE_CALLBACK_EFFECTS_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),build_proof_sha256=sha(stage/'proof.json'),oracle_proof_sha256=sha(oracle/'proof.json'),fixture_sha256=sha(fixture),native_log_sha256=sha(log),cases=cases,invocations=len(expected),actual_blocking_voices=sum(len(v)for v in voices.values()),all100_final_globals_checked_each_invocation=True,voice_boundary_globals_and_counter_match=True,scenes=proof['scenes'],audio_driver='wasapi',muted=True,installed_main_unchanged=True,candidate_installed=False,limits=['Isolated original custom25 kernel invocations with controlled globals/counter, not full natural puzzle histories','Actual native callback, sound playback and counter/flag order; original OS voice call modeled at the comparison boundary','No save-layout change, full-game audiovisual or complete behavior claim'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');status('PASS',proof_sha256=sha(out/'proof.json'));print('Original/native completion effects PASS:',cases,'cases,',len(expected),'invocations')
except Exception:status('FAILED',error=traceback.format_exc());raise
