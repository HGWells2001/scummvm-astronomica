"""Record v16 only after the complete exact-build P522/older native suite."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

r = Path('outputs/astronomica-cleanroom')
w = Path('work/fresh-20260913')
exe = w / 'build/Releasex64/scummvm.exe'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
model = next(x for x in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if x.startswith('Modello dichiarato'))
proof = json.loads((w / 'probe-save-proof.json').read_text())
assert proof['status'] == 'PASS' and proof['exe_sha256'] == digest(exe)
assert proof['metadata_listed'] and proof['slot'] == 15 and not proof['diagnostic']
assert proof['audio_driver'] == 'native' and proof['actual_audio_driver'] == 'wasapi'
assert proof['truncations'] == proof['corruptions'] == 4472
assert proof['boundaries'] > 0 and proof['invalid_states'] > 0 and proof['variant_fixture_unchanged']
previous = json.loads((w / 'universe-previous-slot-proof.json').read_text())
assert previous['status'] == 'PASS' and previous['unchanged'] and previous['exe_sha256'] == digest(exe)
for name, marker in (
    ('probe-saves.log', 'probe save verification: PASS'),
    ('probe-saves-startup.log', 'probe startup save: PASS'),
    ('universe-previous-slot.log', 'universe startup save: PASS')
):
    p = w / name
    text = p.read_text()
    assert p.stat().st_mtime > exe.stat().st_mtime and marker in text and 'FAIL' not in text
    assert 'Log closed successfully' in text and 'Using SDL Audio Driver "wasapi"' in text
for src, dst in (
    ('probe-saves.log', 'probe-saves-runtime.log'), ('probe-saves-startup.log', 'probe-saves-startup.log'),
    ('probe-save-proof.json', 'probe-save-proof.json'), ('universe-previous-slot.log', 'universe-previous-slot.log'),
    ('universe-previous-slot-proof.json', 'universe-previous-slot-proof.json')
):
    shutil.copyfile(w / src, r / 'evidence' / dst)
validation = dict(proof)
validation.update(date='2026-10-22', format_version=16, payload_bytes=4472, scene=522,
    full_suite=True, fresh_process_slot=15, byte_corruptions=proof['corruptions'],
    invalid_checksummed_states=proof['invalid_states'], scope='ordinary_nonflight_local1_zero',
    compatibility='Versions1-15 retained; frozen verified v15 universe slot read unchanged',
    limitations=['Only ordinary local1=0 boundaries with the trusted recurring poll at index6',
        'Flight, expiry, special-hit success and deferred index0 work remain unsavable',
        'Ambient sample restarts from beginning', 'No complete manual audiovisual playthrough'])
(r / 'evidence/probe-saves-validation.json').write_text(json.dumps(validation, indent=2))
# Refresh source references after promotion; this does not execute the original program.
subprocess.run([sys.executable, str(r / 'probe_p522_save.py'), 'D:/astro'], check=True)
subprocess.run([sys.executable, str(w / 'finish_universe_saves.py')], check=True)
heading = (
    '# Ripresa: salvataggi sonda P522,22 ottobre2026\n\n'
    f'Formato v16:4472 byte,{proof["boundaries"]} ripristini/successori verificati. '
    'Conserva calendario, orbite attive, sonda nascosta, timer del poll originale200ms, '
    'stato dormiente degli altri puzzle e cometa. Slot15 in un nuovo processo PASS.\n'
    'Sono supportati solo confini ordinari senza volo con local1=0 e poll fidato index6. '
    'Volo, expiry, successo speciale e fase differita index0 restano esclusi.\n'
    'Compatibilita v1-v15, vero slotv15 congelato, rifiuto atomico dei file alterati, '
    'suite completa WASAPI e avvio normale verificati sullo stesso eseguibile.\n'
    'Checkpoint:finish_probe_saves.py;check_probe_saves.py;check_probe_regressions.py;P522-SAVE-FORMAT.md. '
    'Non eseguire finalizzatori precedenti da soli.\n'
    'Venti scene con salvataggi verificati non misurano il completamento globale. '
    'Restano altri salvataggi, tipografia aiuto e verifica audiovisiva manuale integrale. '
    'Automazione PAUSED; preferenze e salvataggi personali intatti.\n\n')
p = r / 'NEXT-STEPS.md'
s = p.read_text()
p.write_text(s if s.startswith('# Ripresa: salvataggi sonda P522') else heading + s)
Path('AI_MODEL_CHECKPOINT.md').write_text(
    '# Astronomica: checkpoint AI,22 ottobre2026\n\n' + model + '\n\n' + heading +
    'Originali D:/astro; solo cleanroom dal13settembre2026, senza prototipi o tentativi esclusi. '
    'Controllare entrambe le quote e fermarsi vicino1% della limitante. Nessun acquisto o riscatto reset.\n')
p = r / 'P522-SAVE-FORMAT.md'
s = p.read_text()
s = s.replace('Status: candidate, SDL only; official native suite pending.',
    'Status: verified22October2026; official native WASAPI and complete compatible suite PASS on the same executable.')
p.write_text(s)
p = r / 'P522-SAVE-PLAN.md'
s = p.read_text()
plan_note = ('## Verified ordinary nonflight save support,22 October2026\n\n'
    'Version16 is implemented and verified; see P522-SAVE-FORMAT.md and evidence/probe-saves-validation.json. '
    'Only local1=0 boundaries with the trusted index6 poll are supported. '
    'The inventory and proposed contract below remain research history.\n\n')
p.write_text(s if s.startswith(plan_note) else plan_note + s)
note = (
    '\n\n## P522 nonflight probe saves,22 October2026\n\n'
    f'Version16 preserves ordinary P522 state across {proof["boundaries"]} measured native round trips/successors, '
    'with a fresh-process slot15 and unchanged verified v15 slot compatibility. '
    'The original recurring200ms poll epoch, active orbit/frame phases and calendar are retained. '
    'Flight, expiry, special-hit success and the deferred index0 phase remain excluded. '
    'All4472 truncations and4472 byte corruptions reject atomically. '
    'The complete compatible native WASAPI suite passes on the same executable.\n')
for name in ('README.md', 'SAVE-RESEARCH.md'):
    p = r / name
    s = p.read_text()
    p.write_text(s if '## P522 nonflight probe saves,22 October2026' in s else s + note)
for name in ('record_save_coverage.py', 'refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(w / name)], check=True)
(r / 'RUN-IN-PROGRESS.md').write_text(
    'P522 v16 ordinary nonflight saves verified22October2026. Complete same-build native WASAPI suite, '
    'fresh-process slot15 and prior v15 slot PASS. Publication still requires export verification. '
    'Newest finisher finish_probe_saves.py. Automation remains PAUSED.\n')
print('P522 v16 nonflight save checkpoint PASS')
