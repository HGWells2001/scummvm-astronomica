"""Headless development verification with a real audio clock, no packaging."""
from pathlib import Path
import os
import subprocess
import sys
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('--place', type=int, choices=[512,525,527,529], default=0)
args = ap.parse_args()

base = Path(__file__).parent.resolve()
cfg = base/'continuous-movies.ini'
log = base/('continuous-movies'+(f'-{args.place}' if args.place else '')+'.log')
cfg.write_text('[scummvm]\nconfirm_exit=false\nmute=true\nenable_unsupported_game_warning=false\ngui_theme=builtin\n[movies]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_verify_movies=true\n'+f'astronomica_movie_place={args.place}\n')
env = {k.upper():v for k,v in os.environ.items()}
env.update(SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='wasapi')
with (base/'continuous-movies-console.log').open('w') as out:
    p = subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--logfile='+str(log),'--debuglevel=1','movies'],cwd=base,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=240)
text = log.read_text(errors='replace')
assert p.returncode == 0 and 'continuous movie verification: PASS' in text
assert 'FAIL' not in text and 'CRITICAL' not in text
print('\n'.join(line for line in text.splitlines() if 'continuous ' in line))
sys.exit(p.returncode)
