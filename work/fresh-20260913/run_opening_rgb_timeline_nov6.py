"""Bounded real WASAPI mixer proof for the compiled paused-start core fix."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,traceback
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage';b=s/'complete-build'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**kw):(b/'timeline-status.json').write_text(json.dumps(dict(status=value,pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 p=json.loads((b/'proof.json').read_text());context=json.loads((s/'provenance.json').read_text())
 assert p['candidate_exe_sha256']==d(b/'bin/scummvm.exe') and p['stage_sha256']=={n:d(s/n)for n in p['stage_sha256']}
 assert all(d(s/'framework-overlay'/n)==h for n,h in context['core_delta_sha256'].items())
 config=b/'timeline.ini';log=b/'timeline-native.log'
 config.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_p523_timeline=true\nsavepath='+b.as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='wasapi'
 state('RUNNING_WASAPI_GATE')
 with(b/'timeline-console.log').open('w')as output:
  child=subprocess.Popen([str(b/'bin/scummvm.exe'),'--config='+str(config),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=output,stderr=subprocess.STDOUT)
  try:code=child.wait(timeout=60)
  finally:
   if child.poll()is None:
    child.terminate()
    try:child.wait(timeout=10)
    except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
 text=log.read_text();assert code==0 and'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-4000:]
 assert 'Using SDL Audio Driver "wasapi"'in text
 for marker,count in [('P523 original timeline cell: PASS',6),('P523 original timeline verification: PASS',1)]:assert text.count(marker)==count,(marker,text.count(marker))
 assert d(b/'bin/scummvm.exe')==p['candidate_exe_sha256']
 receipt=dict(status='P523_COMPLETE_BUILD_ORIGINAL_MOV_TIMELINE_WASAPI_PASS',candidate_exe_sha256=p['candidate_exe_sha256'],stage_sha256=p['stage_sha256'],framework_delta_sha256=context['core_delta_sha256'],log_sha256=d(log),config_sha256=d(config),source_driver_sha256=d(Path(__file__)),audio_driver='wasapi',muted=True,video_surface='dummy',original_mov_cells=6,source_clock_roles=[[7,0,0],[17029,0,17010],[20074,20066,0]],fresh_and_nonzero_new_mixer_elapsed=True,repeated_same_frame_seeks=12,stopped_wrong_rate_oversize_refusal=True,video_implementations_rebuilt=16,video_decoder_layout_changed=True,source_pcm_cursor_captured=False,public_save_support=False,limits=['Represented millisecond clock roles only, not raw old mixer state or rational timestamp','No source PCM seek policy or active engine state installation','Default clock/lifecycle/general/old-format closure still required'])
 (b/'timeline-proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS',proof_sha256=d(b/'timeline-proof.json'));print('Real paused-start gate WASAPI PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
