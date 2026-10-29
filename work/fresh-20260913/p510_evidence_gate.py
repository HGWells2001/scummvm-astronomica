"""Read-only official P510 closure gate; absence preserves the prior baseline."""
from pathlib import Path
import hashlib
import json


def validated_p510(root, work):
    root, work = Path(root), Path(work)
    validation = root / 'evidence/p510-saves-validation.json'
    if not validation.is_file():
        return None
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    read = lambda name: json.loads((root / 'evidence' / name).read_text())
    v, proof, old = map(read, ('p510-saves-validation.json', 'p510-save-proof.json', 'p501-v27-previous-slot-proof.json'))
    expected = digest(work / 'build/Releasex64/scummvm.exe')
    from p510_ordinary_gate import validated_ordinary
    ordinary_path = root / 'evidence/p510-ordinary-entry/ordinary-entry-gate-proof.json'
    validated_ordinary(ordinary_path, ordinary_path.parent, expected)
    assert v['ordinary_entry_proof_sha256'] == digest(ordinary_path)
    assert v['status'] == proof['status'] == old['status'] == 'PASS'
    assert v['full_suite'] and not v['diagnostic'] and not proof['diagnostic']
    assert v['exe_sha256'] == proof['exe_sha256'] == old['exe_sha256'] == expected
    for state in (v, proof):
        assert state['scope'] == 'trusted_p510_ordinary_countdown'
        assert state['format_version'] == 28 and state['slot'] == 27
        assert state['payload_bytes'] == state['truncations'] == state['corruptions'] == 4540
        assert state['invalid_states'] == 23 and state['cross_destinations'] == 7
        assert state['starts'] == state['commits'] and state['original_routes'] == 8
        assert state['actual_audio_driver'] == 'wasapi'
        assert all(state[key] for key in ('metadata_listed', 'fresh_process', 'fresh_slot_unchanged', 'paused_source_save', 'paused_recipient_load', 'fixtures_unchanged'))
    assert v['slot_sha256'] == proof['slot_sha256'] == digest(work / 'p510-save-regression/astro-verify.027')
    assert v['log_sha256'] == proof['log_sha256']
    for stem, name, marker in (
        ('p510-saves', 'p510-saves-runtime.log', 'P510 ASVM28 malformed atomic: PASS'),
        ('p510-saves-startup', 'p510-saves-startup.log', 'P510 ASVM28 fresh physical continuation: PASS')):
        path = root / 'evidence' / name
        text = path.read_text()
        assert digest(path) == proof['log_sha256'][stem]
        assert marker in text and 'FAIL' not in text
        assert 'Using SDL Audio Driver "wasapi"' in text and text.rstrip().endswith('--- Log closed successfully.')
    assert 'P510 native paused continuation' in (root / 'evidence/p510-saves-list.log').read_text()
    frozen = work / 'verified-checkpoints/p501-025e82d8bd3b/frozen-slot26/astro-verify.026'
    assert old['unchanged'] and old['audio_driver'] == 'wasapi'
    assert old['origin_commit'] == 'ad2ec32fa658919c65e920c2c2609d3610061acd'
    assert old['producing_exe_sha256'] == '025e82d8bd3b8e267bccec7d4c3e044d37d87049dbeeadd9b4158187573d91d3'
    assert old['slot_sha256'] == digest(frozen) == 'adcc9b9be47d0b7153a94eb3b9883b85a12090fbd64e8793e32e61daeeea81fa'
    old_log = root / 'evidence/p501-v27-previous-slot.log'
    text = old_log.read_text()
    assert digest(old_log) == old['log_sha256'] and 'P501 startup save: PASS' in text and 'FAIL' not in text
    assert 'Using SDL Audio Driver "wasapi"' in text and text.rstrip().endswith('--- Log closed successfully.')
    return v, proof
