"""Observe genuine ASVM30 loading and feedback overlap without changing the fixture."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,shutil,subprocess,sys
w=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--stage',default='restored-music-owner-nov17-stage');ap.add_argument('--out',default='restored-music-owner-native-nov17');ap.add_argument('--expected',choices=['baseline','fixed'],default='baseline');a=ap.parse_args()
s=w/a.stage;out=w/a.out;out.mkdir(exist_ok=False);(out/'saves').mkdir();exe=s/'bin/scummvm.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=w/'portable-normal-music-native-nov16b/physical-slots/astro-verify.032';pin=sha(source);shutil.copyfile(source,out/'saves'/source.name)
cfg=out/'test.ini';log=out/'native.log';cfg.write_text('[scummvm]\nconfirm_exit=false\nautosave_period=0\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nsave_slot=32\nastronomica_verify_restored_music_owner=true\n',encoding='utf-8')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--logfile='+str(log),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
 subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','restored-music-owner-'+a.expected,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
text=log.read_text(errors='replace');assert code==0 and 'Restored music owner observation complete'in text,text[-2500:]
boot=re.search(r'Restored music boot admission: scene(\d+) loaded(\d)',text);owner=re.search(r'Restored music ownership observation: menuLoaded(\d) active(\d) adopted(\d) feedback(\d) retained(\d) scene(\d+)',text);assert boot and owner
fixed=a.expected=='fixed';assert int(boot[2])==int(fixed)and tuple(map(int,owner.groups()))==(1,1,int(fixed),1,int(fixed),525)
assert sha(source)==sha(out/'saves'/source.name)==pin
j=dict(status='RESTORED_MUSIC_OWNER_FIXED_NATIVE_PASS'if fixed else'RESTORED_MUSIC_OWNER_AND_BOOT_REGRESSIONS_REPRODUCED',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),fixture_sha256=pin,boot_scene=int(boot[1]),boot_loaded=bool(int(boot[2])),restored_music_adopted=bool(int(owner[3])),feedback_retains_restored_music=bool(int(owner[5])),native_log_sha256=sha(log),native_exited_naturally=True,fixture_unchanged=True,limits=['One genuine pre-change P525 ASVM30 active-music file','Boot and post-menu load tested separately; not all format/source combinations'])
(out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
