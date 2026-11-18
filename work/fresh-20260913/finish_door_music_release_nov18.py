"""Wait for natural native completion, then finish the already-authorized release."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;out=w/'door-music-release-run-nov18';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n',encoding='utf-8')
def run(name,*args):
    state('RUNNING_RELEASE_STEP',step=name)
    with(out/(name+'.log')).open('w')as log:subprocess.run([sys.executable,str(w/name),*args],cwd=w.parents[1],stdout=log,stderr=subprocess.STDOUT,check=True)
try:
    state('WAITING_GENERAL_NATURAL_COMPLETION');gate=w/'door-music-general-nov18';deadline=time.monotonic()+14400
    while not(gate/'proof.json').exists():
        assert time.monotonic()<deadline,'Leave native suites untouched'
        if(gate/'status.json').exists():assert read(gate/'status.json')['status']!='FAILED'
        time.sleep(1)
    proof=read(gate/'proof.json');assert proof['status']=='DOOR_MUSIC_GENERAL_NATIVE_PASS'and proof['native_exited_naturally']and proof['candidate_exe_sha256']==read(w/'door-music-candidate-nov18b-stage/proof.json')['candidate_exe_sha256']
    run('promote_door_music_nov18.py')
    run('check_door_music_nov18.py','--stage','door-music-candidate-nov18b-stage','--out','door-music-installed-native-nov18','--expected','fixed','--windows','--installed')
    run('check_door_music_genuine_nov18.py','--installed')
    run('prepare_door_music_publication_nov18.py')
    run('check_door_music_publication_install_nov18.py')
    run('publish_door_music_nov18.py')
    run('seal_door_music_nov18.py')
    seal=read(w/'door-music-seal-nov18.json');assert seal['status']=='DOOR_MUSIC_PUBLISHED_WORKSPACE_SEAL_PASS'
    (out/'proof.json').write_text(json.dumps(dict(status='DOOR_MUSIC_RELEASE_COMPLETE_PASS',at=datetime.now(timezone.utc).isoformat(),seal_sha256=sha(w/'door-music-seal-nov18.json'),commit=seal['published_commit'],forced_termination=False),indent=2)+'\n',encoding='utf-8');state('PASS');print('DOOR_MUSIC_RELEASE_COMPLETE_PASS')
except Exception:state('FAILED',error=traceback.format_exc());raise
