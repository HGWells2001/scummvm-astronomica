"""Run the existing general native verifier on the physical candidate, in a fresh savepath."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,time,traceback
w=Path(__file__).resolve().parent;root=w.parents[1];s=w/'opening-rgb-nov6-stage'
out=w/'opening-rgb-general-nov6';out.mkdir(exist_ok=False)
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def state(value,**fields):
    (out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),
        updated_at=datetime.now(timezone.utc).isoformat(),**fields),indent=2)+'\n')
try:
    proof=s/'provenance.json';p=json.loads(proof.read_text())
    assert p['status']=='OPENING_RGB_FORMAT_ONLY_SOURCE_DELTA'
    exe=s/'complete-build/bin/scummvm.exe';expected=d(exe)
    assert p['stage_sha256']=={n:d(s/n)for n in p['stage_sha256']}
    slots=out/'slots';slots.mkdir()
    fixtures={}
    for suffix in ('098','099'):
        name='astro-verify.'+suffix;source=w/'p525-physical-nov3c-stage/frozen-fixtures'/name
        fixtures[name]=d(source);shutil.copyfile(source,slots/name)
    config=out/'general.ini'
    config.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify=true\nsavepath='+slots.as_posix()+'\n')
    env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='wasapi'
    log=out/'general-native.log';state('RUNNING_GENERAL_NATIVE_WASAPI',candidate_exe_sha256=expected)
    with(out/'console.log').open('w')as console:
        child=subprocess.Popen([str(exe),'--config='+str(config),'--extrapath='+str(w/'fonts'),
            '--savepath='+str(slots),'--logfile='+str(log),'--debuglevel=1','astro-verify'],
            cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
        until=time.monotonic()+14400
        try:
            while child.poll() is None:
                text=log.read_text(errors='replace') if log.exists() else ''
                if 'FAIL'in text or time.monotonic()>until:
                    child.terminate();break
                time.sleep(1)
            code=child.wait(timeout=15)
        finally:
            if child.poll() is None:child.kill();child.wait(timeout=15)
    text=log.read_text()
    assert code==0 and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-3000:]
    assert 'Astronomica script verification: PASS'in text and 'Astronomica lifecycle verification: PASS'in text
    assert 'Using SDL Audio Driver "wasapi"'in text
    assert d(exe)==expected and p['stage_sha256']=={n:d(s/n)for n in p['stage_sha256']}
    assert fixtures=={n:d(slots/n)for n in fixtures}
    receipt=dict(status='OPENING_RGB_GENERAL_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),
        candidate_exe_sha256=expected,stage_sha256=p['stage_sha256'],compile_source_scope_proof_sha256=d(proof),
        log_sha256=d(log),config_sha256=d(config),audio_driver='wasapi',mute=True,
        frozen_aliases_unchanged=fixtures,main_modified=False,public_support=False,
        limitations=['Existing general verifier only; no genuine all-version fixture compatibility claim',
            'No manual whole-game audiovisual or release claim'])
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'))
except Exception:state('FAILED',error=traceback.format_exc());raise
