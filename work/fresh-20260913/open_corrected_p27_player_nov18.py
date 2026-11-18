"""Open a normal interactive P27 player for optional listening, without touching user settings."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
w=Path(__file__).resolve().parent;out=w/'door-music-player-nov18';out.mkdir(exist_ok=False);(out/'saves').mkdir();s=w/'door-music-candidate-nov18b-stage';build=json.loads((s/'proof.json').read_text());exe=s/'bin/scummvm.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(exe)==build['candidate_exe_sha256'] and json.loads((w/'door-music-windows-native-nov18/proof.json').read_text())['candidate_exe_sha256']==sha(exe)
cfg=out/'player.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=false\nmusic_volume=128\nsfx_volume=192\n[astronomica]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_start_place=27\n',encoding='utf-8')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='windows',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as console:
    child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--logfile='+str(out/'native.log'),'--extrapath='+str(w/'fonts'),'--debuglevel=1','astronomica'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
# This is a user-controlled player, not an unattended qualification suite.
# The user's authorized final shutdown may close it with other applications.
receipt=dict(status='NORMAL_CORRECTED_P27_PLAYER_OPENED',at=datetime.now(timezone.utc).isoformat(),pid=child.pid,exe_sha256=sha(exe),configuration_sha256=sha(cfg),diagnostic_flags_absent=True,isolated_settings_and_saves=True,manual_player_not_a_suite=True)
(out/'launch.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(receipt['status'],child.pid)
