"""Verify P518's custom command, callback pointers and puzzle gates from originals."""
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
custom = next(s for s in symbols if s['name'] == '_do_custom')
base = custom['file_offset']-custom['offset']
dispatch = {struct.unpack_from('<I',exe,base+0x72a0+4*i)[0]:struct.unpack_from('<H',exe,base+0x731c+2*i)[0] for i in range(31)}
assert dispatch[12] == 0x2427
modes = {struct.unpack_from('<I',exe,base+0x722e+4*i)[0]:struct.unpack_from('<H',exe,base+0x7236+2*i)[0] for i in range(2)}
assert modes == {0:0x246a,1:0x25a7}
size = struct.unpack_from('<H',exe,0x292+8*(custom['segment']-1))[0]
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
assert relocations[0x246e] == (3,0x15fd)
assert relocations[0x25ba] == (3,0x2036)
functions = {}
for name,length in [('_fxm_set_idplanet',52),('_fxm_move_idplanet',637)]:
    s = next(s for s in symbols if s['name'] == name)
    code = exe[s['file_offset']:s['file_offset']+length]
    functions[name] = dict(segment=s['segment'],offset=hex(s['offset']),length=length,sha256=hashlib.sha256(code).hexdigest())
raw = (args.root/'PLACES/P518/MEGAFILE.HYP').read_bytes()
scene = parse(raw)
assert len(scene['sprites']) == 32 and len(scene['scripts']) == 3
assert scene['sprites'][8]['move_data'] == [10,0,2,1,0]
assert scene['sprites'][8]['rect'] == [10,270,640,0]
assert [s['frame_data'] for s in scene['sprites'][9:18]] == [[50,1,0]]*9
assert scene['scripts'][1][0]['opcode'] == 39 and scene['scripts'][1][0]['args'] == [1,1,1,2]
assert scene['scripts'][2][0]['args'] == [12,0,0,0,0,0]
click = scene['sprites'][7]['click']
assert any(c['opcode'] == 31 and c['args'] == [1,3,9,0,0,0] for c in click)
assert any(c['opcode'] == 23 and c['args'] == [25,0,0,0,0,0] and c['delay'] == 6500 for c in click)
assert any(c['opcode'] == 5 and c['args'] == [388] for c in click)
answers = {i:[v for v in range(1,16) if v+i == 10 or v-i == 9] for i in range(1,10)}
args.out.write_text(json.dumps(dict(scene=518,resource_sha256=hashlib.sha256(raw).hexdigest(),custom12='4:2427-2664',modes=modes,callbacks=functions,launcher_sprite=9,planet_sprite='local2+9',answers=answers,success_global=34,destination=388,semantics=dict(follow='proposed point uses previous delta; callback copies sprite9 velocity for next step',release='set delta(-2,0); retain runtime period and timestamp',arrival='old rectangle center, after bounce velocity update',correct='direct S10; stop movement, retain visibility and animation',wrong='direct S9; hide and subtract 2^(id-1) from local1',success_count='local3 incremented at release, before arrival')),indent=2))
print('Original P518 evidence: PASS (dispatch, callbacks, nine planets and answer pairs)')
