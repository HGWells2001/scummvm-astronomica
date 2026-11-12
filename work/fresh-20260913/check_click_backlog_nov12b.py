"""Compare actual polled mouse batches with a single original-click reference."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback

w = Path(__file__).resolve().parent
out = w / 'click-backlog-native-nov12b'
out.mkdir(exist_ok=False)
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def state(value, **fields):
    (out / 'status.json').write_text(json.dumps(dict(status=value, driver_pid=os.getpid(), updated_at=datetime.now(timezone.utc).isoformat(), **fields), indent=2) + '\n')


try:
    state('WAITING_REAL_ENGINE_BATCH_BUILDS')
    stages = {role:w / ('click-backlog-' + role + '-nov12b-stage') for role in ('baseline','candidate')}
    for role, stage in stages.items():
        while not (stage / 'proof.json').exists():
            error = w / ('click-backlog-' + role + '-nov12b-build.err')
            if error.exists() and error.stat().st_size:
                raise RuntimeError(error.read_text())
            time.sleep(1)
        subprocess.run([sys.executable, str(w / ('audit_click_backlog_' + role + '_nov12b.py')), stage.name, 'click-backlog-' + role + '-source-review-nov12b.json'], check=True)
    resource = Path('D:/astro/PLACES/P536/MEGAFILE.HYP')
    resource_pin = sha(resource)
    rows = []
    for label, role, video in [('baseline-batched-clicks','baseline','dummy'), ('candidate-first-click','candidate','dummy'), ('candidate-first-click-windows','candidate','windows')]:
        expected = role == 'candidate'
        case = out / label
        case.mkdir()
        saves = case / 'saves'
        saves.mkdir()
        cfg = case / 'test.ini'
        cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\nfullscreen=false\ngui_language=en\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=false\nastronomica_animation=false\nastronomica_sprite_input=false\nastronomica_entry_scripts=false\nastronomica_verify_input_backlog=true\nastronomica_input_backlog_expected=' + str(expected).lower() + '\nsavepath=' + saves.as_posix() + '\n')
        env = {key.upper():value for key,value in os.environ.items()}
        env.update(SDL_VIDEODRIVER=video, SDL_AUDIODRIVER='wasapi')
        exe = stages[role] / 'bin/scummvm.exe'
        pin = sha(exe)
        log = case / 'native.log'
        state('RUNNING_POLLED_ORIGINAL_CLICK_BATCHES', profile=label)
        with (case / 'console.log').open('w') as console:
            child = subprocess.Popen([str(exe), '--config=' + str(cfg), '--extrapath=' + str(w / 'fonts'), '--logfile=' + str(log), '--debuglevel=1', 'astro-verify'], cwd=case, env=env, stdout=console, stderr=subprocess.STDOUT)
            try:
                subprocess.run([sys.executable, str(w / 'suite_registry_nov12.py'), 'register', '--pid', str(child.pid), '--label', 'click-backlog-' + label, '--proof', str(out / 'proof.json')], check=True, stdout=subprocess.DEVNULL)
            finally:
                code = child.wait()
        text = log.read_text(errors='replace')
        match = re.search(r'Click backlog native result: PASS \(expected([01]),cases(\d+),differences(\d+)\)', text)
        assert code == 0 and 'FAIL' not in text and match and 'Log closed successfully' in text, text[-4000:]
        assert bool(int(match[1])) == expected and int(match[2]) == 12
        assert 'Click backlog host controls: PASS (keyboard1,menu1,quit1)' in text
        assert int(match[3]) == 0 if expected else int(match[3]) > 0
        assert sha(exe) == pin and not list(saves.iterdir())
        rows.append(dict(profile=label, role=role, video_driver=video, cases=12, differences_from_first_click=int(match[3]), all100_globals_and13locals_checked=True,
            keyboard_menu_and_quit_preserved=True, native_log_sha256=sha(log), native_exe_sha256=pin, native_exited_naturally=True))
    prefs = read(w / 'nov12-user-prefs-pin.json')
    assert sha(Path(prefs['path'])) == prefs['sha256'] and sha(resource) == resource_pin
    receipt = dict(status='CLICK_BACKLOG_POLLED_NATIVE_PASS', completed_at=datetime.now(timezone.utc).isoformat(), candidate_exe_sha256=sha(stages['candidate'] / 'bin/scummvm.exe'),
        baseline_diagnostic_exe_sha256=sha(stages['baseline'] / 'bin/scummvm.exe'), cases=rows, original_hyp_sha256=resource_pin,
        all_processes_exited_naturally=True, user_preferences_unchanged=True,
        limits=['Same extracted real pollPlayerInput and exact optional observer in baseline and candidate;actual native EventSource batches,not direct click-only calls',
            'Twelve original P536 control bursts per profile compare the first-click reference and all100globals/13locals;Windows included',
            'ScummVM keyboard/menu/quit remain processed;original Win16 removal of every window message is adapted to mouse clicks',
            'No original Windows execution or whole-game completion claim;native quit event ends the completed diagnostic normally'])
    (out / 'proof.json').write_text(json.dumps(receipt, indent=2) + '\n')
    state('PASS')
    print(receipt['status'])
except Exception:
    state('FAILED', error=traceback.format_exc())
    raise
