from pathlib import Path
import subprocess,os,sys
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-p523.ini'
cfg.write_text('[scummvm]\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_p523=true\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
cmd=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--logfile='+str(base/'p523.log'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base),'--debuglevel=1','astro-verify']
p=subprocess.run(cmd,env=env,cwd=base,capture_output=True,text=True,timeout=420)
(base/'p523-console.log').write_text(p.stdout+p.stderr);print('exit',p.returncode);print((p.stdout+p.stderr)[-1400:]);sys.exit(p.returncode)





