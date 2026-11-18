"""Run original-route fixtures through real navigation handlers and the frame pump."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys,traceback
w=Path(__file__).resolve().parent;stage=w/'navigation-music-observer-nov18b-stage';out=w/'navigation-music-native-nov18b';out.mkdir(exist_ok=False);(out/'saves').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def state(s,**kw):(out/'status.json').write_text(json.dumps(dict(status=s,at=datetime.now(timezone.utc).isoformat(),driver_pid=os.getpid(),**kw),indent=2)+'\n')
try:
    build=read(stage/'proof.json');assert build['status']=='NAVIGATION_MUSIC_OBSERVER_B_BUILD_PASS'
    exe=stage/'bin/scummvm.exe';pin=build['candidate_exe_sha256'];assert sha(exe)==pin
    original=read(w/'p513-control-music-seal-nov17.json');assert sha(w/'build/Releasex64/scummvm.exe')==build['base_exe_sha256']==original['exe_sha256']
    from navigation_music_source_nov18b import observe
    source=w.parents[1]/'outputs/astronomica-cleanroom/engine/astronomica';cpp,header=observe((source/'astronomica.cpp').read_text(),(source/'astronomica.h').read_text())
    assert cpp==(stage/'source/engines/astronomica/astronomica.cpp').read_text() and header==(stage/'source/engines/astronomica/astronomica.h').read_text()
    cases=read(w/'navigation-music-cases-nov18.json')['cases'];assert len(cases)==1538
    cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\nmusic_volume=128\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_start_place=103\nastronomica_observe_navigation_music=true\n');log=out/'native.log'
    env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi');state('RUNNING_NAVIGATION_MUSIC',candidate_exe_sha256=pin)
    with(out/'console.log').open('w')as console:
        child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
        try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','original-navigation-with-active-music-nov18','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
        finally:code=child.wait()
    text=log.read_text(errors='replace')
    rows=[tuple(map(int,x))for x in re.findall(r'Navigation Music row: case(\d+) route(\d+) P(\d+) dir(\d+) requested(\d+) permit(\d+) pad(\d+) actual(\d+) after(\d+) loop(-?\d+) active(\d) advancing(\d) owner(\d) resultPASS',text)]
    assert code==0 and len(rows)==1538 and 'Navigation Music complete: passed1538 total1538'in text,text[-3500:]
    for i,(row,c)in enumerate(zip(rows,cases)):
        assert row[:10]==(i,c['route_index'],c['source'],c['direction'],c['requested'],c['permit'],c['keypad'],c['destination'],c['permit_after'],(c['destination_loop'] or -1))
    assert row[10]==bool(c['destination_loop']) and row[12]==1
        if c['destination_loop']:assert row[11]==1
    assert 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.') and not list((out/'saves').iterdir())
    assert sha(exe)==pin and sha(w/'build/Releasex64/scummvm.exe')==original['exe_sha256']
    receipt=dict(status='ORIGINAL_NAVIGATION_ACTIVE_MUSIC_PASS',at=datetime.now(timezone.utc).isoformat(),observer_exe_sha256=pin,canonical_exe_sha256=original['exe_sha256'],observer_build_proof_sha256=sha(stage/'proof.json'),cases_sha256=sha(w/'navigation-music-cases-nov18.json'),native_log_sha256=sha(log),literal_navigation_routes=760,source_rooms_with_routes=305,mode1_room_without_nav_routes=31,keyboard_variants=2,extra_permitted_gate_fixtures=9,native_cases=1538,canonical_engine_changed=False,normal_frame_pump_preserved=True,native_exited_naturally=True,mute=True,audio_driver='wasapi',limits=['Controlled direct source loads and actual arrow/keypad handlers, not proof that every route is reachable from a new game','Global57 controlled at the navigation boundary; no exhaustive global-state or sprite-click matrix','Native active/advancing stream and same-zone ownership checks, not acoustic recordings','Denied gate destinations checked before the full P429 movie completes; native process exits naturally'])
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS');print(receipt['status'])
except Exception:state('FAILED',error=traceback.format_exc());raise
