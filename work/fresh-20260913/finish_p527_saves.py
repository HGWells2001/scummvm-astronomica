"""Record P527 v23 only after the unchanged complete native regression chain."""
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
regressions = json.loads((work / 'p527-regressions-status.json').read_text())
assert regressions['status'] == 'PASS' and regressions['full_suite'] and regressions['exe_sha256'] == expected
proof = json.loads((work / 'p527-save-proof.json').read_text())
assert proof['status'] == 'PASS' and proof['exe_sha256'] == expected and not proof['diagnostic']
assert proof['audio_driver'] == 'native' and proof['actual_audio_driver'] == 'wasapi'
assert proof['scope'] == 'quiet_p527' and proof['slot'] == 22 and proof['metadata_listed']
assert proof['payload_bytes'] == proof['truncations'] == proof['corruptions'] == 3940
assert proof['seen_masks'] == 15 and proof['selector_states'] == 5 and proof['movie_frames'] == 1105
assert proof['future_outcome_checks'] >= 2
for key in ('boundaries', 'history_boundaries', 'dormant_boundaries', 'ordinary_boundaries',
            'busy_rejections', 'absent_boundaries', 'selector_image_mismatches', 'successor_checks',
            'invalid_states', 'natural_voice_ends'):
    assert proof[key] > 0, key
assert proof['extended_atomic_state'] and proof['music_restart'] and proof['variant_fixture_unchanged']
previous = json.loads((work / 'p516-previous-slot-proof.json').read_text())
assert previous['status'] == 'PASS' and previous['exe_sha256'] == expected and previous['unchanged']
assert previous['origin_commit'] == 'dcc18aed083b3957d6a72c5a3e1c3794814d5b9d'
assert previous['slot_sha256'] == '54eaa0859f21014f21890b14f00b33ecb5c6a7a3f90c30a64b84d251934b8781'
for source, destination, marker in (
    ('p527-saves.log', 'p527-saves-runtime.log', 'P527 save verification: PASS'),
    ('p527-saves-startup.log', 'p527-saves-startup.log', 'P527 startup save: PASS'),
    ('p516-previous-slot.log', 'p516-previous-slot.log', 'P516 startup save: PASS')):
    path = work / source
    text = path.read_text()
    assert path.stat().st_mtime > exe.stat().st_mtime
    assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    shutil.copy2(path, research / 'evidence' / destination)
for name in ('p527-save-proof.json', 'p516-previous-slot-proof.json'):
    shutil.copy2(work / name, research / 'evidence' / name)
validation = dict(proof)
validation.update(date='2026-10-25', format_version=23, scene=527, full_suite=True,
                  compatibility='Versions1-22 retained; genuine frozen verified v22 slot21 read unchanged',
                  limitations=['Stopped movie and quiet script-idle boundaries only',
                               'Foreground audio, active playback and queued work excluded',
                               'Ambient sample position is restarted; manual audiovisual playthrough remains outstanding'])
(research / 'evidence/p527-saves-validation.json').write_text(json.dumps(validation, indent=2))
subprocess.run([sys.executable, str(research / 'probe_p527_save.py'), '--out', str(research / 'evidence/p527-save-original.json')], check=True)
model = next((line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines()
              if line.startswith('Modello dichiarato')), "Modello dichiarato dall'utente: GPT-6.1 Sol, ragionamento medio. Nessun cambio automatico applicato.")
subprocess.run([sys.executable, str(work / 'finish_p516_saves.py')], check=True)
heading = ('# Ripresa: salvataggi P527,25 ottobre2026\n\n'
           f'Formato v23:3940byte,{proof["boundaries"]} ripristini verificati. '
           'Conserva selezione,maschera,ultimo intervallo tentato e fotogramma realmente presentato indipendenti. '
           'Tutti1105fotogrammi originali confrontati tra decodifica sequenziale e seek; slot22 in nuovo processo e metadata PASS. '
           'Vero slotv22 congelato invariato e suite completa WASAPI sullo stesso eseguibile PASS.\n'
           'Confini quieti con filmato fermo; riproduzione attiva,code e voci in primo piano escluse. '
           '27/35scene con salvataggi verificati (77,1% della copertura salvataggi),nessuna percentuale globale attendibile. '
           'Restano altri salvataggi,tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED.\n\n')
path = research / 'NEXT-STEPS.md'
text = path.read_text()
if not text.startswith('# Ripresa: salvataggi P527'):
    path.write_text(heading + text)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,25 ottobre2026\n\n' + model + '\n\n' + heading +
    'Originali D:/astro; cleanroom dal13settembre2026. Checkpoint:finish_p527_saves.py; non eseguire finalizzatori precedenti da soli.\n')
note = ('\n\n## P527 saves,25 October2026\n\nVersion23 preserves quiet stopped-movie boundaries, '
        'selection and seen history, independent retained movie sample and all605runner words. '
        'All1105native frame reconstructions,fresh-process slot22,unchanged genuine frozen v22slot21 and the complete WASAPI suite PASS. '
        'Active playback,queued work and foreground audio remain excluded.\n')
format_path = research / 'P527-SAVE-FORMAT.md'
format_text = format_path.read_text().replace('# P527 version23 candidate', '# P527 version23 saves').replace(
    'Status: staged real-engine implementation; complete official native suite and publication pending.',
    'Status: complete same-build native WASAPI suite verified25October2026; publication requires the separate export gate.')
official = '\n\n## Official same-build verification,25 October2026\n\n'
if official not in format_text:
    format_path.write_text(format_text.rstrip() + official +
        'Complete same-build native WASAPI suite,fresh-process slot22,metadata and unchanged genuine frozen v22slot21 PASS. '
        'All1105original frame reconstructions compare byte-for-byte. Earlier candidate entries remain historical evidence.\n')
for name in ('README.md', 'SAVE-RESEARCH.md'):
    path = research / name
    text = path.read_text()
    if '## P527 saves,25 October2026' not in text:
        path.write_text(text + note)
for name in ('record_save_coverage.py', 'refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(work / name)], check=True)
(research / 'RUN-IN-PROGRESS.md').write_text('Quiet P527v23 native saves verified25October2026; complete same-build WASAPI suite PASS. Publication requires export verification. Newest finisher finish_p527_saves.py; automation PAUSED.\n')
print('Quiet P527v23 native checkpoint PASS', flush=True)
