"""Verify genuine v22 compatibility, P527 v23 and the complete older native chain."""
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
snapshot = work / 'verified-checkpoints/p516-6727874da49a'
slot = snapshot / 'frozen-slot21/astro-verify.021'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
state = work / 'p527-regressions-status.json'

def journal(status, **fields):
    pending = state.with_suffix('.tmp')
    pending.write_text(json.dumps(dict(status=status, exe_sha256=expected, **fields), indent=2))
    pending.replace(state)

try:
    journal('RUNNING', step='genuine_frozen_v22')
    frozen = json.loads((snapshot / 'frozen-slot21.json').read_text())
    assert frozen['status'] == 'FROZEN_VERIFIED_V22'
    assert frozen['producing_exe_sha256'] == '6727874da49ad53d05645971547ff544bc57d58ed3ad665cd4ae6dfce1adef8c'
    assert frozen['origin_commit'] == 'dcc18aed083b3957d6a72c5a3e1c3794814d5b9d'
    assert frozen['slot_sha256'] == digest(slot) == '54eaa0859f21014f21890b14f00b33ecb5c6a7a3f90c30a64b84d251934b8781'
    before = digest(slot)
    env = {key.upper(): value for key, value in os.environ.items()}
    env['SDL_VIDEODRIVER'] = 'dummy'
    env.pop('SDL_AUDIODRIVER', None)
    log = work / 'p516-previous-slot.log'
    result = subprocess.run([
        str(exe), '--config=' + str(work / 'verify-p516-saves.ini'),
        '--extrapath=' + str(work / 'fonts'), '--savepath=' + str(slot.parent),
        '--logfile=' + str(log), '--debuglevel=1', '--save-slot=21', 'astro-verify'
    ], env=env, cwd=work, capture_output=True, text=True, timeout=180)
    text = log.read_text()
    assert result.returncode == 0 and 'P516 startup save: PASS' in text and 'FAIL' not in text, text[-3500:]
    assert text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    assert digest(slot) == before and digest(exe) == expected
    (work / 'p516-previous-slot-proof.json').write_text(json.dumps(dict(
        date='2026-10-25', status='PASS', exe_sha256=expected, slot_sha256=before,
        producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
        unchanged=True, audio_driver='wasapi'
    ), indent=2))
    print('Genuine frozen P516 v22 slot compatibility PASS', flush=True)
    for name in ('check_p527_saves.py', 'check_p516_regressions.py'):
        assert digest(exe) == expected
        journal('RUNNING', step=name)
        print('Starting ' + name, flush=True)
        subprocess.run([sys.executable, str(work / name)], check=True)
    assert digest(exe) == expected
    journal('PASS', full_suite=True)
    print('P527 v23 and all compatible native regression suites PASS', flush=True)
except Exception:
    journal('FAILED', error=traceback.format_exc())
    raise
