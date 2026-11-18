"""Check shared door overlap, paused mixer clocks and resumption across five Music tracks."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys
w=Path(__file__).resolve().parent;s=w/'door-pause-matrix-observer-nov18b-stage';out=w/'door-pause-matrix-native-nov18b';out.mkdir(exist_ok=False);(out/'saves').mkdir();read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(s/'proof.json');assert build['status']=='DOOR_PAUSE_MATRIX_OBSERVER_B_BUILD_PASS';exe=s/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256'];seal=read(w/'door-music-seal-nov18.json');assert sha(w/'build/Releasex64/scummvm.exe')==build['base_exe_sha256']==seal['exe_sha256']
from door_pause_matrix_source_nov18b import observe
source=w.parents[1]/'outputs/astronomica-cleanroom/engine/astronomica';cpp,header=observe((source/'astronomica.cpp').read_text(),(source/'astronomica.h').read_text());assert cpp==(s/'source/engines/astronomica/astronomica.cpp').read_text()and header==(s/'source/engines/astronomica/astronomica.h').read_text()
cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_door_pause_matrix=true\n',encoding='utf-8');log=out/'native.log'
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
    try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','shared-door-five-tracks-pause-matrix','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
    finally:code=child.wait()
text=log.read_text(errors='replace');rows=[tuple(map(int,x))for x in re.findall(r'Door pause matrix: place(\d+) state(\d) loop(\d+) clip(\d+) loaded(\d) started(\d) overlap(\d) guard(\d) frozen(\d) advancing(\d) narration(\d) resultPASS',text)]
expected=[(p,state,loop,clip)+((1,)*7)for p,state,loop in[(126,0,900),(103,0,902),(219,0,901),(361,0,903),(103,1,908)]for clip in(905,907)]
assert code==0 and rows==expected and 'Door pause matrix complete: passed10 total10'in text and 'FAIL'not in text,text[-3500:]
assert text.rstrip().endswith('--- Log closed successfully.')and not list((out/'saves').iterdir())and sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
proof=dict(status='SHARED_DOOR_PAUSE_MATRIX_NATIVE_PASS',at=datetime.now(timezone.utc).isoformat(),observer_exe_sha256=sha(exe),canonical_exe_sha256=seal['exe_sha256'],build_proof_sha256=sha(s/'proof.json'),native_log_sha256=sha(log),controlled_cases=10,shared_music_tracks=[900,901,902,903,908],door_effects=[905,907],rows=rows,native_exited_naturally=True,production_engine_unchanged=True,limits=['Direct native playback API for two reviewed effects across five actual original ambient tracks;not ten natural door interactions','Actual PauseToken freezes both Music and effect elapsed clocks;same Music owner advances after resume','Transient save/load refused and narration remains foreground;muted WASAPI is not an acoustic recording'])
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(proof['status'])
