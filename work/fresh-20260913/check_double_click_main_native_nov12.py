"""Exercise the actual installed poll loop with fresh isolated configuration."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys

w = Path(__file__).resolve().parent
out = w / 'double-click-main-native-nov12'
out.mkdir(exist_ok=False)
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
build = read(w / 'double-click-candidate-nov12-stage/proof.json')
exe = w / 'build/Releasex64/scummvm.exe'
assert sha(exe) == build['candidate_exe_sha256']
saves = out / 'saves'
saves.mkdir()
config = out / 'test.ini'
config.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_double_click=true\nastronomica_double_click_expected=true\nsavepath=' + saves.as_posix() + '\n')
env = {key.upper():value for key,value in os.environ.items()}
env.update(SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='wasapi')
log = out / 'native.log'
with (out / 'console.log').open('w') as console:
    child = subprocess.Popen([str(exe), '--config=' + str(config), '--extrapath=' + str(w / 'fonts'), '--logfile=' + str(log), '--debuglevel=1', 'astro-verify'], cwd=out, env=env, stdout=console, stderr=subprocess.STDOUT)
    try:
        subprocess.run([sys.executable, str(w / 'suite_registry_nov12.py'), 'register', '--pid', str(child.pid), '--label', 'double-click-installed-native', '--proof', str(out / 'proof.json')], check=True, stdout=subprocess.DEVNULL)
    finally:
        code = child.wait()
text = log.read_text(errors='replace')
assert code == 0 and 'FAIL' not in text and 'Double click native result: PASS (expected1,cases6,differences0,tripleMatches6,delayed1,separate1)' in text and 'Log closed successfully' in text, text[-3500:]
prefs = read(w / 'nov12-user-prefs-pin.json')
assert sha(Path(prefs['path'])) == prefs['sha256'] and sha(exe) == build['candidate_exe_sha256'] and not list(saves.iterdir())
receipt = dict(status='INSTALLED_DOUBLE_CLICK_NATIVE_PASS', completed_at=datetime.now(timezone.utc).isoformat(), candidate_exe_sha256=sha(exe), native_log_sha256=sha(log),
    first_click_matches=6, global_values_checked=100, local_values_checked=2, third_click_and_delayed_distinct_presses_preserved=True, user_preferences_unchanged=True, native_exited_naturally=True)
(out / 'proof.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'])
