"""Run the existing general native verifier on the physical candidate, in a fresh savepath."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;root=w.parents[1];s=w/'double-click-candidate-nov12-stage'
out=w/'double-click-general-nov12';out.mkdir(exist_ok=False)
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**fields):
    (out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),
        updated_at=datetime.now(timezone.utc).isoformat(),**fields),indent=2)+'\n')
try:
    state('WAITING_TARGETED_CODEC_GATE')
    codec=w/'double-click-native-nov12'
    deadline=time.monotonic()+1200
    while not(codec/'proof.json').exists():
        if(codec/'status.json').exists():assert json.loads((codec/'status.json').read_text())['status']!='FAILED'
        assert time.monotonic()<deadline
        time.sleep(1)
    assert json.loads((codec/'proof.json').read_text())['status']=='DOUBLE_CLICK_REAL_POLLS_NATIVE_PASS'
    proof=s/'proof.json';p=json.loads(proof.read_text())
    assert p['status']=='DOUBLE_CLICK_REAL_ENGINE_BUILD_PASS'
    exe=s/'bin/scummvm.exe';expected=d(exe)
    assert p['candidate_engine_sha256']=={n:d(s/'source/engines/astronomica'/n)for n in p['candidate_engine_sha256']}
    slots=out/'slots';slots.mkdir()
    fixtures={}
    for suffix in ('098','099'):
        name='astro-verify.'+suffix;source=w/'opening-rgb-general-nov6/slots'/name
        fixtures[name]=d(source);shutil.copyfile(source,slots/name)
    config=out/'general.ini'
    config.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify=true\nsavepath='+slots.as_posix()+'\n')
    env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='wasapi'
    log=out/'general-native.log';state('RUNNING_GENERAL_NATIVE_WASAPI',candidate_exe_sha256=expected)
    with(out/'console.log').open('w')as console:
        child=subprocess.Popen([str(exe),'--config='+str(config),'--extrapath='+str(w/'fonts'),
            '--savepath='+str(slots),'--logfile='+str(log),'--debuglevel=1','astro-verify'],
            cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
        subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','double-click-full-general-engine','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
        began=time.monotonic();reported=False
        while child.poll() is None:
            text=log.read_text(errors='replace') if log.exists() else ''
            if not reported and ('FAIL'in text or time.monotonic()-began>14400):
                state('WAITING_FOR_NATURAL_NATIVE_EXIT',native_pid=child.pid,failure_marker_seen='FAIL'in text,forced_termination=False);reported=True
            time.sleep(1)
        code=child.wait()
    text=log.read_text()
    assert code==0 and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-3000:]
    assert 'Astronomica script verification: PASS'in text and 'Astronomica lifecycle verification: PASS'in text
    assert 'Using SDL Audio Driver "wasapi"'in text
    assert d(exe)==expected and p['candidate_engine_sha256']=={n:d(s/'source/engines/astronomica'/n)for n in p['candidate_engine_sha256']}
    assert fixtures=={n:d(slots/n)for n in fixtures}
    receipt=dict(status='DOUBLE_CLICK_GENERAL_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),
        candidate_exe_sha256=expected,stage_sha256=p['candidate_engine_sha256'],compile_source_scope_proof_sha256=d(proof),
        log_sha256=d(log),config_sha256=d(config),audio_driver='wasapi',mute=True,
        frozen_aliases_unchanged=fixtures,main_modified=False,public_support=False,native_exited_naturally=True,forced_termination=False,
        diagnostic_feature_keys_absent=True,limitations=['Existing general verifier only; no genuine all-version fixture compatibility claim',
            'No manual whole-game audiovisual or release claim'])
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'))
except Exception:state('FAILED',error=traceback.format_exc());raise
