"""Verify genuine v26 compatibility, P501 v27 and the complete older native chain."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import traceback

root = Path(__file__).resolve().parents[2]
os.chdir(root)
work = root / 'work/fresh-20260913'
exe = work / 'build/Releasex64/scummvm.exe'
snapshot = work / 'verified-checkpoints/p504-2a305b134662'
slot = snapshot / 'frozen-slot25/astro-verify.025'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
state = work / 'p501-regressions-status.json'

def journal(status, **fields):
    pending = state.with_suffix('.tmp')
    pending.write_text(json.dumps(dict(status=status, exe_sha256=expected, **fields), indent=2))
    pending.replace(state)

try:
    journal('RUNNING', step='genuine_frozen_v26')
    frozen = json.loads((snapshot / 'frozen-slot25.json').read_text())
    assert frozen['status'] == 'FROZEN_VERIFIED_V26'
    assert frozen['producing_exe_sha256'] == '2a305b13466244f84cfd092bfa20774ea0bcfe2f91dbef77decddb850a3a727c'
    assert frozen['origin_commit'] == '1af25c6ced7b315e2c7bbd7bba3c58d125a0c022'
    assert frozen['slot_sha256'] == digest(slot) == '4aaf608d8ac4d18002db155344665cdcea70c0eea7e08637ba2a700bad392e77'
    before = digest(slot)
    env = {key.upper(): value for key, value in os.environ.items()}
    env['SDL_VIDEODRIVER'] = 'dummy'
    env.pop('SDL_AUDIODRIVER', None)
    log = work / 'p504-previous-slot.log'
    result = subprocess.run([
        str(exe), '--config=' + str(work / 'verify-p504-saves.ini'),
        '--extrapath=' + str(work / 'fonts'), '--savepath=' + str(slot.parent),
        '--logfile=' + str(log), '--debuglevel=1', '--save-slot=25', 'astro-verify'
    ], env=env, cwd=work, capture_output=True, text=True, timeout=180)
    text = log.read_text()
    assert result.returncode == 0 and 'P504 startup save: PASS' in text and 'FAIL' not in text, text[-3500:]
    assert text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    assert digest(slot) == before and digest(exe) == expected
    (work / 'p504-previous-slot-proof.json').write_text(json.dumps(dict(
        date='2026-10-27', status='PASS', exe_sha256=expected, slot_sha256=before,
        producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
        unchanged=True, audio_driver='wasapi'
    ), indent=2))
    print('Genuine frozen P504 v26 slot compatibility PASS', flush=True)
    for name in ('check_p501_saves.py', 'check_p504_regressions.py'):
        assert digest(exe) == expected
        journal('RUNNING', step=name)
        print('Starting ' + name, flush=True)
        subprocess.run([sys.executable, str(work / name)], check=True)
    assert digest(exe) == expected
    journal('PASS', full_suite=True)
    print('P501 v27 and all compatible native regression suites PASS', flush=True)
except Exception:
    journal('FAILED', error=traceback.format_exc())
    raise
