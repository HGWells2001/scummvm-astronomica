"""Native save tests use a dedicated directory, never the player's save folder."""
from pathlib import Path
import subprocess,os,sys
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-saves.ini'
savepath=base/'save-regression';savepath.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_saves=true\nastronomica_verify_save_files=true\n')
cfg.write_text(cfg.read_text().replace('[astro-verify]', '[astro-verify]\nsavepath='+savepath.as_posix()))
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
common=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
for name,extra in [('saves',[]),('saves-startup',['--save-slot=1'])]:
 p=subprocess.run(common+['--logfile='+str(base/(name+'.log'))]+extra+['astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
 (base/(name+'-console.log')).write_text(p.stdout+p.stderr)
 print(name,'exit',p.returncode);print((p.stdout+p.stderr)[-1000:])
 assert p.returncode==0
 log=(base/(name+'.log')).read_text();assert 'save verification: PASS' in log and 'FAIL' not in log
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
(base/'saves-list.log').write_text(p.stdout+p.stderr)
assert p.returncode==0 and 'Astronomica regression' in p.stdout,(p.returncode,p.stdout,p.stderr)
print('Native saves, startup restoration and ScummVM save-list metadata: PASS')
