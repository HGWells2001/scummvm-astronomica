"""Profile the whole original P501 resource and all direct assets, separately from native proof."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

sys.dont_write_bytecode = True
research = Path(__file__).resolve().parent
sys.path.insert(0, str(research))
from astro_reader import parse

ap = argparse.ArgumentParser()
ap.add_argument('--original-root', type=Path, default=Path('D:/astro'))
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
folder = args.original_root / 'PLACES/P501'
path = folder / 'MEGAFILE.HYP'
raw = path.read_bytes()
sha = lambda data: hashlib.sha256(data).hexdigest()
assert len(raw) == 786726
assert sha(raw) == 'fe46b4707b6c4bb1f8df9e31fed8b7af103e3839702d88c5e30c331f71877b41'
scene = parse(raw)
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
assert len(scene['sprites']) == 27 and len(commands) == 259
assert len(scene['scripts']) == 1 and len(scene['scripts'][0]) == 8
assets = []
for item in sorted(folder.iterdir()):
    if not item.is_file() or item == path:
        continue
    data = item.read_bytes()
    row = dict(name=item.name, size=len(data), sha256=sha(data))
    if data[:2] == b'BM':
        assert data[:2] == b'BM' and len(data) == 205878
        width, height, planes, bpp, compression = struct.unpack_from('<iiHHI', data, 18)
        assert (width, height, planes, bpp, compression) == (640, 320, 1, 8, 0)
        row['bitmap_header'] = dict(width=width, height=height, planes=planes, bpp=bpp, compression=compression)
    assets.append(row)
assert {a['name'] for a in assets if 'bitmap_header' in a} == {
    'BACKORBI', 'PHOBOS', 'BLACKDWA', 'JUPITER', 'VESTA', 'MOON'}
result = dict(status='STATIC_ORIGINAL_INVENTORY_ONLY',
              source=dict(path=str(path), size=len(raw), sha256=sha(raw)),
              reader_sha256=sha((research / 'astro_reader.py').read_bytes()),
              full_parse=True, sprite_count=27, command_count=len(commands), commands=commands,
              conditions=scene['conditions'], startup_scripts=scene['scripts'], assets=assets,
              structured_prefix=dict(size=len(raw), sha256=sha(raw)),
              opaque_tail=dict(offset=len(raw), size=0, sha256=sha(b'')),
              sprites=[{k: v for k, v in sprite.items() if k != 'frames'} for sprite in scene['sprites']],
              background_identities=['', 'backorbi', 'phobos', 'blackdwa', 'jupiter', 'vesta', 'moon'],
              limitations=['Static original data profile; no original executable or native save test was run',
                           'Bitmap header and byte identity checks do not establish displayed pixel fidelity',
                           'Only direct asset files are inventoried; subdirectories are outside this profile'])
args.out.write_text(json.dumps(result, indent=2))
print('Original P501 full static profile PASS:27 sprites,259 commands,8-command poll,six external BMPs')
