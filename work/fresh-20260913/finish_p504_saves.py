"""Record useful quiet P504 v26 saves after the exact complete native suite."""
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
regressions = json.loads((work / 'p504-regressions-status.json').read_text())
assert regressions['status'] == 'PASS' and regressions['full_suite'] and regressions['exe_sha256'] == expected
proof = json.loads((work / 'p504-save-proof.json').read_text())
assert proof['status'] == 'PASS' and proof['exe_sha256'] == expected and not proof['diagnostic']
assert proof['audio_driver'] == 'native' and proof['actual_audio_driver'] == 'wasapi'
assert proof['scope'] == 'trusted_p504_partial_orbits' and proof['slot'] == 25 and proof['metadata_listed']
assert proof['payload_bytes'] == proof['truncations'] == proof['corruptions'] == 7816
assert proof['direction_settings'] == 4 and proof['speed_settings'] == 16
assert proof['failed_launch_combinations'] == 252 and proof['timer_cases'] >= 18
assert proof['target_settings'] == 4 and proof['proper_solved_masks'] == 14 and proof['first_kind4_transitions'] == 4
assert proof['partial_boundaries'] > 0 and proof['handoffs'] > 0 and proof['excluded_solved_failure_histories'] == 4
assert proof['future_outcome_checks'] >= 2
assert proof['poll_timer_cases'] >= 24 and proof['rejected_poll_phases'] > 0
positive = ('boundaries', 'history_boundaries', 'dormant_boundaries', 'ordinary_boundaries',
            'busy_rejections', 'prelaunch_boundaries', 'low_failure_boundaries', 'high_failure_boundaries',
            'changed_control_history', 'retained_explosion_boundaries', 'private_cache_boundaries',
            'successor_checks', 'invalid_states', 'natural_voice_ends')
for key in positive:
    assert proof[key] > 0, key
assert proof['extended_atomic_state'] and proof['music_restart'] and proof['variant_fixture_unchanged']
previous = json.loads((work / 'p503-previous-slot-proof.json').read_text())
assert previous['status'] == 'PASS' and previous['exe_sha256'] == expected and previous['unchanged']
assert previous['origin_commit'] == '768a3fd5cfd1c484d3dcacdf297a64ce8f1c6fd9'
assert previous['slot_sha256'] == 'eab9b475a17744f1ed29b4c6f3a0d69886a9b9a7ddb1d4a625cf1fb67654193f'
for source, destination, marker in (
    ('p504-saves.log', 'p504-saves-runtime.log', 'P504 save verification: PASS'),
    ('p504-saves-startup.log', 'p504-saves-startup.log', 'P504 startup save: PASS'),
    ('p503-previous-slot.log', 'p503-previous-slot.log', 'P503 startup save: PASS')):
    path = work / source
    text = path.read_text()
    assert path.stat().st_mtime > exe.stat().st_mtime
    assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    shutil.copy2(path, research / 'evidence' / destination)
for name in ('p504-save-proof.json', 'p503-previous-slot-proof.json'):
    shutil.copy2(work / name, research / 'evidence' / name)
validation = dict(proof)
validation.update(date='2026-10-27', format_version=26, scene=504, full_suite=True,
                  compatibility='Versions1-25 retained; genuine frozen verified v25 slot24 read unchanged',
                  limitations=['Quiet choices, never-solved stopped failures and healthy partial orbit pairs only',
                               'Only the exact original poll at index0/10 is retained; primary ascent, index3, stale solved-target failed relaunch histories, completion, other pending work and foreground audio excluded',
                               'Ambient sample cursor is restarted; complete manual audiovisual playthrough outstanding'])
(research / 'evidence/p504-saves-validation.json').write_text(json.dumps(validation, indent=2))
subprocess.run([sys.executable, str(research / 'probe_p504_save.py'), '--out', str(research / 'evidence/p504-save-original.json')], check=True)
plan_path = research/'P504-SAVE-PLAN.md'
plan_path.write_text(plan_path.read_text().replace(
    'Status: isolated real-engine implementation under validation. No production save claim until the complete native closing gate passes.',
    'Status: same-build native WASAPI and complete compatibility verification PASS27October2026. Publication requires the separate export gate.'))
