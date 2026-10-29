"""Require actual original normal entry on the same executable as save coverage."""
from pathlib import Path
import hashlib, json, re


def validated_ordinary(proof_path, logdir, expected, slot=None):
    proof_path, logdir = Path(proof_path), Path(logdir)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    p = json.loads(proof_path.read_text())
    assert p['status'] == 'PASS' and p['scope'] == 'actual_ordinary_entry_retained_disabled_loop0'
    assert p['exe_sha256'] == expected and p['actual_audio_driver'] == 'wasapi'
    assert p['entry_scripts'] and p['source_loop_id'] == p['fresh_loop_id'] == 0
    assert p['loop_enabled'] is False and p['manual_startup_enqueue'] is False
    assert p['intro_id'] == 300 and p['actual_intro_starts'] == 1 and p['original_startup_programs_queued'] == 4
    assert 1 <= p['ordinary_ready_count'] <= 51
    assert p['format_version'] == 28 and p['payload_bytes'] == 4540 and p['slot'] == 27
    assert all(p[key] for key in ('intro_drained','paused_source_byte_roundtrip','fresh_entry_true','fresh_entry_false','no_intro_replay','metadata_listed'))
    assert p['s0_sha256'] == 'ce810e10b319f0ef6fe1f93b61b868baa1446506d008a9e6569628f8f37f313f'
    assert p['s300_sha256'] == 'f1b28eab8ff17d5ca704a161c26d3c9a7320785dca1647921d17a9e0520db12a'
    for label, sha in p['log_sha256'].items():
        path = logdir/label
        assert digest(path) == sha
        text = path.read_text()
        if label == 'listed.log':
            assert 'P510 native paused continuation' in text
        else:
            assert 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
            assert re.findall(r'Using SDL Audio Driver "([^"]+)"', text) == ['wasapi']
            assert 'P510 ASVM28 fresh physical continuation: PASS' in text
            if label.startswith('fresh-'):
                assert 'introduction:' not in text
    initial = (logdir/'initial.log').read_text()
    assert initial.count('Astronomica P510 introduction: S300.WAV') == 1
    assert 'P510 ordinary loaded: loop0 enabled1 lastSound300 active0 starts1 queued4' in initial
    assert 'P510 entry scripts: 4 queued, 0 skipped' in initial
    assert 'P510 ordinary paused ASVM28 save: PASS' in initial
    assert 'P510 ASVM28 byte roundtrip: PASS (boundary1,4540bytes,paused source/recipient' in initial
    if slot is not None:
        assert digest(Path(slot)) == p['slot_sha256']
    return p
