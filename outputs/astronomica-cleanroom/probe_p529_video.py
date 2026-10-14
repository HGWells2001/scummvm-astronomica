"""Read P529's four outcomes and movie segments directly from original files."""
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
raw = (args.root/'PLACES/P529/MEGAFILE.HYP').read_bytes()
s = parse(raw)
assert s['movies'] == ['FUNIV.MOV']
assert s['conditions'] == [[1,0,16,0,0,15],[1,1,1,0,0,1],[1,2,1,0,0,0],[1,3,4,0,0,15]]
segments = [c['args'][1:] for c in s['scripts'][2] if c['opcode'] == 37]
assert segments == [[0,359],[1029,232],[720,226],[360,359]]
assert [c['args'] for c in s['scripts'][2] if c['opcode'] == 3] == [[0,160,40,0]]
assert [c['args'] for c in s['scripts'][1] if c['opcode'] == 33] == [[1,3,2,1],[1,3,3,1],[1,3,1,1],[1,3,0,1]]
assert [c['args'] for c in s['scripts'][2] if c['opcode'] == 19] == [[11,20,1,0],[10,20,1,0],[9,20,1,0],[11,-1,1,0],[10,-1,1,0],[9,-1,1,0]]
b = (args.root/'PLACES/P529/FUNIV.MOV').read_bytes()
def atoms(start,end):
    while start+8 <= end:
        size,kind = struct.unpack_from('>I4s',b,start)
        assert size >= 8 and start+size <= end
        if kind == b'mvhd': yield struct.unpack_from('>II',b,start+20)
        if kind == b'moov': yield from atoms(start+8,start+size)
        start += size
headers = list(atoms(0,len(b)))
assert headers == [(30,1261)]
assert all(a+n <= 1261 for a,n in segments)
exe = (args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols = json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
custom = next(x for x in symbols if x['name'] == '_do_custom')
base = custom['file_offset']-custom['offset']
dispatch = {struct.unpack_from('<i',exe,base+0x6c94+4*i)[0]:struct.unpack_from('<H',exe,base+0x6c94+4*i+2*(34-i)+0x44)[0] for i in range(34)}
assert dispatch[529] == 0x5a34
success = exe[base+0x5a34:base+0x5a64]
assert bytes.fromhex('66 26 83 bf be 00 00') in success
assert bytes.fromhex('66 26 c7 87 be 00 01 00 00 00') in success
assert bytes.fromhex('66 26 c7 87 fa 00 01 00 00 00') in success
args.out.write_text(json.dumps(dict(resource_sha256=hashlib.sha256(raw).hexdigest(),movie_sha256=hashlib.sha256(b).hexdigest(),movie='PLACES/P529/FUNIV.MOV',timescale=30,duration_ticks=1261,segments=segments,position=[160,40],selector_range=[0,15],outcome_groups=[[1,5],[6,8],[9,12],[13,15]],completed_mask=15,early_success_group=[6,8],destination=98,digit_timer_ms=20,digit_stop_delay_ms=4000,success_handler='4:5a34-5a62',success_global=45,additional_unlock_global=60,success_handler_sha256=hashlib.sha256(success).hexdigest()),indent=2))
print('Original P529 movie, selection and outcome inputs: PASS')
