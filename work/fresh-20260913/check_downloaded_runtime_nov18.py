"""Verify actual game startup from the repaired download with isolated settings/saves."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
w=Path(__file__).resolve().parent;out=w/'downloaded-runtime-native-nov18';out.mkdir(exist_ok=False);(out/'saves').mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
repair=json.loads((w/'downloaded-source-runtime-repair-nov18.json').read_text());target=Path(repair['target']);exe=target/'work/fresh-20260913/build/Releasex64/scummvm.exe';assert sha(exe)==repair['exe_sha256']
cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astronomica]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_start_place=1\nastronomica_verify_startup_sequence=true\n',encoding='utf-8');log=out/'native.log'
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--extrapath='+str(target/'work/fresh-20260913/fonts'),'--logfile='+str(log),'--debuglevel=1','astronomica'],cwd=target,env=env,stdout=console,stderr=subprocess.STDOUT)
    try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','repaired-github-source-download-startup-nov18','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
    finally:code=child.wait()
text=log.read_text(errors='replace');assert code==0 and 'Startup sequence: PASS'in text and text.rstrip().endswith('--- Log closed successfully.'),text[-2200:]
assert sha(exe)==repair['exe_sha256'] and not list((out/'saves').iterdir())
receipt=dict(status='REPAIRED_DOWNLOAD_NATIVE_STARTUP_PASS',at=datetime.now(timezone.utc).isoformat(),exe_sha256=sha(exe),repair_proof_sha256=sha(w/'downloaded-source-runtime-repair-nov18.json'),native_log_sha256=sha(log),native_exit_code=code,native_exited_naturally=True,isolated_settings_and_saves=True,limits=['Controlled native startup verification of the repaired download; not another full game regression'])
(out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(receipt['status'])
