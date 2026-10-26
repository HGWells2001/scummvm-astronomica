"""Record useful quiet P503 v25 saves after the exact complete native suite."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

research = Path('outputs/astronomica-cleanroom')
work = Path('work/fresh-20260913')
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
exe = work / 'build/Releasex64/scummvm.exe'
expected = digest(exe)
regressions = json.loads((work / 'p503-regressions-status.json').read_text())
assert regressions['status'] == 'PASS' and regressions['full_suite'] and regressions['exe_sha256'] == expected
proof = json.loads((work / 'p503-save-proof.json').read_text())
assert proof['status'] == 'PASS' and proof['exe_sha256'] == expected and not proof['diagnostic']
assert proof['audio_driver'] == 'native' and proof['actual_audio_driver'] == 'wasapi'
assert proof['scope'] == 'quiet_p503_partial_orbits' and proof['slot'] == 24 and proof['metadata_listed']
assert proof['payload_bytes'] == proof['truncations'] == proof['corruptions'] == 8132
assert proof['direction_settings'] == 4 and proof['speed_settings'] == 16
assert proof['failed_launch_combinations'] == 312 and proof['timer_cases'] == 18
assert proof['target_settings'] == 5 and proof['proper_solved_masks'] == 30 and proof['first_kind4_transitions'] == 5
assert proof['partial_boundaries'] > 0 and proof['handoffs'] > 0 and proof['excluded_solved_failure_histories'] == 5
assert proof['future_outcome_checks'] >= 2
positive = ('boundaries', 'history_boundaries', 'dormant_boundaries', 'ordinary_boundaries',
            'busy_rejections', 'prelaunch_boundaries', 'low_failure_boundaries', 'high_failure_boundaries',
            'changed_control_history', 'retained_explosion_boundaries', 'private_cache_boundaries',
            'successor_checks', 'invalid_states', 'natural_voice_ends')
for key in positive:
    assert proof[key] > 0, key
assert proof['extended_atomic_state'] and proof['music_restart'] and proof['variant_fixture_unchanged']
previous = json.loads((work / 'p502-previous-slot-proof.json').read_text())
assert previous['status'] == 'PASS' and previous['exe_sha256'] == expected and previous['unchanged']
assert previous['origin_commit'] == '13ea40c1adb016b2521fc51bf55785654d9ea0f5'
assert previous['slot_sha256'] == '339d18fa1221a926bfa2888c907929acf0338293ac751c5c2f7ce5d0dfb005a4'
for source, destination, marker in (
    ('p503-saves.log', 'p503-saves-runtime.log', 'P503 save verification: PASS'),
    ('p503-saves-startup.log', 'p503-saves-startup.log', 'P503 startup save: PASS'),
    ('p502-previous-slot.log', 'p502-previous-slot.log', 'P502 startup save: PASS')):
    path = work / source
    text = path.read_text()
    assert path.stat().st_mtime > exe.stat().st_mtime
    assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    shutil.copy2(path, research / 'evidence' / destination)
for name in ('p503-save-proof.json', 'p502-previous-slot-proof.json'):
    shutil.copy2(work / name, research / 'evidence' / name)
validation = dict(proof)
validation.update(date='2026-10-26', format_version=25, scene=503, full_suite=True,
                  compatibility='Versions1-24 retained; genuine frozen verified v24 slot23 read unchanged',
                  limitations=['Quiet choices, never-solved stopped failures and healthy partial orbit pairs only',
                               'Primary ascent, solved-target failed relaunch histories, full solved transition, queued work and foreground audio excluded',
                               'Ambient sample cursor is restarted; complete manual audiovisual playthrough outstanding'])
(research / 'evidence/p503-saves-validation.json').write_text(json.dumps(validation, indent=2))
subprocess.run([sys.executable, str(research / 'probe_p503_save.py'), '--out', str(research / 'evidence/p503-save-original.json')], check=True)
plan_path = research/'P503-SAVE-PLAN.md'
plan_path.write_text(plan_path.read_text().replace(
    'Status: isolated real-engine implementation under validation. No production save claim until the complete native closing gate passes.',
    'Status: same-build native WASAPI and complete compatibility verification PASS26October2026. Publication requires the separate export gate.'))
model = next((line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines()
              if line.startswith('Modello dichiarato')), "Modello dichiarato dall'utente: GPT-6.1 Sol, ragionamento medio. Nessun cambio automatico applicato.")
subprocess.run([sys.executable, str(work / 'finish_p502_saves.py')], check=True)
heading = ('# Ripresa: salvataggi P503,26 ottobre2026\n\n'
           f'Formato v25:8132byte,{proof["boundaries"]} ripristini verificati. '
           'Conserva scelte e orbite parziali, con posizione,fotogramma e timer indipendenti dei due oggetti di ogni coppia. '
           'Tutti5bersagli,4direzioni e16velocita,30maschere parziali,605valori e geometria Jupiter dormiente,slot24 in nuovo processo e metadata PASS. '
           'Vero slotv24 congelato invariato e suite completa WASAPI sullo stesso eseguibile PASS.\n'
           'Ascesa iniziale,rilanci falliti di bersagli gia risolti,code,voci e transizioni complete escluse. '
           '29/35scene con salvataggi verificati (82.9% della copertura salvataggi),nessuna percentuale globale attendibile. '
           'Restano altri salvataggi,tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED.\n\n')
path = research / 'NEXT-STEPS.md'
text = path.read_text()
if not text.startswith('# Ripresa: salvataggi P503'):
    path.write_text(heading + text)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,26 ottobre2026\n\n' + model + '\n\n' + heading +
    'Originali D:/astro; cleanroom dal13settembre2026. Checkpoint:finish_p503_saves.py; non eseguire finalizzatori precedenti da soli.\n')
format_path = research / 'P503-SAVE-FORMAT.md'
format_text = format_path.read_text().replace('# P503 version25 candidate', '# P503 version25 saves').replace(
    'Status: staged actual-engine implementation; complete official WASAPI suite/publication pending.',
    'Status: complete same-build native WASAPI suite verified26October2026; publication requires the separate export gate.')
format_text = format_text.replace('# P503 staged save format25', '# P503 save format25').replace(
    'Status: isolated real-engine candidate pending final native proof and independent review. Not integrated into canonical sources or the main executable.',
    'Status: complete same-build native WASAPI suite verified26October2026; publication requires the separate export gate.')
official = '\n\n## Official same-build verification,26 October2026\n\n'
if official not in format_text:
    format_path.write_text(format_text.rstrip() + official +
        'Complete same-build native WASAPI suite,fresh-process slot24,metadata and unchanged genuine frozen v24slot23 PASS. '
        'Only the explicit quiet partial-orbit P503 scope is verified. Earlier candidate entries remain historical evidence.\n')
note = ('\n\n## P503 saves,26 October2026\n\nVersion25 preserves quiet choices, never-solved stopped failures and healthy partial orbits with independent partner frames and motion epochs, '
        'all605runner words,CometMotion scratch and dormant Jupiter geometry. Fresh-process slot24, '
        'all8132truncations/corruptions and genuine frozen v24slot23 compatibility plus complete native WASAPI suite PASS. '
        'Primary ascent, solved-target failed relaunch histories, complete-solution transitions, pending work and foreground audio remain excluded.\n')
for name in ('README.md', 'SAVE-RESEARCH.md'):
    path = research / name
    text = path.read_text()
    if '## P503 saves,26 October2026' not in text:
        path.write_text(text + note)
for name in ('record_save_coverage.py', 'refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(work / name)], check=True)
(research / 'RUN-IN-PROGRESS.md').write_text('Quiet partial-orbit P503v25 native saves verified26October2026; complete same-build WASAPI suite PASS. Publication requires export verification. Newest finisher finish_p503_saves.py; automation PAUSED.\n')
print('Quiet partial-orbit P503v25 native checkpoint PASS', flush=True)
