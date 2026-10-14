"""Verify opcode 18 and its two callback relocations in the original executable."""
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
symbol = next(s for s in symbols if s['name'] == '_execute_command')
base = symbol['file_offset']-symbol['offset']
dispatch = {struct.unpack_from('<I',exe,base+0x187a+4*i)[0]:struct.unpack_from('<H',exe,base+0x193a+2*i)[0] for i in range(48)}
assert dispatch[18] == 0x08bb
size = struct.unpack_from('<H',exe,0x292+8*(symbol['segment']-1))[0]
relocations = {}
for i in range(struct.unpack_from('<H',exe,base+size)[0]):
    typ, flags, src, segment, offset = struct.unpack_from('<BBHHH',exe,base+size+2+8*i)
    seen = set()
    while src != 65535 and src not in seen and src+2 <= size:
        seen.add(src)
        if flags & 3 == 0:
            relocations[src] = (segment,offset)
        if flags & 4:
            break
        src = struct.unpack_from('<H',exe,base+src)[0]
assert relocations[0xa02] == (7,0xc30)
assert relocations[0xa35] == (7,0xd30)
functions = {}
for name, length in [('_SWBounceSpriteMoveProc',256),('_SWWrapSpriteMoveProc',241),('_SWSetSpriteMoveTime',111)]:
    s = next(s for s in symbols if s['name'] == name)
    data = exe[s['file_offset']:s['file_offset']+length]
    functions[name] = dict(segment=s['segment'],offset=hex(s['offset']),length=length,sha256=hashlib.sha256(data).hexdigest())
raw = (args.root/'PLACES/P521/MEGAFILE.HYP').read_bytes()
scene = parse(raw)
commands = scene['sprites'][4]['click']
movement = [c['args'] for c in commands if c['opcode'] == 18]
assert len(movement) == 10 and [c[0] for c in movement] == list(range(14,24))
assert all(c[4:] == [2,0] for c in movement)
assert [c['args'][0] for c in commands if c['opcode'] == 30] == list(range(14,24))
assert all(s['rect'] == [0,320,640,0] for s in scene['sprites'][13:23])
assert any(c['opcode'] == 23 and c['args'] == [25,0,0,0,0,0] for c in scene['sprites'][2]['click'])
args.out.write_text(json.dumps(dict(executable_sha256=hashlib.sha256(exe).hexdigest(),opcode18='15:08bb-0a91',callback_relocations={'1':'7:0c30','2':'7:0d30'},functions=functions,semantics=dict(bounds_order=['top','bottom','right','left'],bounds_test='old rectangle; strict inequality',timer='signed word period; previous timestamp preserved; one step without catch-up',coordinates='render rectangle only; stored GameSprite xy unchanged',bounce='reverse runtime delta, clamp to boundary',wrap='after fully outside, place at opposite edge'),p521=dict(resource_sha256=hashlib.sha256(raw).hexdigest(),movement_commands=movement,fragment_ids=list(range(14,24)),success_choice=3,destination=388)),indent=2))
print('Original sprite motion evidence: PASS (dispatch, relocations, P521 ten fragments)')
