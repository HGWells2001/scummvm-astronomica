"""Fresh static profile of the original P504 resource and its direct assets."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

sys.dont_write_bytecode = True
research = Path(__file__).resolve().parent
sys.path.insert(0, str(research))
from astro_reader import parse

ap = argparse.ArgumentParser()
ap.add_argument('--original-root', type=Path, default=Path('D:/astro'))
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
folder = args.original_root / 'PLACES/P504'
path = folder / 'MEGAFILE.HYP'
raw = path.read_bytes()
sha = lambda data: hashlib.sha256(data).hexdigest()
assert len(raw) == 805459 and sha(raw) == 'dde86ef89aa520e16d006b41ddefece537f81901ad3e8db13c5a3bbe5e6009ba'
# The strict reader consumes the current structured resource up to this boundary.
# Preserve the remaining original bytes as an opaque tail, never claim full parsing.
structured_bytes = 0xa04d3
scene = parse(raw[:structured_bytes])
commands = []

def walk(value, location):
    if isinstance(value, dict):
        if 'opcode' in value:
            commands.append(dict(location=location, **value))
        for key, child in value.items():
            walk(child, location + '/' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, location + '/' + str(index))

walk(scene, 'scene')
assert len(scene['sprites']) == 45 and len(commands) == 225
assets = [dict(name=p.name, size=p.stat().st_size, sha256=sha(p.read_bytes()))
          for p in sorted(folder.iterdir()) if p.is_file() and p != path]
result = dict(status='STATIC_ORIGINAL_INVENTORY_ONLY', source=dict(path=str(path), size=len(raw), sha256=sha(raw)),
              reader_sha256=sha((research / 'astro_reader.py').read_bytes()), sprite_count=45,
              command_count=len(commands), commands=commands, conditions=scene['conditions'], assets=assets,
              structured_prefix=dict(size=structured_bytes, sha256=sha(raw[:structured_bytes])),
              opaque_tail=dict(offset=structured_bytes, size=len(raw)-structured_bytes,
                               sha256=sha(raw[structured_bytes:]), interpretation='Not decoded by this profile'),
              sprites=[{key: value for key, value in sprite.items() if key != 'frames'} for sprite in scene['sprites']],
              limitations=['Static current original resource profile; no original executable or native save test was run',
                           'The structured prefix is parsed completely; the148864-byte original tail remains opaque',
                           'Only direct asset files are inventoried; the WIN subdirectory is outside this profile'])
args.out.write_text(json.dumps(result, indent=2))
print('Original P504 static profile PASS:45 sprites,225 commands; separate from native save proof')
