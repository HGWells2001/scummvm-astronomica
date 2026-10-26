"""Verify genuine v23 compatibility, P502 v24 and the complete older native chain."""
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
snapshot = work / 'verified-checkpoints/p527-d0c181251ab0'
slot = snapshot / 'frozen-slot22/astro-verify.022'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
state = work / 'p502-regressions-status.json'

def journal(status, **fields):
    pending = state.with_suffix('.tmp')
    pending.write_text(json.dumps(dict(status=status, exe_sha256=expected, **fields), indent=2))
    pending.replace(state)

try:
    journal('RUNNING', step='genuine_frozen_v23')
    frozen = json.loads((snapshot / 'frozen-slot22.json').read_text())
    assert frozen['status'] == 'FROZEN_VERIFIED_V23'
    assert frozen['producing_exe_sha256'] == 'd0c181251ab0b4714d344a09134ba4f5aa3c4962314b4892fc82660c17fc8c95'
    assert frozen['origin_commit'] == 'c87f0ad095a99519462d5de37d472acbd344d74d'
    assert frozen['slot_sha256'] == digest(slot) == '2e123bf358434a0b8e3aa7ce311ed9bba53d8427e9017cf5461a4927396ae1a5'
    before = digest(slot)
    env = {key.upper(): value for key, value in os.environ.items()}
    env['SDL_VIDEODRIVER'] = 'dummy'
    env.pop('SDL_AUDIODRIVER', None)
    log = work / 'p527-previous-slot.log'
    result = subprocess.run([
        str(exe), '--config=' + str(work / 'verify-p527-saves.ini'),
        '--extrapath=' + str(work / 'fonts'), '--savepath=' + str(slot.parent),
        '--logfile=' + str(log), '--debuglevel=1', '--save-slot=22', 'astro-verify'
    ], env=env, cwd=work, capture_output=True, text=True, timeout=180)
    text = log.read_text()
    assert result.returncode == 0 and 'P527 startup save: PASS' in text and 'FAIL' not in text, text[-3500:]
    assert text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    assert digest(slot) == before and digest(exe) == expected
    (work / 'p527-previous-slot-proof.json').write_text(json.dumps(dict(
        date='2026-10-26', status='PASS', exe_sha256=expected, slot_sha256=before,
        producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
        unchanged=True, audio_driver='wasapi'
    ), indent=2))
    print('Genuine frozen P527 v23 slot compatibility PASS', flush=True)
    for name in ('check_p502_saves.py', 'check_p527_regressions.py'):
        assert digest(exe) == expected
        journal('RUNNING', step=name)
        print('Starting ' + name, flush=True)
        subprocess.run([sys.executable, str(work / name)], check=True)
    assert digest(exe) == expected
    journal('PASS', full_suite=True)
    print('P502 v24 and all compatible native regression suites PASS', flush=True)
except Exception:
    journal('FAILED', error=traceback.format_exc())
    raise
