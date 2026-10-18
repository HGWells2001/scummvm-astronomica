"""Check native music/effect routing with the real mixer and original WAVs."""
from pathlib import Path
import hashlib,json,os,subprocess
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-audio-channels.ini'
cfg.write_text('[scummvm]\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_audio_channels=true\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
files=[Path(f'D:/astro/PLACES/P{scene}/S{sound}.WAV') for scene in (505,508,519,524,526,528) for sound in (0,1)]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
p=subprocess.run([str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--logfile='+str(base/'audio-channels.log'),'--extrapath='+str(base/'fonts'),'--savepath='+str(base),'--debuglevel=1','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=180)
(base/'audio-channels-console.log').write_text(p.stdout+p.stderr);log=(base/'audio-channels.log').read_text()
print('Audio channel exit',p.returncode);print(log[-1000:])
assert p.returncode==0 and 'FAIL' not in log and 'Log closed successfully' in log
assert 'audio channel verification: PASS (6 muted music loops, 6 foreground replacements, controls restored)' in log
assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(base/'audio-channels-proof.json').write_text(json.dumps(dict(status='PASS',date='2026-10-18',original_wav_sha256=before,unchanged=True),indent=2))
