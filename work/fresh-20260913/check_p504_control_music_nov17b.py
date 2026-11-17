"""Compare actual original speed-button playback against the same owned Music stream."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,subprocess,sys
w=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--out',required=True);ap.add_argument('--expected',choices=['baseline','fixed'],required=True);ap.add_argument('--windows',action='store_true');ap.add_argument('--installed',action='store_true');a=ap.parse_args()
s=w/a.stage;out=w/a.out;out.mkdir(exist_ok=False);saves=out/'saves';saves.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((s/'proof.json').read_text());exe=w/'build/Releasex64/scummvm.exe' if a.installed else s/'bin/scummvm.exe';pin=build['candidate_exe_sha256'];assert sha(exe)==pin
cfg=out/'test.ini';cfg.write_text('[scummvm]\nconfirm_exit=false\nautosave_period=0\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_p504_control_music=true\n');log=out/'native.log'
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='windows'if a.windows else'dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(saves),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
 try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','p504-control-music-'+a.expected,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
 finally:code=child.wait()
text=log.read_text(errors='replace');m=re.search(r'P504 speed music observation: loaded(\d) started(\d) hit(\d) sound(\d) setting(-?\d+) effect(\d) music(\d) starts(\d+) idle(\d) blocked(\d)',text);assert code==0 and m,text[-2400:]
values=tuple(map(int,m.groups()));expected=int(a.expected=='fixed');assert values==(1,1,1,1,1,expected,expected,1,0,0),values
assert 'P504 speed narration foreground: 1'in text and 'Using SDL Audio Driver "wasapi"'in text and text.rstrip().endswith('--- Log closed successfully.')
assert sha(exe)==pin and not list(saves.iterdir())
j=dict(status='P504_CONTROL_MUSIC_NATIVE_PASS'if expected else'P504_CONTROL_MUSIC_INTERRUPTION_REPRODUCED',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,values=dict(zip(('loaded','started','hit','sound','setting','effect','music','starts','idle','blocked'),values)),native_log_sha256=sha(log),windows_backend=a.windows,installed_workspace=a.installed,native_exited_naturally=True,user_installation_ignored=True,limits=['Actual original sprite10 speed increment from0to1 while localS0 Music is active; exact same Music handle','Foreground narration boundary checked; no complete human audio or all-effect catalogue claim'])
(out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
