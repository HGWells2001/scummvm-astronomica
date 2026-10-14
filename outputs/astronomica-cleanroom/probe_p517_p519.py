"""Check animation/flash inputs against original resources and executable."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from astro_reader import parse

ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
exe = (args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols = json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
execute = next(s for s in symbols if s['name'] == '_execute_command')
base = execute['file_offset']-execute['offset']
dispatch = {struct.unpack_from('<I',exe,base+0x187a+4*i)[0]:struct.unpack_from('<H',exe,base+0x193a+2*i)[0] for i in range(48)}
assert dispatch[19] == 0x827 and dispatch[30] == 0xb2d
flash = next(s for s in symbols if s['name'] == '_flash_white')
assert flash['segment'] == 18 and flash['offset'] == 0x1652
flash_code = exe[flash['file_offset']:flash['file_offset']+0x172a-0x1652]
assert bytes.fromhex('68 ff ff ff 00') in flash_code

def commands(value):
    if isinstance(value, dict):
        if 'opcode' in value:
            yield value
        else:
            for item in value.values():
                yield from commands(item)
    elif isinstance(value, list):
        for item in value:
            yield from commands(item)

rows = []
for place in [517,519]:
    raw = (args.root/f'PLACES/P{place}/MEGAFILE.HYP').read_bytes()
    scene = parse(raw)
    ops = list(commands(scene))
    if place == 517:
        timers = sorted({tuple(c['args']) for c in ops if c['opcode'] == 19})
        assert timers == [(9,100,1,0),(10,100,1,0),(11,300,1,0)]
        assert {c['args'][0] for c in ops if c['opcode'] == 30} == {9,10,11}
        assert any(c['opcode'] == 5 and c['args'] == [512] for c in ops)
        assert any(c['opcode'] == 5 and c['args'] == [157] for c in ops)
    else:
        assert len(scene['mouse_rects']) == 10
        assert sum(c['opcode'] == 21 for c in ops) == 3
        assert any(c['opcode'] == 5 and c['args'] == [281] for c in ops)
        for detector, target, flag in [(9,1,2),(7,3,3),(5,4,4),(6,0,5),(8,2,6)]:
            assert any(c['opcode'] == 32 and c['args'] == [1,flag,1] for c in scene['mouse_rects'][target]['click'])
            assert any(c['opcode'] == 32 and c['args'][:2] == [1,0] for c in scene['mouse_rects'][detector]['click'])
    rows.append(dict(scene=place,resource_sha256=hashlib.sha256(raw).hexdigest(),command_count=len(ops),entry_templates=len(scene['scripts'])))
args.out.write_text(json.dumps(dict(resources=rows,animation_entry='15:0827',stop_entry='15:0b2d',flash_entry='18:1652',flash_sha256=hashlib.sha256(flash_code).hexdigest(),runtime_evidence='runtime.log: P517/P519 interaction verification'),indent=2))
print('Original P517/P519 animation, flash and route inputs: PASS')
