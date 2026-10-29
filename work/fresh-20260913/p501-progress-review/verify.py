"""Verify the frozen sealed-P501 acceptance snapshot without rewriting it."""
from pathlib import Path
import hashlib
import json

here = Path(__file__).resolve().parent
data = json.loads((here / 'acceptance-index.json').read_text())
assert data['scheme'] == 'astronomica-acceptance-v1'
assert [g['id'] for g in data['gates']] == ['A%02d' % i for i in range(1, 11)]
assert sum(g['status'] == 'PASS' for g in data['gates']) == 6
assert data['overall_acceptance_index']['percent'] == 60
assert data['verified_baseline']['published_commit'] == 'ad2ec32fa658919c65e920c2c2609d3610061acd'
assert data['metrics']['native_safe_save_scene_coverage']['supported'] == 31
assert data['whole_game_completion_percent'] is None
for name, expected in data['evidence_sha256'].items():
    path = here / 'baseline-evidence' / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
print('Frozen sealed-P501 acceptance integrity PASS:6/10=60%, saves31/35=88.6%')
