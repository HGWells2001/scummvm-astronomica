"""Read an unchanged verified v16 slot, then run P522 and all older native suites."""
from pathlib import Path
import hashlib, json, os, subprocess, sys

root = Path(__file__).resolve().parents[2]
os.chdir(root)
b = root / 'work/fresh-20260913'
exe = b / 'build/Releasex64/scummvm.exe'
slot = b / 'verified-checkpoints/probe-634c241e0d42/frozen-slot15/astro-verify.015'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
frozen = json.loads((slot.parent.parent / 'frozen-slot15.json').read_text())
assert frozen['producing_exe_sha256'] == '634c241e0d4242ad95e5915d4c77af491fe8c20b62100533e6bb82d444152bb0'
assert frozen['slot_sha256'] == digest(slot)
before = digest(slot)
env = {k.upper(): v for k, v in os.environ.items()}
env['SDL_VIDEODRIVER'] = 'dummy'
env.pop('SDL_AUDIODRIVER', None)
log = b / 'probe-previous-slot.log'
p = subprocess.run([
    str(exe), '--config=' + str(b / 'verify-probe-saves.ini'),
    '--extrapath=' + str(b / 'fonts'), '--savepath=' + str(slot.parent),
    '--logfile=' + str(log), '--debuglevel=1', '--save-slot=15', 'astro-verify'
], env=env, cwd=b, capture_output=True, text=True, timeout=180)
s = log.read_text()
assert p.returncode == 0 and 'probe startup save: PASS' in s and 'FAIL' not in s, s[-3500:]
assert 'Log closed successfully' in s and 'Using SDL Audio Driver "wasapi"' in s
assert before == digest(slot) and expected == digest(exe)
(b / 'probe-previous-slot-proof.json').write_text(json.dumps(dict(
    date='2026-10-22', status='PASS', exe_sha256=expected, slot_sha256=before,
    producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
    unchanged=True, audio_driver='wasapi'
), indent=2))
print('Previous probe v16 slot compatibility PASS', flush=True)
for name in ('check_rendezvous_saves.py', 'check_probe_regressions.py'):
    assert digest(exe) == expected
    print('Starting ' + name, flush=True)
    subprocess.run([sys.executable, str(b / name)], check=True)
assert digest(exe) == expected
print('P514 v17 and all compatible native regression suites PASS', flush=True)
