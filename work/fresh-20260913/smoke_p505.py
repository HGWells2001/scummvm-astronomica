from pathlib import Path
import subprocess,os
out=Path('outputs/astronomica-cleanroom').resolve();base=Path('work/fresh-20260913').resolve()
env=dict(os.environ);env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
log=base/'p505-launch.log'
if log.exists(): log.unlink()
with (base/'p505-launch-console.log').open('w') as console:
 p=subprocess.Popen([str(out/'bin/scummvm.exe'),'--config='+str(out/'bin/astronomica.ini'),'--logfile='+str(log),'--debuglevel=1','astronomica-p505'],cwd=out/'bin',env=env,stdout=console,stderr=console)
 try: p.wait(timeout=35)
 except subprocess.TimeoutExpired:
  p.terminate();p.wait(timeout=5)
text=log.read_text(errors='replace');print(text[-1800:])
assert 'resource explorer: P505' in text
assert 'P505 introduction: S300.WAV' in text
assert 'P505 loop: S0.WAV' in text
assert 'P505 entry scripts: 3 queued, 0 skipped' in text
assert 'unsupported scripts skipped' not in text
assert 'CRITICAL' not in text
print('P505 packaged launcher startup: PASS')
