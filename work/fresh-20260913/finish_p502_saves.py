"""Record useful quiet P502 v24 saves after the exact complete native suite."""
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
regressions = json.loads((work / 'p502-regressions-status.json').read_text())
assert regressions['status'] == 'PASS' and regressions['full_suite'] and regressions['exe_sha256'] == expected
proof = json.loads((work / 'p502-save-proof.json').read_text())
assert proof['status'] == 'PASS' and proof['exe_sha256'] == expected and not proof['diagnostic']
assert proof['audio_driver'] == 'native' and proof['actual_audio_driver'] == 'wasapi'
assert proof['scope'] == 'quiet_p502_nonflight' and proof['slot'] == 23 and proof['metadata_listed']
assert proof['payload_bytes'] == proof['truncations'] == proof['corruptions'] == 6728
assert proof['direction_settings'] == 4 and proof['speed_settings'] == 16
assert proof['failed_launch_combinations'] == 62 and proof['timer_cases'] == 6
assert proof['future_outcome_checks'] >= 2
positive = ('boundaries', 'history_boundaries', 'dormant_boundaries', 'ordinary_boundaries',
            'busy_rejections', 'prelaunch_boundaries', 'low_failure_boundaries', 'high_failure_boundaries',
            'changed_control_history', 'retained_explosion_boundaries', 'private_cache_boundaries',
            'successor_checks', 'invalid_states', 'natural_voice_ends')
for key in positive:
    assert proof[key] > 0, key
assert proof['extended_atomic_state'] and proof['music_restart'] and proof['variant_fixture_unchanged']
previous = json.loads((work / 'p527-previous-slot-proof.json').read_text())
assert previous['status'] == 'PASS' and previous['exe_sha256'] == expected and previous['unchanged']
assert previous['origin_commit'] == 'c87f0ad095a99519462d5de37d472acbd344d74d'
assert previous['slot_sha256'] == '2e123bf358434a0b8e3aa7ce311ed9bba53d8427e9017cf5461a4927396ae1a5'
for source, destination, marker in (
    ('p502-saves.log', 'p502-saves-runtime.log', 'P502 save verification: PASS'),
    ('p502-saves-startup.log', 'p502-saves-startup.log', 'P502 startup save: PASS'),
    ('p527-previous-slot.log', 'p527-previous-slot.log', 'P527 startup save: PASS')):
    path = work / source
    text = path.read_text()
    assert path.stat().st_mtime > exe.stat().st_mtime
    assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    shutil.copy2(path, research / 'evidence' / destination)
for name in ('p502-save-proof.json', 'p527-previous-slot-proof.json'):
    shutil.copy2(work / name, research / 'evidence' / name)
validation = dict(proof)
validation.update(date='2026-10-26', format_version=24, scene=502, full_suite=True,
                  compatibility='Versions1-23 retained; genuine frozen verified v23 slot22 read unchanged',
                  limitations=['Quiet nonflight choice and hidden stopped failed-return boundaries only',
                               'Active flight, success transitions, queued work and foreground audio excluded',
                               'Ambient sample cursor is restarted; complete manual audiovisual playthrough outstanding'])
(research / 'evidence/p502-saves-validation.json').write_text(json.dumps(validation, indent=2))
subprocess.run([sys.executable, str(research / 'probe_p502_save.py'), '--out', str(research / 'evidence/p502-save-original.json')], check=True)
model = next((line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines()
              if line.startswith('Modello dichiarato')), "Modello dichiarato dall'utente: GPT-6.1 Sol, ragionamento medio. Nessun cambio automatico applicato.")
subprocess.run([sys.executable, str(work / 'finish_p527_saves.py')], check=True)
heading = ('# Ripresa: salvataggi P502,26 ottobre2026\n\n'
           f'Formato v24:6728byte,{proof["boundaries"]} ripristini verificati. '
           'Conserva scelte,proiettile nascosto fermo,coordinate e timer dei fallimenti,CometMotion ed esplosione indipendenti. '
           'Tutte4direzioni e16velocita,605valori e geometria Jupiter dormiente,slot23 in nuovo processo e metadata PASS. '
           'Vero slotv23 congelato invariato e suite completa WASAPI sullo stesso eseguibile PASS.\n'
           'Confini quieti senza volo; code,voci e transizioni di successo escluse. '
           '28/35scene con salvataggi verificati (80% della copertura salvataggi),nessuna percentuale globale attendibile. '
           'Restano altri salvataggi,tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED.\n\n')
path = research / 'NEXT-STEPS.md'
text = path.read_text()
if not text.startswith('# Ripresa: salvataggi P502'):
    path.write_text(heading + text)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,26 ottobre2026\n\n' + model + '\n\n' + heading +
    'Originali D:/astro; cleanroom dal13settembre2026. Checkpoint:finish_p502_saves.py; non eseguire finalizzatori precedenti da soli.\n')
format_path = research / 'P502-SAVE-FORMAT.md'
format_text = format_path.read_text().replace('# P502 version24 candidate', '# P502 version24 saves').replace(
    'Status: staged actual-engine implementation; complete official WASAPI suite/publication pending.',
    'Status: complete same-build native WASAPI suite verified26October2026; publication requires the separate export gate.')
official = '\n\n## Official same-build verification,26 October2026\n\n'
if official not in format_text:
    format_path.write_text(format_text.rstrip() + official +
        'Complete same-build native WASAPI suite,fresh-process slot23,metadata and unchanged genuine frozen v23slot22 PASS. '
        'Only the explicit quiet nonflight P502 scope is verified. Earlier candidate entries remain historical evidence.\n')
note = ('\n\n## P502 saves,26 October2026\n\nVersion24 preserves quiet nonflight choices and hidden stopped failed-return history, '
        'all605runner words,CometMotion scratch and dormant Jupiter geometry. Fresh-process slot23, '
        'all6728truncations/corruptions and genuine frozen v23slot22 compatibility plus complete native WASAPI suite PASS. '
        'Active flight,success transitions,pending work and foreground audio remain excluded.\n')
for name in ('README.md', 'SAVE-RESEARCH.md'):
    path = research / name
    text = path.read_text()
    if '## P502 saves,26 October2026' not in text:
        path.write_text(text + note)
for name in ('record_save_coverage.py', 'refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(work / name)], check=True)
(research / 'RUN-IN-PROGRESS.md').write_text('Quiet nonflight P502v24 native saves verified26October2026; complete same-build WASAPI suite PASS. Publication requires export verification. Newest finisher finish_p502_saves.py; automation PAUSED.\n')
print('Quiet nonflight P502v24 native checkpoint PASS', flush=True)
