"""Compare missing close-up/special-menu tracks and compatible P1 save admission on native code."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,shutil,subprocess,sys
w=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--out',required=True);ap.add_argument('--expected',choices=['baseline','fixed'],required=True);ap.add_argument('--windows',action='store_true');a=ap.parse_args();s=w/a.stage;out=w/a.out;out.mkdir(exist_ok=False);(out/'saves').mkdir();exe=s/'bin/scummvm.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((s/'proof.json').read_text());pin=build['candidate_exe_sha256'];assert sha(exe)==pin
fixture=w/'portable-normal-music-native-nov16b/physical-slots/astro-verify.032';fixture_pin=sha(fixture);shutil.copyfile(fixture,out/'saves'/fixture.name)
cfg=out/'test.ini';log=out/'native.log';cfg.write_text('[scummvm]\nconfirm_exit=false\nautosave_period=0\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_scene_music=true\n',encoding='utf-8')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='windows'if a.windows else'dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--logfile='+str(log),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
 subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','scene-music-'+a.expected,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
text=log.read_text(errors='replace');done=re.search(r'Scene music observation complete: matched(\d+) total(\d+)',text);assert code==0 and done,text[-2300:]
matched,total=map(int,done.groups());assert total==18 and matched==(18 if a.expected=='fixed'else 6)
assert 'Scene music P1 recipient: current1 legacy1 narrationRefused1'in text
assert sha(exe)==pin and sha(fixture)==sha(out/'saves'/fixture.name)==fixture_pin
j=dict(status='SCENE_MUSIC_NATIVE_PASS'if a.expected=='fixed'else'SCENE_MUSIC_DEFAULTS_BASELINE_MISMATCH_REPRODUCED',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,matched=matched,total=total,original_fixture_sha256=fixture_pin,current_and_legacy_menu_music_recipients=True,narration_rejected_without_mutation=True,native_log_sha256=sha(log),native_exited_naturally=True,user_installation_ignored=True,windows_backend=a.windows,limits=['Nine actual scenes at two state values; mode3 close-ups and specialmode0 cases represented','Native channel/type selection and real older-save admission,not a manual full audiovisual certificate'])
(out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'],matched,total)
