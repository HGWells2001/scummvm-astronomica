"""Verify genuine v25 compatibility, P504 v26 and the complete older native chain."""
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
snapshot = work / 'verified-checkpoints/p503-1777ebb503b6'
slot = snapshot / 'frozen-slot24/astro-verify.024'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
state = work / 'p504-regressions-status.json'

def journal(status, **fields):
    pending = state.with_suffix('.tmp')
    pending.write_text(json.dumps(dict(status=status, exe_sha256=expected, **fields), indent=2))
    pending.replace(state)

try:
    journal('RUNNING', step='genuine_frozen_v25')
    frozen = json.loads((snapshot / 'frozen-slot24.json').read_text())
    assert frozen['status'] == 'FROZEN_VERIFIED_V25'
    assert frozen['producing_exe_sha256'] == '1777ebb503b6a9389be9f55f46d1a2fc9a14357ea3042ab4bf9d0599083f4974'
    assert frozen['origin_commit'] == '768a3fd5cfd1c484d3dcacdf297a64ce8f1c6fd9'
    assert frozen['slot_sha256'] == digest(slot) == 'eab9b475a17744f1ed29b4c6f3a0d69886a9b9a7ddb1d4a625cf1fb67654193f'
    before = digest(slot)
    env = {key.upper(): value for key, value in os.environ.items()}
    env['SDL_VIDEODRIVER'] = 'dummy'
    env.pop('SDL_AUDIODRIVER', None)
    log = work / 'p503-previous-slot.log'
    result = subprocess.run([
        str(exe), '--config=' + str(work / 'verify-p503-saves.ini'),
        '--extrapath=' + str(work / 'fonts'), '--savepath=' + str(slot.parent),
        '--logfile=' + str(log), '--debuglevel=1', '--save-slot=24', 'astro-verify'
    ], env=env, cwd=work, capture_output=True, text=True, timeout=180)
    text = log.read_text()
    assert result.returncode == 0 and 'P503 startup save: PASS' in text and 'FAIL' not in text, text[-3500:]
    assert text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    assert digest(slot) == before and digest(exe) == expected
    (work / 'p503-previous-slot-proof.json').write_text(json.dumps(dict(
        date='2026-10-27', status='PASS', exe_sha256=expected, slot_sha256=before,
        producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
        unchanged=True, audio_driver='wasapi'
    ), indent=2))
    print('Genuine frozen P503 v25 slot compatibility PASS', flush=True)
    for name in ('check_p504_saves.py', 'check_p503_regressions.py'):
        assert digest(exe) == expected
        journal('RUNNING', step=name)
        print('Starting ' + name, flush=True)
        subprocess.run([sys.executable, str(work / name)], check=True)
    assert digest(exe) == expected
    journal('PASS', full_suite=True)
    print('P504 v26 and all compatible native regression suites PASS', flush=True)
except Exception:
    journal('FAILED', error=traceback.format_exc())
    raise
