"""Development-only real-time playback check; no distributable launcher."""
from pathlib import Path
import subprocess,os,time,re
base=Path(__file__).parent.resolve();cfg=base/'movie-check.ini';log=base/'movie-check.log'
cfg.write_text('[scummvm]\nconfirm_exit=false\nmute=true\nenable_unsupported_game_warning=false\ngui_theme=builtin\n[movie-check]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=520\nastronomica_entry_scripts=true\nastronomica_sprite_input=true\nastronomica_animation=true\nastronomica_audio=true\n')
if log.exists():log.unlink()
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER=os.environ.get('ASTRO_TEST_AUDIO_DRIVER','wasapi'))
with (base/'movie-check-console.log').open('w') as console:
 p=subprocess.Popen([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--logfile='+str(log),'--debuglevel=1','movie-check'],cwd=base,env=env,stdout=console,stderr=console)
 try:
  deadline=time.monotonic()+55
  while p.poll() is None and time.monotonic()<deadline:
   if log.exists() and 'resource explorer: P537' in log.read_text(errors='replace'):break
   time.sleep(.2)
 finally:
  if p.poll() is None:p.terminate();p.wait(timeout=5)
text=log.read_text(errors='replace')
assert 'P520 movie started at 240,130' in text
assert 'resource explorer: P537' in text
m=re.search(r'movie segment finished: (\d+) frames drawn',text)
assert m and int(m[1])>100
assert 'CRITICAL' not in text
print('Real-time P520 playback: PASS;',m[1],'frames; destination P537')
