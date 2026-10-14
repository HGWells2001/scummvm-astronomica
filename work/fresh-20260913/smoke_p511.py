from pathlib import Path
import subprocess,os,time
out=Path('outputs/astronomica-cleanroom').resolve();base=Path('work/fresh-20260913').resolve()
env=dict(os.environ);env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
log=base/'p511-launch.log'
if log.exists(): log.unlink()
with (base/'p511-launch-console.log').open('w') as console:
 p=subprocess.Popen([str(out/'bin/scummvm.exe'),'--config='+str(out/'bin/astronomica.ini'),'--logfile='+str(log),'--debuglevel=1','astronomica-p511'],cwd=out/'bin',env=env,stdout=console,stderr=console)
 try:
  deadline=time.monotonic()+60
  while p.poll() is None and time.monotonic()<deadline:
   if log.exists() and 'P511 loop: S0.WAV' in log.read_text(errors='replace'): break
   time.sleep(0.2)
  if p.poll() is None: p.terminate();p.wait(timeout=5)
 except subprocess.TimeoutExpired:
  p.terminate();p.wait(timeout=5)
text=log.read_text(errors='replace');print(text[-1800:])
assert 'resource explorer: P511' in text
assert 'P511 introduction: S302.WAV' in text
assert 'P511 loop: S0.WAV' in text
assert 'P511 entry scripts: 5 queued, 0 skipped' in text
assert 'unsupported scripts skipped' not in text
assert 'CRITICAL' not in text
print('P511 packaged launcher startup: PASS')
