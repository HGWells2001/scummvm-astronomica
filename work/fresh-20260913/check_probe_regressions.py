"""Read an unchanged verified v15 slot, then run P522 and all older native suites."""
from pathlib import Path
import hashlib, json, os, subprocess, sys

root = Path(__file__).resolve().parents[2]
os.chdir(root)
b = root / 'work/fresh-20260913'
exe = b / 'build/Releasex64/scummvm.exe'
slot = b / 'verified-checkpoints/universe-dbe43465359f/frozen-slot14/astro-verify.014'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
frozen = json.loads((slot.parent.parent / 'frozen-slot14.json').read_text())
assert frozen['producing_exe_sha256'] == 'dbe43465359fff29a4a1931b850f463251120a71c21039e44106e64a1b6ffe7b'
assert frozen['slot_sha256'] == digest(slot)
before = digest(slot)
env = {k.upper(): v for k, v in os.environ.items()}
env['SDL_VIDEODRIVER'] = 'dummy'
env.pop('SDL_AUDIODRIVER', None)
log = b / 'universe-previous-slot.log'
p = subprocess.run([
    str(exe), '--config=' + str(b / 'verify-universe-saves.ini'),
    '--extrapath=' + str(b / 'fonts'), '--savepath=' + str(slot.parent),
    '--logfile=' + str(log), '--debuglevel=1', '--save-slot=14', 'astro-verify'
], env=env, cwd=b, capture_output=True, text=True, timeout=180)
s = log.read_text()
assert p.returncode == 0 and 'universe startup save: PASS' in s and 'FAIL' not in s, s[-3500:]
assert 'Log closed successfully' in s and 'Using SDL Audio Driver "wasapi"' in s
assert before == digest(slot) and expected == digest(exe)
(b / 'universe-previous-slot-proof.json').write_text(json.dumps(dict(
    date='2026-10-22', status='PASS', exe_sha256=expected, slot_sha256=before,
    producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
    unchanged=True, audio_driver='wasapi'
), indent=2))
print('Previous universe v15 slot compatibility PASS', flush=True)
for name in ('check_probe_saves.py', 'check_universe_regressions.py'):
    assert digest(exe) == expected
    print('Starting ' + name, flush=True)
    subprocess.run([sys.executable, str(b / name)], check=True)
assert digest(exe) == expected
print('P522 v16 and all compatible native regression suites PASS', flush=True)
