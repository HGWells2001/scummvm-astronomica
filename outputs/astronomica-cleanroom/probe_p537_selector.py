"""Verify selector and clone inputs directly from the original P537 resource."""
import argparse
import hashlib
import json
from pathlib import Path
from astro_reader import parse

ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
raw = (args.root / 'PLACES/P537/MEGAFILE.HYP').read_bytes()
s = parse(raw)
assert len(s['sprites']) == 48
assert s['conditions'] == [[1, 0, 16, 0, 0, 15]]
assert s['sprites'][8]['clone'] == -1
assert len(s['sprites'][8]['frames']) == 10
assert all(p['clone'] == 9 for p in s['sprites'][9:29])
for index, delta, overflow, limit in [(4, -1, -1, 0), (5, 1, 16, 15)]:
    commands = [(c['opcode'], c['args'], c['delay']) for c in s['sprites'][index]['click']]
    assert commands == [(28, [-1], 0), (9, [7], 0), (46, [1, 0, delta], 0),
                        (31, [1, 0, overflow, 0, 0, 0], 0), (32, [1, 0, limit], 0),
                        (42, [], -1), (41, [0], 0), (29, [-1], 200)]
assert any(c['opcode'] == 23 and c['args'][0] == 14 for c in s['sprites'][32]['click'])
args.out.write_text(json.dumps(dict(
    resource_sha256=hashlib.sha256(raw).hexdigest(),
    initial_value=0, minimum=0, maximum=15,
    decrement_sprite=5, increment_sprite=6,
    multi_frame_clones=list(range(10, 30)), frame_source_sprite=9,
    original_copy_evidence='_SWCloneSprite 7:0349-0358 copies 0x9d bytes of source sprite state',
    rocket_evidence='p537-rocket.json: original custom command and three movement callbacks'
), indent=2))
print('Original P537 selector and clone inputs: PASS')
