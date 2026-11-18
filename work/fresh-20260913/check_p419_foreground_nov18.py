"""Check original P419 repeated local audio and cleanup through an actual navigation key."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,struct,subprocess,sys,traceback
w=Path(__file__).resolve().parent;stage=w/'p419-foreground-observer-nov18-stage';out=w/'p419-foreground-native-nov18';out.mkdir(exist_ok=False);(out/'saves').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n')
try:
    build=read(stage/'proof.json');assert build['status']=='P419_FOREGROUND_OBSERVER_BUILD_PASS';exe=stage/'bin/scummvm.exe';pin=build['candidate_exe_sha256'];assert sha(exe)==pin
    release=read(w/'p513-control-music-seal-nov17.json');assert sha(w/'build/Releasex64/scummvm.exe')==release['exe_sha256']==build['base_exe_sha256']
    from p419_foreground_source_nov18 import observe
    source=w.parents[1]/'outputs/astronomica-cleanroom/engine/astronomica';cpp,header=observe((source/'astronomica.cpp').read_text(),(source/'astronomica.h').read_text())
    assert cpp==(stage/'source/engines/astronomica/astronomica.cpp').read_text() and header==(stage/'source/engines/astronomica/astronomica.h').read_text()
    original=Path('D:/astro/PLACES/P419/MEGAFILE.HYP');raw=original.read_bytes();scene=next(x for x in read(w/'original-branches-nov6/inventory.json')['scenes']if x['scene']==419);assert sha(original)==scene['sha256']
    commands={16231:(23,26,2,0,0,0,0),16263:(31,1,0,1,0,0,0),16295:(9,2),16307:(41,0)}
    for offset,values in commands.items():assert struct.unpack_from('<'+'i'*len(values),raw,offset)==values
    assert struct.unpack_from('<i',raw,16307+8)[0]==100 and struct.unpack_from('<i',raw,4)[0]==358
    cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\nmusic_volume=128\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_start_place=103\nastronomica_observe_p419_foreground=true\n');log=out/'native.log'
    env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');state('RUNNING_ORIGINAL_P419_FOREGROUND')
    with(out/'console.log').open('w')as console:
        child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
        try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','original-p419-repeated-foreground-and-navigation-nov18','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
        finally:code=child.wait()
    text=log.read_text(errors='replace');repeated=re.search(r'P419 foreground repeated: local1 starts(\d+) foreground1 music0 resultPASS',text)
    assert code==0 and repeated and int(repeated[1])>=2 and 'P419 foreground complete: passed3 total3'in text,text[-2500:]
    assert 'P419 foreground boundary: phase0 place419 local0 starts0 advancing1 loop902 resultPASS'in text
    assert re.search(r'P419 foreground boundary: phase2 place358 local-?\d+ starts\d+ advancing1 loop902 resultPASS',text)
    assert 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.') and not list((out/'saves').iterdir())
    assert sha(exe)==pin and sha(w/'build/Releasex64/scummvm.exe')==release['exe_sha256']
    receipt=dict(status='ORIGINAL_P419_REPEATED_FOREGROUND_NAVIGATION_PASS',at=datetime.now(timezone.utc).isoformat(),observer_exe_sha256=pin,canonical_exe_sha256=release['exe_sha256'],build_proof_sha256=sha(stage/'proof.json'),native_log_sha256=sha(log),original_scene_sha256=sha(original),original_s1_sha256=sha(Path('D:/astro/PLACES/P419/S1.WAV')),global52_cases=[0,1],observed_s1_dispatches_in_repeated_case=int(repeated[1]),actual_navigation_destination=358,music_advancing_after_navigation=True,canonical_engine_changed=False,normal_frame_pump_preserved=True,native_exited_naturally=True,mute=True,limits=['S1 is left unclassified as speech or effect; no acoustic recording','Original entry0 explicitly self-calls with delay100; no one-shot expectation','Controlled global52 fixtures do not prove natural reachability or exact original Win16 scheduling','The check validates bounded repeated dispatch and cleanup; not all P419 controls or a new audio fix'])
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS');print(receipt['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
