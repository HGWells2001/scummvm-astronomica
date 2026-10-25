"""Verify real P511 saves and fresh-process continuation; parse measured coverage."""
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
cfg = base/(prefix+'verify-p511-saves.ini')
savepath = base/(prefix+'p511-save-regression')
savepath.mkdir(exist_ok=True)
source = args.variant_slot.resolve() if args.variant_slot else base/'variant-save-regression/astro-verify.009'
alias = savepath/'astro-verify.099'
source_hash = digest(source)
assert source != alias, 'Variant source must remain separate from the isolated alias'
shutil.copyfile(source, alias)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p511_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env = {k.upper(): v for k, v in os.environ.items()}
env['SDL_VIDEODRIVER'] = 'dummy'
env.pop('SDL_AUDIODRIVER', None)
if args.dummy_audio:
    env['SDL_AUDIODRIVER'] = 'dummy'
expected_driver = 'dummy' if args.dummy_audio else 'wasapi'
common = [str(exe), '--config='+str(cfg), '--extrapath='+str(base/'fonts'), '--savepath='+str(savepath), '--debuglevel=1']
audio = {f'P511/{p.name}': digest(p) for p in sorted(Path('D:/astro/PLACES/P511').glob('*.WAV'))}
assert audio and 'P511/S0.WAV' in audio and 'P511/S1.WAV' in audio
fingerprints = []
coverage = None
for name, extra in [('p511-saves', []), ('p511-saves-startup', ['--save-slot=20'])]:
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
    assert 'P511 save verification: PASS' in text and text.rstrip().endswith('--- Log closed successfully.'), name
    drivers = re.findall(r'Using SDL Audio Driver "([^"]+)"', text)
    assert drivers == [expected_driver], drivers
    assert 'Using SDL Video Driver "dummy"' in text
    found = re.findall(r'P511 slot fingerprint: ([0-9a-f]{8})', text)
    assert len(found) == 1, found
    fingerprints.append(found[0])
    if extra:
        assert 'P511 startup save: PASS' in text
    else:
        matches = re.findall(r'Astronomica P511 saves: PASS \((\d+) boundaries, (\d+) history boundaries, (\d+) dormant boundaries, (\d+) ordinary boundaries, (\d+) busy rejections\)', text)
        assert len(matches) == 1
        keys = ('boundaries', 'history_boundaries', 'dormant_boundaries', 'ordinary_boundaries', 'busy_rejections')
        coverage = dict(zip(keys, map(int, matches[0])))
        assert all(n > 0 for n in coverage.values()), coverage
        history = re.findall(r'Astronomica P511 history coverage: PASS \((\d+) choice controls, (\d+) retained-image boundaries, (\d+) frame-history boundaries, (\d+) animation boundaries, (\d+) successor checks, (\d+) future outcome checks\)', text)
        assert len(history) == 1
        keys = ('choice_controls','retained_image_boundaries','frame_history_boundaries','animation_boundaries','successor_checks','future_outcome_checks')
        coverage.update(zip(keys,map(int,history[0])))
        assert coverage['choice_controls'] == 8 and coverage['future_outcome_checks'] >= 4 and all(coverage[k] > 0 for k in keys), coverage
        timers = re.findall(r'Astronomica P511 timer epochs: PASS \((\d+) native save/successor cases, before/at/after periods and uint32 wrap\)', text)
        assert len(timers) == 1 and int(timers[0]) > 0
        coverage['timer_cases'] = int(timers[0])
        rejected = re.findall(r'Astronomica P511 rejection verification: PASS \((\d+) truncations, (\d+) corruptions, (\d+) invalid states, extended atomic state\)', text)
        assert len(rejected) == 1
        truncations, corruptions, invalid_states = map(int, rejected[0])
        assert truncations == corruptions == 6256 and invalid_states > 0
        voices = re.findall(r'Astronomica P511 natural voice end: PASS', text)
        music = re.findall(r'Astronomica P511 Music restart: PASS', text)
        assert len(voices) == len(music) == 1
        coverage.update(truncations=truncations, corruptions=corruptions, invalid_states=invalid_states,
                        extended_atomic_state=bool(rejected), natural_voice_ends=len(voices), music_restart=bool(music))
        domains = re.findall(r'Astronomica P511 controls coverage: PASS \((\d+) dial settings, (\d+) cloud settings, (\d+) type settings\)', text)
        assert len(domains)==1 and tuple(map(int,domains[0]))==(16,14,4), domains
        coverage.update(zip(('dial_settings','cloud_settings','type_settings'),map(int,domains[0])))
        deadline = re.findall(r'Astronomica P511 ambient deadline: PASS \((\d+) cases, original entry\)', text)
        assert len(deadline)==1 and int(deadline[0])==3, deadline
        coverage['ambient_deadline_cases']=int(deadline[0])
    assert digest(exe) == expected_exe
    print(text[-1800:], flush=True)
assert fingerprints[0] == fingerprints[1], fingerprints
p = subprocess.run(common+['--list-saves'], env=env, cwd=base, capture_output=True, text=True, timeout=60)
metadata_listed = p.returncode == 0 and 'P511 continuation regression' in p.stdout
assert metadata_listed, p.stdout+p.stderr
(base/(prefix+'p511-saves-list.log')).write_text(p.stdout+p.stderr)
for name, expected in audio.items():
    assert digest(Path('D:/astro/PLACES')/name) == expected
fixture_unchanged = digest(source) == digest(alias) == source_hash
assert fixture_unchanged and digest(exe) == expected_exe
proof = dict(date='2026-10-25', status='PASS', audio_driver='dummy' if args.dummy_audio else 'native',
             actual_audio_driver=expected_driver, diagnostic=bool(args.tag), exe_sha256=expected_exe,
             metadata_listed=metadata_listed, slot=20, fresh_process_fingerprint=fingerprints[1],
             original_wav_sha256=audio, variant_fixture_sha256=source_hash, variant_fixture_unchanged=fixture_unchanged,
             **coverage)
(base/(prefix+'p511-save-proof.json')).write_text(json.dumps(proof, indent=2))
print('P511 measured save coverage, fresh-process continuation and metadata PASS', flush=True)




