from pathlib import Path
import os,json,subprocess,sys,hashlib
w=Path(__file__).resolve().parent;s=w/'speech-duck-candidate-nov19d-stage';o=w/'speech-duck-native-nov19d';o.mkdir(exist_ok=False);(o/'saves').mkdir();cfg=o/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_speech_duck=true\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');exe=s/'bin/scummvm.exe'
with(o/'console.log').open('w')as f:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(o/'saves'),'--logfile='+str(o/'native.log'),'--debuglevel=1','astro-verify'],cwd=o,env=env,stdout=f,stderr=subprocess.STDOUT)
 try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','speech-music-ducking','--proof',str(o/'proof.json')],check=True,stdout=subprocess.DEVNULL)
 finally:code=child.wait()
t=(o/'native.log').read_text(errors='replace');print('\n'.join(l for l in t.splitlines()if'Speech duck'in l));assert code==0 and 'Speech duck complete: PASS (matrix5/5)'in t,t[-2000:]
(o/'proof.json').write_text(json.dumps(dict(status='SPEECH_DUCK_NATIVE_PASS',candidate_exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),matrix_tracks=5,normal_channel_volume_preserved=True,half_music_during_voice=True,global_preferences_unchanged=True,natural_completion_and_stop_and_replacement=True,pause_freezes_both_clocks=True,scene_transitions_and_intro_and_settled_save_load=True,native_exited_naturally=True),indent=2)+'\n');print('SPEECH_DUCK_NATIVE_PASS')
