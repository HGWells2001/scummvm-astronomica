"""Verify real P522 saves and fresh-process continuation; parse measured coverage."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, time

ap = argparse.ArgumentParser()
ap.add_argument('--exe', type=Path)
ap.add_argument('--tag', default='')
ap.add_argument('--dummy-audio', action='store_true')
ap.add_argument('--variant-slot', type=Path)
args = ap.parse_args()
assert not args.tag or re.fullmatch(r'[a-z0-9-]+', args.tag)
assert not (args.exe or args.dummy_audio or args.variant_slot) or args.tag, 'Diagnostic overrides require isolated output names'
root = Path(__file__).resolve().parents[2]
base = Path(__file__).resolve().parent
exe = args.exe.resolve() if args.exe else base/'build/Releasex64/scummvm.exe'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected_exe = digest(exe)
prefix = args.tag+'-' if args.tag else ''
cfg = base/(prefix+'verify-probe-saves.ini')
savepath = base/(prefix+'probe-save-regression')
savepath.mkdir(exist_ok=True)
source = args.variant_slot.resolve() if args.variant_slot else base/'variant-save-regression/astro-verify.009'
alias = savepath/'astro-verify.099'
source_hash = digest(source)
assert source != alias, 'Variant source must remain separate from the isolated alias'
shutil.copyfile(source, alias)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_probe_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env = {k.upper(): v for k, v in os.environ.items()}
env['SDL_VIDEODRIVER'] = 'dummy'
env.pop('SDL_AUDIODRIVER', None)
if args.dummy_audio:
    env['SDL_AUDIODRIVER'] = 'dummy'
expected_driver = 'dummy' if args.dummy_audio else 'wasapi'
common = [str(exe), '--config='+str(cfg), '--extrapath='+str(base/'fonts'), '--savepath='+str(savepath), '--debuglevel=1']
audio = {f'P522/{name}': digest(Path('D:/astro/PLACES/P522')/name) for name in ('S0.WAV', 'S1.WAV')}
fingerprints = []
coverage = None
for name, extra in [('probe-saves', []), ('probe-saves-startup', ['--save-slot=15'])]:
    assert digest(exe) == expected_exe
    log = base/(prefix+name+'.log')
    log.write_text('')
    console = base/(prefix+name+'-console.log')
    with console.open('w') as output:
        p = subprocess.Popen(common+['--logfile='+str(log)]+extra+['astro-verify'], env=env, cwd=base, stdout=output, stderr=subprocess.STDOUT, text=True)
        started = time.monotonic()
        try:
            while p.poll() is None and time.monotonic()-started < 1800:
                if 'FAIL' in log.read_text():
                    p.terminate()
                    break
                time.sleep(0.25)
            if p.poll() is None:
                p.terminate()
            p.wait(timeout=10)
        finally:
            if p.poll() is None:
                p.terminate()
                p.wait(timeout=10)
    text = log.read_text()
    print(name, 'exit', p.returncode, flush=True)
    if p.returncode or 'FAIL' in text:
        print(text[-6500:]+console.read_text()[-1000:])
        raise AssertionError(name)
    assert 'probe save verification: PASS' in text and text.rstrip().endswith('--- Log closed successfully.'), name
    drivers = re.findall(r'Using SDL Audio Driver "([^"]+)"', text)
    assert drivers == [expected_driver], drivers
    assert 'Using SDL Video Driver "dummy"' in text
    found = re.findall(r'probe slot fingerprint: ([0-9a-f]{8})', text)
    assert len(found) == 1, found
    fingerprints.append(found[0])
    if extra:
        assert 'probe startup save: PASS' in text
    else:
        matches = re.findall(r'Astronomica probe saves: PASS \((\d+) boundaries, (\d+) history boundaries, (\d+) dormant boundaries, (\d+) ordinary boundaries, (\d+) failed return boundaries, (\d+) calendar edges, (\d+) poll timing cases, (\d+) flight rejections\)', text)
        assert len(matches) == 1
        keys = ('boundaries', 'history_boundaries', 'dormant_boundaries', 'ordinary_boundaries', 'failed_return_boundaries', 'calendar_edges', 'poll_timing_cases', 'flight_rejections')
        coverage = dict(zip(keys, map(int, matches[0])))
        assert all(n > 0 for n in coverage.values()), coverage
        rejected = re.findall(r'Astronomica probe rejection verification: PASS \((\d+) truncations, (\d+) corruptions, (\d+) invalid states, extended atomic state\)', text)
        assert len(rejected) == 1
        truncations, corruptions, invalid_states = map(int, rejected[0])
        assert truncations == corruptions == 4472 and invalid_states > 0
        voices = re.findall(r'Astronomica probe natural voice end: PASS', text)
        music = re.findall(r'Astronomica probe Music restart: PASS', text)
        assert len(voices) == len(music) == 1
        coverage.update(truncations=truncations, corruptions=corruptions, invalid_states=invalid_states,
                        extended_atomic_state=bool(rejected), natural_voice_ends=len(voices), music_restart=bool(music))
    assert digest(exe) == expected_exe
    print(text[-1800:], flush=True)
assert fingerprints[0] == fingerprints[1], fingerprints
p = subprocess.run(common+['--list-saves'], env=env, cwd=base, capture_output=True, text=True, timeout=60)
metadata_listed = p.returncode == 0 and 'Probe continuation regression' in p.stdout
assert metadata_listed, p.stdout+p.stderr
(base/(prefix+'probe-saves-list.log')).write_text(p.stdout+p.stderr)
for name, expected in audio.items():
    assert digest(Path('D:/astro/PLACES')/name) == expected
fixture_unchanged = digest(source) == digest(alias) == source_hash
assert fixture_unchanged and digest(exe) == expected_exe
proof = dict(date='2026-10-22', status='PASS', audio_driver='dummy' if args.dummy_audio else 'native',
             actual_audio_driver=expected_driver, diagnostic=bool(args.tag), exe_sha256=expected_exe,
             metadata_listed=metadata_listed, slot=15, fresh_process_fingerprint=fingerprints[1],
             original_wav_sha256=audio, variant_fixture_sha256=source_hash, variant_fixture_unchanged=fixture_unchanged,
             **coverage)
(base/(prefix+'probe-save-proof.json')).write_text(json.dumps(proof, indent=2))
print('P522 measured save coverage, fresh-process continuation and metadata PASS', flush=True)