model = next((line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines()
              if line.startswith('Modello dichiarato')), "Modello dichiarato dall'utente: GPT-6.1 Sol, ragionamento medio. Nessun cambio automatico applicato.")
subprocess.run([sys.executable, str(work / 'finish_p503_saves.py')], check=True)
heading = ('# Ripresa: salvataggi P504,27 ottobre2026\n\n'
           f'Formato v26:7816byte,{proof["boundaries"]} ripristini verificati. '
           'Conserva scelte e orbite parziali, con posizione,fotogramma e timer indipendenti dei due oggetti di ogni coppia. '
           'Tutti i 4 bersagli, 4 direzioni e 16 velocita, 14 maschere parziali, 605 valori e indice/epoca del poll originale conservati, geometria Jupiter dormiente, slot25 in nuovo processo e metadata PASS. '
           'Vero slotv25 congelato invariato e suite completa WASAPI sullo stesso eseguibile PASS.\n'
           'Sono esclusi ascesa, indice3, rilanci falliti di bersagli gia risolti, altre code, voci e transizioni complete. '
           '30/35 scene con salvataggi verificati (85.7% della copertura salvataggi), nessuna percentuale globale attendibile. '
           'Restano altri salvataggi,tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED.\n\n')
path = research / 'NEXT-STEPS.md'
text = path.read_text()
if not text.startswith('# Ripresa: salvataggi P504'):
    path.write_text(heading + text)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,27 ottobre2026\n\n' + model + '\n\n' + heading +
    'Originali D:/astro; cleanroom dal13settembre2026. Checkpoint:finish_p504_saves.py; non eseguire finalizzatori precedenti da soli.\n')
format_path = research / 'P504-SAVE-FORMAT.md'
format_text = format_path.read_text().replace('# P504 version26 candidate', '# P504 version26 saves').replace(
    'Status: staged actual-engine implementation; complete official WASAPI suite/publication pending.',
    'Status: complete same-build native WASAPI suite verified27October2026; publication requires the separate export gate.')
format_text = format_text.replace('# P504 staged save format26', '# P504 save format26').replace(
    'Status: isolated real-engine candidate pending final native proof and independent review. Not integrated into canonical sources or the main executable.',
    'Status: complete same-build native WASAPI suite verified27October2026; publication requires the separate export gate.')
format_text = format_text.replace('# P504 actual-engine staged format26', '# P504 save format26').replace(
    'Status: authored in isolation against the pinned published P503 engine; native and independent final proof pending. No canonical integration is implied.',
    'Status: same-build native WASAPI and complete compatibility verification PASS27October2026; publication requires the separate export gate.')
official = '\n\n## Official same-build verification,27 October2026\n\n'
if official not in format_text:
    format_path.write_text(format_text.rstrip() + official +
        'Complete same-build native WASAPI suite,fresh-process slot25,metadata and unchanged genuine frozen v25slot24 PASS. '
        'Only the explicit trusted-poll partial-orbit P504 scope is verified. Earlier candidate entries remain historical evidence.\n')
note = ('\n\n## P504 saves,27 October2026\n\nVersion26 preserves choices, never-solved stopped failures and healthy partial orbits with independent partner frames and motion epochs, '
        'all605runner words plus literal original poll index/since,CometMotion scratch and dormant Jupiter geometry. Fresh-process slot25, '
        'all7816truncations/corruptions and genuine frozen v25slot24 compatibility plus complete native WASAPI suite PASS. '
        'Primary ascent, index3, solved-target failed relaunch histories, completion, pending work other than the trusted poll and foreground audio remain excluded.\n')
for name in ('README.md', 'SAVE-RESEARCH.md'):
    path = research / name
    text = path.read_text()
    if '## P504 saves,27 October2026' not in text:
        path.write_text(text + note)
for name in ('record_save_coverage.py', 'refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(work / name)], check=True)
(research / 'RUN-IN-PROGRESS.md').write_text('Quiet partial-orbit P504v26 native saves verified27October2026; complete same-build WASAPI suite PASS. Publication requires export verification. Newest finisher finish_p504_saves.py; automation PAUSED.\n')
print('Quiet partial-orbit P504v26 native checkpoint PASS', flush=True)
