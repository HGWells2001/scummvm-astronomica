"""Bounded real WASAPI mixer proof for the compiled paused-start core fix."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,traceback
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage';b=s/'complete-build'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**kw):(b/'gate-status.json').write_text(json.dumps(dict(status=value,pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 p=json.loads((b/'proof.json').read_text());context=json.loads((s/'provenance.json').read_text())
 assert p['candidate_exe_sha256']==d(b/'bin/scummvm.exe') and p['stage_sha256']=={n:d(s/n)for n in p['stage_sha256']}
 assert d(s/'framework-overlay/video/video_decoder.cpp')==context['core_delta_sha256']['video/video_decoder.cpp'] and d(s/'framework-overlay/video/paused_audio_gate.h')==context['core_delta_sha256']['video/paused_audio_gate.h']
 config=b/'gate.ini';log=b/'gate-native.log'
 config.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_p523_paused_gate=true\nsavepath='+b.as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='wasapi'
 state('RUNNING_WASAPI_GATE')
 with(b/'gate-console.log').open('w')as output:
  child=subprocess.Popen([str(b/'bin/scummvm.exe'),'--config='+str(config),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=output,stderr=subprocess.STDOUT)
  try:code=child.wait(timeout=60)
  finally:
   if child.poll()is None:
    child.terminate()
    try:child.wait(timeout=10)
    except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
 text=log.read_text();assert code==0 and'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-4000:]
 assert 'Using SDL Audio Driver "wasapi"'in text
 for marker,count in [('P523 paused gate direct: PASS',2),('P523 paused gate mixer: PASS',2),('P523 paused gate allocation refusal: PASS',3),('P523 paused startup gate verification: PASS',1)]:assert text.count(marker)==count,(marker,text.count(marker))
 assert d(b/'bin/scummvm.exe')==p['candidate_exe_sha256']
 receipt=dict(status='P523_COMPLETE_BUILD_REAL_PAUSED_START_GATE_WASAPI_PASS',candidate_exe_sha256=p['candidate_exe_sha256'],stage_sha256=p['stage_sha256'],framework_delta_sha256={'video/video_decoder.cpp':context['core_delta_sha256']['video/video_decoder.cpp'],'video/paused_audio_gate.h':context['core_delta_sha256']['video/paused_audio_gate.h']},log_sha256=d(log),config_sha256=d(config),source_driver_sha256=d(Path(__file__)),audio_driver='wasapi',muted=True,video_surface='dummy',raw_and_limited_paths=True,nested_channel_pause=True,allocation_refusals=3,direct_prearm_silence_samples=1024,video_decoder_layout_changed=True,clock_import_implemented=True,source_pcm_cursor_captured=False,public_save_support=False,limits=['Gate arithmetic/ownership and actual mixer startup tests; no active P523 media installation','Pre-arm silence may already be buffered; this is zero original-source consumption, not exact backend phase','General and real original-media regressions separate'])
 (b/'gate-proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS',proof_sha256=d(b/'gate-proof.json'));print('Real paused-start gate WASAPI PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
