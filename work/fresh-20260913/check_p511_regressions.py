"""Frozen genuine v20 compatibility before P511 and the full older native chain."""
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
snapshot = base/'verified-checkpoints/p509-b4d7e936aaaf'
slot = snapshot/'frozen-slot19/astro-verify.019'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
frozen = json.loads((snapshot/'frozen-slot19.json').read_text())
assert frozen['status'] == 'FROZEN_VERIFIED_V20'
assert frozen['producing_exe_sha256'] == 'b4d7e936aaaf39a379ee15765b7d49c16546d805bd57a1df5f36d823e097f59f'
assert frozen['origin_commit'] == '5f05fd1d3c9e2c1715e202e58310eb7836e782ce'
assert frozen['slot_sha256'] == digest(slot) == 'fcb257d8c9af158d982063c91d81f5bb8bc32de3a5f055afb4031c92e5aaf0fb'
before = digest(slot)
env = {k.upper(): v for k, v in os.environ.items()}
env['SDL_VIDEODRIVER'] = 'dummy'
env.pop('SDL_AUDIODRIVER', None)
log = base/'p509-previous-slot.log'
result = subprocess.run([
    str(exe), '--config='+str(base/'verify-p509-saves.ini'),
    '--extrapath='+str(base/'fonts'), '--savepath='+str(slot.parent),
    '--logfile='+str(log), '--debuglevel=1', '--save-slot=19', 'astro-verify'
], env=env, cwd=base, capture_output=True, text=True, timeout=180)
text = log.read_text()
assert result.returncode == 0 and 'P509 startup save: PASS' in text and 'FAIL' not in text, text[-3500:]
assert text.rstrip().endswith('--- Log closed successfully.')
assert 'Using SDL Audio Driver "wasapi"' in text
assert digest(slot) == before and digest(exe) == expected
(base/'p509-previous-slot-proof.json').write_text(json.dumps(dict(
    date='2026-10-25', status='PASS', exe_sha256=expected, slot_sha256=before,
    producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
    unchanged=True, audio_driver='wasapi'
), indent=2))
print('Genuine frozen P509 v20 slot compatibility PASS', flush=True)
for name in ('check_p511_saves.py', 'check_p509_regressions.py'):
    assert digest(exe) == expected
    print('Starting '+name, flush=True)
    subprocess.run([sys.executable, str(base/name)], check=True)
assert digest(exe) == expected
print('P511 v21 and all compatible native regression suites PASS', flush=True)


