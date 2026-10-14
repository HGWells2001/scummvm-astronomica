"""Target native legacy import; fixture files stay outside the original game."""
from pathlib import Path
import os,subprocess,hashlib,json,shutil
base=Path('work/fresh-20260913').resolve();directory=base/'legacy-save-regression';directory.mkdir(exist_ok=True)
(directory/'missing').mkdir(exist_ok=True);(directory/'invalid').mkdir(exist_ok=True);(directory/'invalid/GAMESTAT').write_text('103\n7\n0\n')
resource=directory/'PLACES/P103/MEGAFILE.HYP';resource.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile('D:/astro/PLACES/P103/MEGAFILE.HYP',resource)
fixture=directory/'GAMESTAT';fixture.write_text('103\n7\n'+'0\n'*99+'1234\n');before=hashlib.sha256(fixture.read_bytes()).hexdigest()
cfg=base/'verify-legacy.ini';cfg.write_text('[scummvm]\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_legacy=true\nastronomica_verify_legacy_directory='+directory.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy');env.pop('SDL_AUDIODRIVER',None)
cmd=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--logfile='+str(base/'legacy.log'),'--extrapath='+str(base/'fonts'),'--savepath='+str(directory),'--debuglevel=1','astro-verify']
p=subprocess.run(cmd,env=env,cwd=base,capture_output=True,text=True,timeout=180);(base/'legacy-console.log').write_text(p.stdout+p.stderr);print('exit',p.returncode);print((p.stdout+p.stderr)[-1300:])
assert p.returncode==0
log=(base/'legacy.log').read_text();assert 'legacy save verification: PASS' in log and 'FAIL' not in log
assert hashlib.sha256(fixture.read_bytes()).hexdigest()==before
(base/'legacy-file-proof.json').write_text(json.dumps(dict(fixture_sha256=before,unchanged_after_import=True),indent=2))
