"""Record P501 v27 only after its exact main-build native compatibility chain passes."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import shutil
import subprocess
import sys

r = Path('outputs/astronomica-cleanroom')
w = Path('work/fresh-20260913')
d = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
exe = w / 'build/Releasex64/scummvm.exe'
expected = d(exe)
regressions = json.loads((w / 'p501-regressions-status.json').read_text())
assert regressions['status'] == 'PASS' and regressions['full_suite'] and regressions['exe_sha256'] == expected
proof = json.loads((w / 'p501-save-proof.json').read_text())
assert proof['status'] == 'PASS' and proof['exe_sha256'] == expected and not proof['diagnostic']
assert proof['audio_driver'] == 'native' and proof['actual_audio_driver'] == 'wasapi'
assert proof['scope'] == 'trusted_p501_ready' and proof['slot'] == 26 and proof['metadata_listed']
assert proof['payload_bytes'] == proof['truncations'] == proof['corruptions'] == 5896
assert proof['future_outcome_checks'] >= 3
for key, expected_count in dict(world_states=6, background_identities=7, cross_world_histories=15,
                          strike_histories=3, input_windows=8, vesta_pauses=1, poll_timer_cases=24).items():
    assert proof[key] == expected_count, key
for key in ('boundaries', 'history_boundaries', 'busy_rejections', 'successor_checks', 'invalid_states', 'natural_voice_ends'):
    assert proof[key] > 0, key
assert proof['music_restart'] and proof['extended_atomic_state'] and proof['variant_fixture_unchanged']
previous = json.loads((w / 'p504-previous-slot-proof.json').read_text())
assert previous['status'] == 'PASS' and previous['exe_sha256'] == expected and previous['unchanged']
assert previous['origin_commit'] == '1af25c6ced7b315e2c7bbd7bba3c58d125a0c022'
assert previous['slot_sha256'] == '4aaf608d8ac4d18002db155344665cdcea70c0eea7e08637ba2a700bad392e77'
for source, destination, marker in (
    ('p501-saves.log', 'p501-saves-runtime.log', 'P501 save verification: PASS'),
    ('p501-saves-startup.log', 'p501-saves-startup.log', 'P501 startup save: PASS'),
    ('p504-previous-slot.log', 'p504-previous-slot.log', 'P504 startup save: PASS')):
    path = w / source
    text = path.read_text()
    assert path.stat().st_mtime > exe.stat().st_mtime
    assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
    assert 'Using SDL Audio Driver "wasapi"' in text
    shutil.copy2(path, r / 'evidence' / destination)
for name in ('p501-save-proof.json', 'p504-previous-slot-proof.json'):
    shutil.copy2(w / name, r / 'evidence' / name)
validation = dict(proof)
validation.update(date=datetime.now().date().isoformat(), format_version=27, scene=501, full_suite=True,
                  compatibility='Versions1-26 retained; genuine frozen verified v26 slot25 read unchanged',
                  limitations=['Stopped ready-to-pitch boundaries with original poll index0/7 only',
                               'Active pitches, generated cleanup, won/completion transitions and foreground audio excluded',
                               'Ambient sample cursor restarts; complete manual audiovisual playthrough outstanding'])
(r / 'evidence/p501-saves-validation.json').write_text(json.dumps(validation, indent=2))
subprocess.run([sys.executable, str(r / 'probe_p501_save.py'), '--out', str(r / 'evidence/p501-save-original.json')], check=True)
subprocess.run([sys.executable, str(w / 'finish_p504_saves.py')], check=True)
heading = ('# Ripresa: salvataggi P501,28 ottobre2026\n\n'
           f'Formato v27:5896byte,{proof["boundaries"]} ripristini verificati. '
           'Conserva i confini pronti al lancio, il poll originale0/7, sette identita di sfondo, '
           'la storia dei fotogrammi nascosti e dei movimenti privati della palla. '
           'Slot26 in nuovo processo, metadata, vero slotv26 congelato e suite completa WASAPI sullo stesso eseguibile PASS.\n'
           'Voli, pulizia generata in coda, voci in primo piano e completamento esclusi. '
           '31/35 scene con salvataggi verificati (88.6% della copertura salvataggi). '
           'Indice complessivo e criteri di accettazione: PROJECT-PROGRESS.md; nessuna stima delle ore residue. '
           'Restano altri salvataggi,tipografia aiuto e verifica audiovisiva manuale integrale. Automazione PAUSED.\n\n')
p = r / 'NEXT-STEPS.md'
text = p.read_text()
if not text.startswith('# Ripresa: salvataggi P501'):
    p.write_text(heading + text)
model = next((line for line in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if line.startswith('Modello dichiarato')),
             "Modello dichiarato dall'utente: GPT-6.1 Sol, ragionamento medio. Nessun cambio automatico applicato.")
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,28 ottobre2026\n\n' + model + '\n\n' + heading +
    'Originali D:/astro; cleanroom dal13settembre2026. Checkpoint:finish_p501_saves.py; non eseguire finalizzatori precedenti da soli.\n')
p = r / 'P501-SAVE-PLAN.md'
p.write_text(p.read_text().replace('Status: isolated real-engine implementation under validation. No production save claim until the complete native closing gate passes.',
                                 'Status: same-build native WASAPI and complete compatibility verification PASS28October2026. Publication requires the separate export gate.'))
p = r / 'P501-SAVE-FORMAT.md'
official = '\n\n## Official same-build verification,28 October2026\n\n'
text = p.read_text()
text = text.replace('Status: isolated actual-engine candidate; native proof and independent final review pending.',
                    'Status: complete same-build native WASAPI verification PASS; publication requires the separate export gate.')
text = text.replace('Status: actual isolated engine authored and compiled; native save proof, fresh-process proof and final independent review remain pending. No canonical integration is approved.',
                    'Status: complete same-build native WASAPI verification PASS; publication requires the separate export gate.')
text = text.replace('# P501 ready-state staged format27', '# P501 ready-state save format27')
if official not in text:
    p.write_text(text.rstrip() + official + 'Complete same-build native WASAPI suite,fresh-process slot26,metadata and unchanged genuine frozen v26slot25 PASS. '
                 'Only the explicit trusted_p501_ready scope is verified; earlier candidate entries remain historical evidence.\n')
note = ('\n\n## P501 saves,28 October2026\n\nVersion27 preserves stopped ready-to-pitch boundaries, literal original poll0/7, '
        'seven background identities,all605runner words,independent sprite records and retained private ball/Comet/Jupiter history. '
        'All5896truncations/corruptions,fresh-process slot26 and genuine frozen v26slot25 plus complete native WASAPI suite PASS. '
        'Active pitches,generated cleanup,foreground voice and completion remain excluded.\n')
for name in ('README.md', 'SAVE-RESEARCH.md'):
    p = r / name
    text = p.read_text()
    if '## P501 saves,28 October2026' not in text:
        p.write_text(text + note)
for name in ('record_save_coverage.py', 'refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(w / name)], check=True)
(r / 'RUN-IN-PROGRESS.md').write_text('P501v27 ready-to-pitch native saves verified28October2026; complete same-build WASAPI suite PASS. Publication requires export verification. Newest finisher finish_p501_saves.py; automation PAUSED.\n')
print('P501v27 main-build native checkpoint PASS', flush=True)
