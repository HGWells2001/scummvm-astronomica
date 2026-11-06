"""Observe real startup admission with animation enabled/disabled in four original scenes."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,os,re,subprocess,time,traceback
w=Path(__file__).resolve().parent;out=w/'original-entry-admission-nov6';out.mkdir(exist_ok=False)
exe=w/'opening-rgb-nov6-stage/complete-build/bin/scummvm.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin=sha(exe);expected={514:(2,0),516:(2,1),518:(3,2),522:(11,8)}
def state(value,**kw):(out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
def run(place,animation):
    folder=out/('P%d-animation-%s'%(place,animation));folder.mkdir();(folder/'saves').mkdir()
    original=Path('D:/astro/PLACES/P%d/MEGAFILE.HYP'%place);original_pin=sha(original)
    cfg=folder/'start.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=C\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=true\nastronomica_animation='+str(animation).lower()+'\nastronomica_start_place='+str(place)+'\nsavepath='+(folder/'saves').as_posix()+'\n')
    env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
    log=folder/'native.log';match=None;child=None
    with(folder/'console.log').open('w')as console:
        child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+180
            while child.poll()is None and time.monotonic()<deadline:
                text=log.read_text(errors='replace')if log.exists()else''
                match=re.search(r'Astronomica P%d entry scripts: (\d+) queued, (\d+) skipped'%place,text)
                if match:break
                time.sleep(.1)
            assert match,'No startup admission observation'
            admitted=expected[place][0 if animation else 1];total=expected[place][0]
            assert tuple(map(int,match.groups()))==(admitted,total-admitted)
            assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
        finally:
            # Explicit bounded observation: no complete gameplay run/clean exit is claimed.
            if child.poll()is None:child.terminate()
            child.wait(timeout=15)
    assert sha(original)==original_pin and sha(exe)==pin and not list((folder/'saves').iterdir())
    result=dict(scene=place,animation=animation,admitted=admitted,skipped=total-admitted,total=total,pid=child.pid,original_file_sha256=original_pin,log_sha256=sha(log),config_sha256=sha(cfg),observation_complete=True,process_stopped_after_observation=True,full_script_execution_verified=False)
    (folder/'proof.json').write_text(json.dumps(result,indent=2)+'\n');return result
try:
    state('RUNNING_EIGHT_BOUNDED_STARTUP_OBSERVATIONS');cases=[]
    with ThreadPoolExecutor(max_workers=2)as pool:
        for f in as_completed([pool.submit(run,p,flag)for p in expected for flag in(False,True)]):
            cases.append(f.result());state('RUNNING_EIGHT_BOUNDED_STARTUP_OBSERVATIONS',completed=len(cases))
    live=sum(c['admitted']for c in cases if c['animation']);static=sum(c['admitted']for c in cases if not c['animation'])
    assert live==18 and static==11 and len(cases)==8
    result=dict(status='ORIGINAL_SEVEN_STATIC_REJECT_COHORT_ADMISSION_MATRIX_PASS',candidate_exe_sha256=pin,completed_at=datetime.now(timezone.utc).isoformat(),cases=cases,animation_enabled_admitted=live,animation_disabled_admitted=static,configuration_dependent_rejects=7,meaning='The four cohorts accounting for all seven historical static rejects are admitted with the actual animation-enabled startup configuration. Counts are admission, not proof of every branch executing.',full_game_or_A03_complete=False,limits=['Owned native processes intentionally stopped after exact startup queue observation','No fresh end-to-end original Windows executable run','Native custom callbacks and alternative outcomes remain separate execution work','All original inputs and personal saves unchanged'])
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');state('PASS',proof_sha256=sha(out/'proof.json'))
except Exception:state('FAILED',error=traceback.format_exc());raise
