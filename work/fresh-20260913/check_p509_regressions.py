"""Frozen genuine v19 compatibility before P509 and the full older native chain."""
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
snapshot = base/'verified-checkpoints/p521-c211fe7efe94'
slot = snapshot/'frozen-slot18/astro-verify.018'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
frozen = json.loads((snapshot/'frozen-slot18.json').read_text())
assert frozen['status'] == 'FROZEN_VERIFIED_V19'
assert frozen['producing_exe_sha256'] == 'c211fe7efe949995728705341bc741ed484cc5ba47f68f024ff8326789da6207'
assert frozen['origin_commit'] == '2e0d63a89a00447757affb086866906e5e3c6cf6'
assert frozen['slot_sha256'] == digest(slot) == '4554f711cabb0606b92fe3799db3306e25cc1eaafadca75bc3a0d545133ef5c7'
before = digest(slot)
env = {k.upper(): v for k, v in os.environ.items()}
env['SDL_VIDEODRIVER'] = 'dummy'
env.pop('SDL_AUDIODRIVER', None)
log = base/'p521-previous-slot.log'
result = subprocess.run([
    str(exe), '--config='+str(base/'verify-p521-saves.ini'),
    '--extrapath='+str(base/'fonts'), '--savepath='+str(slot.parent),
    '--logfile='+str(log), '--debuglevel=1', '--save-slot=18', 'astro-verify'
], env=env, cwd=base, capture_output=True, text=True, timeout=180)
text = log.read_text()
assert result.returncode == 0 and 'P521 startup save: PASS' in text and 'FAIL' not in text, text[-3500:]
assert text.rstrip().endswith('--- Log closed successfully.')
assert 'Using SDL Audio Driver "wasapi"' in text
assert digest(slot) == before and digest(exe) == expected
(base/'p521-previous-slot-proof.json').write_text(json.dumps(dict(
    date='2026-10-24', status='PASS', exe_sha256=expected, slot_sha256=before,
    producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
    unchanged=True, audio_driver='wasapi'
), indent=2))
print('Genuine frozen P521 v19 slot compatibility PASS', flush=True)
for name in ('check_p509_saves.py', 'check_p521_regressions.py'):
    assert digest(exe) == expected
    print('Starting '+name, flush=True)
    subprocess.run([sys.executable, str(base/name)], check=True)
assert digest(exe) == expected
print('P509 v20 and all compatible native regression suites PASS', flush=True)
