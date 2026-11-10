"""Check original voice ordering with actual original movie and WASAPI playback."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,struct,subprocess,traceback
ap=argparse.ArgumentParser();ap.add_argument('--fixed',action='store_true');args=ap.parse_args();w=Path(__file__).resolve().parent
stage=w/('weather-order-audio-fixed-nov10-stage'if args.fixed else'weather-order-audio-baseline-nov10-stage');out=stage/'native-run';out.mkdir(exist_ok=False);(out/'saves').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,updated_at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n')
try:
 build=read(stage/'proof.json');assert build['status']=='WEATHER_ORDER_AUDIO_REAL_ENGINE_CANDIDATE_BUILD_PASS';exe=stage/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256']
 oracle=w/'weather-order-ui-baseline-nov10';subset=oracle/'fixture.bin';p=read(oracle/'proof.json');assert sha(subset)==p['subset_fixture_sha256']
 original_case=struct.unpack_from('<8I',subset.read_bytes(),12+32);assert original_case==(1,0,0,0,1,0,10,1)
 cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p512=true\nastronomica_verify_weather_order_audio=true\nsavepath='+(out/'saves').as_posix()+'\n')
 env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');log=out/'native.log';state('RUNNING_ACTUAL_WEATHER_MOVIE_AND_VOICE')
 with(out/'console.log').open('w')as console:p_=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT,timeout=90)
 text=log.read_text(errors='replace');assert p_.returncode==0 and 'FAIL'not in text and 'Weather movie audio result: PASS'in text,text[-2000:]
 assert 'Using SDL Audio Driver "wasapi"'in text and 'Weather movie audio before: result1 playing1 source335959'in text
 m=re.findall(r'Weather movie audio voice: id(\d+) result(-?\d+) movie(\d+) decoder(\d+)',text);assert len(m)==1
 sound,result,movie,decoder=map(int,m[0]);assert sound==10 and movie==decoder==1 and result==(1 if args.fixed else 0)
 assert sha(exe)==build['candidate_exe_sha256']and sha(subset)==p['subset_fixture_sha256']and not list((out/'saves').iterdir())
 receipt=dict(status='REAL_WEATHER_MOVIE_AUDIO_ORIGINAL_ORDER_PASS'if args.fixed else'REAL_WEATHER_MOVIE_AUDIO_BASELINE_ORDER_COUNTEREXAMPLE_OBSERVED',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),build_proof_sha256=sha(stage/'proof.json'),original_ui_subset_proof_sha256=sha(oracle/'proof.json'),original_ui_case=list(original_case),native_log_sha256=sha(log),actual_blocking_sound=sound,observed_result_at_voice=result,original_expected_result_at_voice=1,final_result=0,actual_original_movie_active=True,decoder_resumed=True,audio_driver='wasapi',muted=True,candidate_installed=False,limits=['Controlled prior result1 and UI-domain settings, original HYP movie entry and original mode0 command actually executed','Actual decoder and blocking WAV playback; not a complete natural UI history or human audiovisual review'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS',proof_sha256=sha(out/'proof.json'));print(receipt['status'],':voice result',result)
except Exception:state('FAILED',error=traceback.format_exc());raise
