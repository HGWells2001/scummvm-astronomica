"""Frozen genuine v21 compatibility before P516 and the full older native chain."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
os.chdir(root)
base = root/'work/fresh-20260913'
exe = base/'build/Releasex64/scummvm.exe'
snapshot = base/'verified-checkpoints/p511-1e27c45d9b7f'
slot = snapshot/'frozen-slot20/astro-verify.020'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
(base/'p516-regressions-status.json').write_text(json.dumps(dict(status='RUNNING',exe_sha256=expected),indent=2))
frozen = json.loads((snapshot/'frozen-slot20.json').read_text())
assert frozen['status'] == 'FROZEN_VERIFIED_V21'
assert frozen['producing_exe_sha256'] == '1e27c45d9b7f5f3ab780837931cc7a6b07639fac3b95d6b58d6e2bfdcce2e306'
assert frozen['origin_commit'] == 'fa543e9319be616d8d946233ecb7f8e67bcc1a28'
assert frozen['slot_sha256'] == digest(slot) == '91c0948e9407c17c1c848cf88f5b8561e098dd52bea2c50462579bca673a80bc'
before = digest(slot)
env = {k.upper(): v for k, v in os.environ.items()}
env['SDL_VIDEODRIVER'] = 'dummy'
env.pop('SDL_AUDIODRIVER', None)
log = base/'p511-previous-slot.log'
result = subprocess.run([
    str(exe), '--config='+str(base/'verify-p511-saves.ini'),
    '--extrapath='+str(base/'fonts'), '--savepath='+str(slot.parent),
    '--logfile='+str(log), '--debuglevel=1', '--save-slot=20', 'astro-verify'
], env=env, cwd=base, capture_output=True, text=True, timeout=180)
text = log.read_text()
assert result.returncode == 0 and 'P511 startup save: PASS' in text and 'FAIL' not in text, text[-3500:]
assert text.rstrip().endswith('--- Log closed successfully.')
assert 'Using SDL Audio Driver "wasapi"' in text
assert digest(slot) == before and digest(exe) == expected
(base/'p511-previous-slot-proof.json').write_text(json.dumps(dict(
    date='2026-10-25', status='PASS', exe_sha256=expected, slot_sha256=before,
    producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
    unchanged=True, audio_driver='wasapi'
), indent=2))
print('Genuine frozen P511 v21 slot compatibility PASS', flush=True)
for name in ('check_p516_saves.py', 'check_p511_regressions.py'):
    assert digest(exe) == expected
    print('Starting '+name, flush=True)
    subprocess.run([sys.executable, str(base/name)], check=True)
assert digest(exe) == expected
(base/'p516-regressions-status.json').write_text(json.dumps(dict(status='PASS',exe_sha256=expected,full_suite=True),indent=2))
print('P516 v22 and all compatible native regression suites PASS', flush=True)
