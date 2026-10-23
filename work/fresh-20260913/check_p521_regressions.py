"""Read a frozen genuine v18 slot before new P521 and all older native suites."""
from pathlib import Path
import hashlib, json, os, subprocess, sys

root = Path(__file__).resolve().parents[2]
os.chdir(root)
b = root / 'work/fresh-20260913'
exe = b / 'build/Releasex64/scummvm.exe'
slot = b / 'verified-checkpoints/planet-9994d088c56e/frozen-slot17/astro-verify.017'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(exe)
frozen = json.loads((slot.parent.parent / 'frozen-slot17.json').read_text())
assert frozen['producing_exe_sha256'] == '9994d088c56ed65f86de27c3681c4a5179a78a5e2c0190c52e11461c1913c601'
assert frozen['slot_sha256'] == digest(slot)
before = digest(slot)
env = {k.upper(): v for k, v in os.environ.items()}
env['SDL_VIDEODRIVER'] = 'dummy'
env.pop('SDL_AUDIODRIVER', None)
log = b / 'planet-previous-slot.log'
p = subprocess.run([
    str(exe), '--config=' + str(b / 'verify-planet-saves.ini'),
    '--extrapath=' + str(b / 'fonts'), '--savepath=' + str(slot.parent),
    '--logfile=' + str(log), '--debuglevel=1', '--save-slot=17', 'astro-verify'
], env=env, cwd=b, capture_output=True, text=True, timeout=180)
s = log.read_text()
assert p.returncode == 0 and 'planet startup save: PASS' in s and 'FAIL' not in s, s[-3500:]
assert 'Log closed successfully' in s and 'Using SDL Audio Driver "wasapi"' in s
assert before == digest(slot) and expected == digest(exe)
(b / 'planet-previous-slot-proof.json').write_text(json.dumps(dict(
    date='2026-10-23', status='PASS', exe_sha256=expected, slot_sha256=before,
    producing_exe_sha256=frozen['producing_exe_sha256'], origin_commit=frozen['origin_commit'],
    unchanged=True, audio_driver='wasapi'
), indent=2))
print('Previous planet v18 slot compatibility PASS', flush=True)
for name in ('check_p521_saves.py', 'check_planet_regressions.py'):
    assert digest(exe) == expected
    print('Starting ' + name, flush=True)
    subprocess.run([sys.executable, str(b / name)], check=True)
assert digest(exe) == expected
print('P521 v19 and all compatible native regression suites PASS', flush=True)
