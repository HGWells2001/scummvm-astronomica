"""Measure original-room music selection on an isolated native engine and unchanged ASVM2 payload."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,shutil,subprocess,sys
w=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--out',required=True);ap.add_argument('--expected',choices=['baseline','fixed'],required=True);a=ap.parse_args();s=w/a.stage;out=w/a.out;out.mkdir(exist_ok=False);(out/'saves').mkdir();exe=s/'bin/scummvm.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fixture=w/'portable-normal-music-native-nov16b/physical-slots/astro-verify.032';fixture_pin=sha(fixture);shutil.copyfile(fixture,out/'saves'/fixture.name)
build=json.loads((s/'proof.json').read_text());pin=build['candidate_exe_sha256'];assert sha(exe)==pin
cfg=out/'test.ini';log=out/'native.log';cfg.write_text('[scummvm]\nconfirm_exit=false\nautosave_period=0\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_exploration_music=true\n',encoding='utf-8')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--logfile='+str(log),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
 subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','exploration-music-'+a.expected,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
text=log.read_text(errors='replace');done=re.search(r'Exploration music observation complete: observed(\d+) total(\d+) stable(\d)',text);assert code==0 and done,text[-2500:]
observed,total,stable=map(int,done.groups());assert total==16 and observed==(16 if a.expected=='fixed'else 0)and stable==1
saved=re.search(r'Exploration music ASVM2 restore: wrote(\d) restored(\d) music(\d)',text);voice=re.search(r'Exploration music narration: exclusive(\d) resumed(\d)',text);assert saved and voice
assert tuple(map(int,saved.groups()))==(1,1,int(a.expected=='fixed'))and tuple(map(int,voice.groups()))==(1,int(a.expected=='fixed'))
assert sha(exe)==pin and sha(fixture)==sha(out/'saves'/fixture.name)==fixture_pin
assert 'Exploration music paused ASVM2: paused1 resumed1'in text
assert 'Exploration music P525 recipient: busyRefused1 preserved1 loaded1 music1'in text
j=dict(status='EXPLORATION_MUSIC_NATIVE_PASS'if a.expected=='fixed'else'EXPLORATION_MUSIC_MISSING_BASELINE_REPRODUCED',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,successful_music_entries=observed,entries=total,asvm2_music_restored=bool(int(saved[3])),narration_exclusive=True,music_resumed_after_voice=bool(int(voice[2])),native_log_sha256=sha(log),native_exited_naturally=True,user_installation_ignored=True,limits=['Eight actual mode1 rooms with both original global60 branches; no complete manual audiovisual playthrough','WASAPI mixer/channel observation with isolated muted configuration; no personal configuration or installation access'])
(out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
