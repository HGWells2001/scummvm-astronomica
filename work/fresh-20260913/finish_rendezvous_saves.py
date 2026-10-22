"""Record v17 only after the complete exact-build P514/older native suite."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

r = Path('outputs/astronomica-cleanroom')
w = Path('work/fresh-20260913')
exe = w / 'build/Releasex64/scummvm.exe'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
model = next(x for x in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if x.startswith('Modello dichiarato'))
proof = json.loads((w / 'rendezvous-save-proof.json').read_text())
assert proof['status'] == 'PASS' and proof['exe_sha256'] == digest(exe)
assert proof['metadata_listed'] and proof['slot'] == 16 and not proof['diagnostic']
assert proof['audio_driver'] == 'native' and proof['actual_audio_driver'] == 'wasapi'
assert proof['truncations'] == proof['corruptions'] == 4632
assert proof['boundaries'] > 0 and proof['invalid_states'] > 0 and proof['variant_fixture_unchanged']
previous = json.loads((w / 'probe-previous-slot-proof.json').read_text())
assert previous['status'] == 'PASS' and previous['unchanged'] and previous['exe_sha256'] == digest(exe)
for name, marker in (
    ('rendezvous-saves.log', 'rendezvous save verification: PASS'),
    ('rendezvous-saves-startup.log', 'rendezvous startup save: PASS'),
    ('probe-previous-slot.log', 'probe startup save: PASS')
):
    p = w / name
    text = p.read_text()
    assert p.stat().st_mtime > exe.stat().st_mtime and marker in text and 'FAIL' not in text
    assert 'Log closed successfully' in text and 'Using SDL Audio Driver "wasapi"' in text
for src, dst in (
    ('rendezvous-saves.log', 'rendezvous-saves-runtime.log'), ('rendezvous-saves-startup.log', 'rendezvous-saves-startup.log'),
    ('rendezvous-save-proof.json', 'rendezvous-save-proof.json'), ('probe-previous-slot.log', 'probe-previous-slot.log'),
    ('probe-previous-slot-proof.json', 'probe-previous-slot-proof.json')
):
    shutil.copyfile(w / src, r / 'evidence' / dst)
validation = dict(proof)
validation.update(date='2026-10-22', format_version=17, payload_bytes=4632, scene=514,
    full_suite=True, fresh_process_slot=16, byte_corruptions=proof['corruptions'],
    invalid_checksummed_states=proof['invalid_states'], scope='settled_rendezvous',
    compatibility='Versions1-16 retained; frozen verified v16 probe slot read unchanged',
    limitations=['Only settled P514 boundaries without queued scripts/actions or foreground audio',
        'Pending launch, successful docking and fuel-exhaustion continuations remain unsavable',
        'Ambient sample restarts from beginning', 'No complete manual audiovisual playthrough'])
(r / 'evidence/rendezvous-saves-validation.json').write_text(json.dumps(validation, indent=2))
# Refresh source references after promotion; this does not execute the original program.
subprocess.run([sys.executable, str(r / 'probe_p514_save.py'), 'D:/astro'], check=True)
subprocess.run([sys.executable, str(w / 'finish_probe_saves.py')], check=True)
heading = (
    '# Ripresa: salvataggi attracco P514,22 ottobre2026\n\n'
    f'Formato v17:4632 byte,{proof["boundaries"]} ripristini/successori verificati. '
    "Conserva orbite attive, carburante, velocita0..15, posizione nascosta dell'ultimo attracco fallito, "
    'timer e stato dormiente degli altri puzzle. Slot16 in un nuovo processo PASS.\n'
    'Sono supportati i confini senza comandi/azioni in coda, voci in primo piano o transizioni ancora attive. '
    'I periodi restano indipendenti dalla posizione e dalla fase delle animazioni.\n'
    'Compatibilita v1-v16, vero slotv16 congelato, rifiuto atomico dei file alterati, '
    'suite completa WASAPI e avvio normale verificati sullo stesso eseguibile.\n'
    'Checkpoint:finish_rendezvous_saves.py;check_rendezvous_saves.py;check_rendezvous_regressions.py;P514-SAVE-FORMAT.md. '
    'Non eseguire finalizzatori precedenti da soli.\n'
    'Ventuno scene con salvataggi verificati non misurano il completamento globale. '
    'Restano altri salvataggi, tipografia aiuto e verifica audiovisiva manuale integrale. '
    'Automazione PAUSED; preferenze e salvataggi personali intatti.\n\n')
p = r / 'NEXT-STEPS.md'
s = p.read_text()
p.write_text(s if s.startswith('# Ripresa: salvataggi attracco P514') else heading + s)
Path('AI_MODEL_CHECKPOINT.md').write_text(
    '# Astronomica: checkpoint AI,22 ottobre2026\n\n' + model + '\n\n' + heading +
    'Originali D:/astro; solo cleanroom dal13settembre2026, senza prototipi o tentativi esclusi. '
    'Controllare entrambe le quote e fermarsi vicino1% della limitante. Nessun acquisto o riscatto reset.\n')
p = r / 'P514-SAVE-FORMAT.md'
s = p.read_text()
s = s.replace('Status: candidate, SDL only; official native suite pending.',
    'Status: verified22October2026; official native WASAPI and complete compatible suite PASS on the same executable.')
s = s.replace('The candidate preserves', 'The format preserves')
s = s.replace('Until those exist this paragraph describes the verification design, not a PASS claim. SDLdummy diagnostics are not an official native-audio/full same-build suite or a manual playthrough.',
    'The official native WASAPI and complete compatible same-build suite pass; see evidence/rendezvous-save-proof.json and evidence/rendezvous-saves-validation.json for measured counts and exact identities. A complete manual audiovisual playthrough remains outstanding.')
p.write_text(s)
p = r / 'P514-SAVE-PLAN.md'
s = p.read_text()
plan_note = ('## Verified settled save support,22 October2026\n\n'
    'Version17 is implemented and verified; see P514-SAVE-FORMAT.md and evidence/rendezvous-saves-validation.json. '
    'The original inventory below remains research history.\n\n')
p.write_text(s if s.startswith(plan_note) else plan_note + s)
note = (
    '\n\n## P514 rendezvous saves,22 October2026\n\n'
    f'Version17 preserves settled P514 state across {proof["boundaries"]} measured native round trips/successors, '
    'with a fresh-process slot16 and unchanged verified v16 slot compatibility. '
    'Active orbit, frame and fuel timers, all16 speeds and hidden failed-docking history are retained. '
    'Queued launch, successful-docking and fuel-exhaustion transitions remain excluded. '
    'All4632 truncations and4632 byte corruptions reject atomically. '
    'The complete compatible native WASAPI suite passes on the same executable.\n')
for name in ('README.md', 'SAVE-RESEARCH.md'):
    p = r / name
    s = p.read_text()
    p.write_text(s if '## P514 rendezvous saves,22 October2026' in s else s + note)
for name in ('record_save_coverage.py', 'refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(w / name)], check=True)
(r / 'RUN-IN-PROGRESS.md').write_text(
    'P514 v17 settled rendezvous saves verified22October2026. Complete same-build native WASAPI suite, '
    'fresh-process slot16 and prior v16 slot PASS. Publication still requires export verification. '
    'Newest finisher finish_rendezvous_saves.py. Automation remains PAUSED.\n')
print('P514 v17 settled save checkpoint PASS')
