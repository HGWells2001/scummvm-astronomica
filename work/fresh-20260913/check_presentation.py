"""Original full-frame presentation and optional debug-strip regression."""
from pathlib import Path
import os,subprocess
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-presentation.ini'
cfg.write_text('[scummvm]\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_presentation=true\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--logfile='+str(base/'presentation.log'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base),'--debuglevel=1','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
(base/'presentation-console.log').write_text(p.stdout+p.stderr);log=(base/'presentation.log').read_text()
print('Presentation exit',p.returncode);print(log[-650:])
assert p.returncode==0 and 'FAIL' not in log and 'presentation verification: PASS' in log and 'Log closed successfully' in log
assert 'full-height presentation: PASS (12 scenes, 855 original P528 pixels, optional strip and recovery)' in log
