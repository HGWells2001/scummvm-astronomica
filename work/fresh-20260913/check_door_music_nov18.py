"""Compare actual P27/P85 door clicks before/after shared-effect classification."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,subprocess,sys
w=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--out',required=True);ap.add_argument('--expected',choices=['baseline','fixed'],required=True);ap.add_argument('--windows',action='store_true');ap.add_argument('--installed',action='store_true');a=ap.parse_args()
s=w/a.stage;out=w/a.out;out.mkdir(exist_ok=False);(out/'saves').mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((s/'proof.json').read_text());exe=w/'build/Releasex64/scummvm.exe'if a.installed else s/'bin/scummvm.exe';pin=build['candidate_exe_sha256'];assert sha(exe)==pin
cfg=out/'test.ini';cfg.write_text('[scummvm]\nconfirm_exit=false\nautosave_period=0\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_door_music=true\n');log=out/'native.log'
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='windows'if a.windows else'dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
    try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','shared-door-music-'+a.expected,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
    finally:code=child.wait()
text=log.read_text(errors='replace');rows=[tuple(map(int,x))for x in re.findall(r'Door Music observation: place(\d+) loaded(\d) started(\d) hit(\d) heard(\d) state(-?\d+) overlap(\d) guard(\d) music(\d) advancing(\d) starts(\d+)',text)]
expected=int(a.expected=='fixed');assert code==0 and len(rows)==2,text[-2800:]
assert rows==[(p,1,1,1,1,1,expected,expected,expected,expected,2-expected)for p in (27,85)],rows
assert f'Door Music traversal: destination1 retained{expected}'in text and 'Door Music narration foreground: 1'in text and f'Door Music complete: passed{2*expected} total2'in text
assert text.rstrip().endswith('--- Log closed successfully.') and sha(exe)==pin and not list((out/'saves').iterdir())
receipt=dict(status='SHARED_DOOR_MUSIC_NATIVE_PASS'if expected else'SHARED_DOOR_MUSIC_INTERRUPTION_REPRODUCED',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,build_proof_sha256=sha(s/'proof.json'),original_evidence_sha256=sha(w/'door-effects-original-nov18.json'),native_log_sha256=sha(log),rows=rows,windows_backend=a.windows,installed_workspace=a.installed,native_exited_naturally=True,limits=['Original hit-tested P27 sprite and P85 rectangle with controlled initial globals','Music owner and elapsed-position continuity, plus save/load transient guards and P27 second-click traversal','Narration911 remains foreground; no whole-game speech/effect classification or acoustic recording'])
(out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
