"""Inventory current original P527 resource and assets; no executable is run."""
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
folder = args.original_root / 'PLACES/P527'
path = folder / 'MEGAFILE.HYP'
raw = path.read_bytes()
sha = lambda data: hashlib.sha256(data).hexdigest()
assert len(raw) == 348102 and sha(raw) == '03df944bdc8dffc6780ba324c6879b7cd91529e741637dd7c59acde220aad6a4'
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
assert len(scene['sprites']) == 9 and len(commands) == 82
assets = [dict(name=p.name, size=p.stat().st_size, sha256=sha(p.read_bytes()))
          for p in sorted(folder.iterdir()) if p.is_file() and p != path]
movie = next(asset for asset in assets if asset['name'].upper() == 'FLATRING.MOV')
assert movie['sha256'] == 'f33e62405662875f3fd1d85087f19954f4d334a3235d528f53facd404dd3b4f3'
result = dict(status='STATIC_ORIGINAL_INVENTORY_ONLY', source=dict(path=str(path), size=len(raw), sha256=sha(raw)),
              reader_sha256=sha((research / 'astro_reader.py').read_bytes()), sprite_count=9,
              command_count=len(commands), commands=commands, conditions=scene['conditions'], assets=assets,
              sprites=[{key: value for key, value in sprite.items() if key != 'frames'} for sprite in scene['sprites']],
              limitations=['Static original resource profile; no original executable or native save test was run'])
args.out.write_text(json.dumps(result, indent=2))
print('Original P527 static profile PASS:9 sprites,82 commands; separate from native save proof')
