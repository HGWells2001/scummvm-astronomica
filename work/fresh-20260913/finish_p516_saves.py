"""Record restricted P516 saves only after the exact complete native regression chain."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

r = Path('outputs/astronomica-cleanroom')
w = Path('work/fresh-20260913')
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = digest(w / 'build/Releasex64/scummvm.exe')
regressions = json.loads((w / 'p516-regressions-status.json').read_text())
assert regressions['status'] == 'PASS' and regressions['full_suite'] and regressions['exe_sha256'] == expected
proof = json.loads((w / 'p516-save-proof.json').read_text())
assert proof['status'] == 'PASS' and proof['exe_sha256'] == expected and not proof['diagnostic']
assert proof['audio_driver'] == 'native' and proof['actual_audio_driver'] == 'wasapi'
assert proof['slot'] == 21 and proof['metadata_listed'] and proof['truncations'] == proof['corruptions'] == 6944
assert proof['choice_controls'] == 6 and proof['direction_settings'] == 4 and proof['speed_settings'] == 16
for key in ('boundaries', 'history_boundaries', 'dormant_boundaries', 'ordinary_boundaries', 'busy_rejections',
            'retained_motion_boundaries', 'handoff_boundaries', 'animation_boundaries', 'successor_checks',
            'timer_cases', 'invalid_states', 'natural_voice_ends'):
    assert proof[key] > 0, key
assert proof['future_outcome_checks'] >= 2 and proof['ambient_deadline_cases'] == 3
assert proof['music_restart'] and proof['extended_atomic_state'] and proof['variant_fixture_unchanged']
previous = json.loads((w / 'p511-previous-slot-proof.json').read_text())
assert previous['status'] == 'PASS' and previous['exe_sha256'] == expected and previous['unchanged']
assert previous['origin_commit'] == 'fa543e9319be616d8d946233ecb7f8e67bcc1a28'
assert previous['slot_sha256'] == '91c0948e9407c17c1c848cf88f5b8561e098dd52bea2c50462579bca673a80bc'
for source, destination, marker in (
    ('p516-saves.log', 'p516-saves-runtime.log', 'P516 save verification: PASS'),
    ('p516-saves-startup.log', 'p516-saves-startup.log', 'P516 startup save: PASS'),
    ('p511-previous-slot.log', 'p511-previous-slot.log', 'P511 startup save: PASS')):
    path = w / source
    text = path.read_text()
    assert path.stat().st_mtime > (w / 'build/Releasex64/scummvm.exe').stat().st_mtime
    assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    shutil.copy2(path, r / 'evidence' / destination)
for name in ('p516-save-proof.json', 'p511-previous-slot-proof.json'):
    shutil.copy2(w / name, r / 'evidence' / name)
validation = dict(proof)
validation.update(date='2026-10-25', format_version=22, payload_bytes=6944, scene=516, full_suite=True,
                  fresh_process_slot=21, byte_corruptions=proof['corruptions'],
                  invalid_checksummed_states=proof['invalid_states'], scope='restricted_stopped_p516',
                  compatibility='Versions1-21 retained; genuine frozen verified v21 slot20 read unchanged',
                  limitations=['Only quiet local2=0 states with configured active orbits and a hidden stopped projectile',
                               'Active flight, aborted unproved history, local2=1, stopped moons and explosion/success transitions excluded',
                               'Pending work and foreground audio excluded; complete manual audiovisual playthrough outstanding'])
(r / 'evidence/p516-saves-validation.json').write_text(json.dumps(validation, indent=2))
subprocess.run([sys.executable, str(r / 'probe_p516_save.py'), '--scene', '516', '--out', str(r / 'evidence/p516-save-original.json')], check=True)
# All earlier proofs have the same executable; record the new validation before shared coverage is regenerated.
subprocess.run([sys.executable, str(w / 'finish_p511_saves.py')], check=True)
heading = ('# Ripresa: salvataggi P516,25 ottobre2026\n\n'
           f'Formato v22:6944byte,{proof["boundaries"]} ripristini verificati. '
           'Conserva orbite, handoff, animazioni e timer indipendenti, storia del missile fermo,605valori e stato cometa. '
           'Slot21 in nuovo processo PASS; compatibilita v1-v21 e vero slotv21 congelato invariato PASS.\n'
           'Scope ristretto:locale2=0,orbite configurate attive e missile nascosto/fermo; volo attivo, altre storie non provate, '
           'locale2=1,orbite ferme,code,voci e transizioni escluse. Suite completa WASAPI sullo stesso eseguibile PASS.\n'
           'Checkpoint:finish_p516_saves.py;check_p516_saves.py;check_p516_regressions.py;P516-SAVE-FORMAT.md. '
           'Non eseguire finalizzatori precedenti da soli.26/35scene con salvataggi verificati non misurano il completamento globale. '
           'Restano altri salvataggi,tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED.\n\n')
path = r / 'NEXT-STEPS.md'
text = path.read_text()
if not text.startswith('# Ripresa: salvataggi P516'):
    path.write_text(heading + text)
model = next(line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if line.startswith('Modello dichiarato'))
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,25 ottobre2026\n\n' + model + '\n\n' + heading +
    'Originali D:/astro; cleanroom dal13settembre2026, senza prototipi o tentativi esclusi. Fermarsi vicino1% della quota limitante; nessun acquisto o riscatto reset.\n')
plan = r / 'P516-SAVE-PLAN.md'
text = plan.read_text()
note = '## Verified restricted P516 saves,25 October2026\n\nVersion22 is verified within the explicit stopped-projectile scope. See P516-SAVE-FORMAT.md and evidence/p516-saves-validation.json. Earlier investigation remains history.\n\n'
if not text.startswith(note):
    plan.write_text(note + text)
format_path = r / 'P516-SAVE-FORMAT.md'
format_text = format_path.read_text().replace('# P516 version22 candidate', '# P516 version22 saves').replace(
    'Status: candidate, SDL only; official native suite pending.',
    'Status: verified25October2026; complete same-build native WASAPI suite PASS within the explicit restricted scope.')
official_heading = '\n\n## Official same-build verification,25 October2026\n\n'
if official_heading not in format_text:
    format_text += official_heading + ('Native WASAPI,86 measured boundaries,all6944truncations/all6944byte corruptions,'
        'fresh-process slot21 and metadata,and unchanged genuine frozen v21slot20 PASS. The complete compatible native suite '
        'passed on the same executable. Earlier SDL investigation remains historical evidence. '
        'The coverage measure becomes26/35inventoried puzzle route scenes (74.3% of save-scene coverage); '
        'it does not measure whole-game completion.\n')
format_path.write_text(format_text)
note = ('\n\n## P516 saves,25 October2026\n\nVersion22 preserves ' + str(proof['boundaries']) +
        ' measured quiet local2=0 P516 boundaries with active orbits and a hidden stopped projectile. Handoff frame/epoch history, '
        'hidden stopped motion, all605runner values, CometMotion and collision geometry are retained. Active flight, aborted unproved histories, '
        'local2=1,stopped moons,pending work,foreground audio and success/explosion transitions remain excluded. '
        'Fresh-process slot21,unchanged genuine frozen v21slot20,6944truncations and6944corruptions,and the complete native WASAPI suite PASS.\n')
for name in ('README.md', 'SAVE-RESEARCH.md'):
    path = r / name
    text = path.read_text()
    if '## P516 saves,25 October2026' not in text:
        path.write_text(text + note)
for name in ('record_save_coverage.py', 'refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(w / name)], check=True)
(r / 'RUN-IN-PROGRESS.md').write_text('Restricted P516v22 native saves verified25October2026. Complete same-build WASAPI suite,fresh-process slot21 and genuine frozen v21slot20 PASS. Publication requires export verification. Newest finisher finish_p516_saves.py. Automation PAUSED.\n')
print('Restricted P516v22 native checkpoint PASS', flush=True)
