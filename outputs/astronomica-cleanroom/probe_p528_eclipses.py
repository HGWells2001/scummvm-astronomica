"""Extract all custom-18 moon positions directly from the original x86 code."""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from astro_reader import parse

ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--deps', type=Path, default=Path('work/fresh-20260913/deps-verified'))
args = ap.parse_args()
sys.path.insert(0,str(args.deps.resolve()))
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
exe = (args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols = json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
custom = next(s for s in symbols if s['name'] == '_do_custom')
base = custom['file_offset']-custom['offset']
dispatch = {struct.unpack_from('<I',exe,base+0x72a0+4*i)[0]:struct.unpack_from('<H',exe,base+0x731c+2*i)[0] for i in range(31)}
assert dispatch[18] == 0x3a3c
modes = {struct.unpack_from('<I',exe,base+0x71f2+4*i)[0]:struct.unpack_from('<H',exe,base+0x71fa+2*i)[0] for i in range(2)}
assert modes == {0:0x3a70,1:0x444c}
md = Cs(CS_ARCH_X86, CS_MODE_16)
rows = {}
phase = quadrant = None
pushes = []
for ins in md.disasm(exe[base+0x3a70:base+0x4449],0x3a70):
    if ins.mnemonic == 'cmp':
        m = re.fullmatch(r'dword ptr es:\[bx \+ (0x3f8|0x3fc)\], (0x[0-9a-f]+|\d+)',ins.op_str)
        if m:
            if m[1] == '0x3f8': phase = int(m[2],0)
            else: quadrant = int(m[2],0); pushes = []
    if ins.mnemonic == 'push' and re.fullmatch(r'0x[0-9a-f]+|\d+',ins.op_str):
        pushes.append(int(ins.op_str,0))
    if ins.mnemonic == 'lcall':
        assert len(pushes) == 2 and (phase,quadrant) not in rows
        rows[phase,quadrant] = [pushes[1],pushes[0]]
assert len(rows) == 48 and set(rows) == {(p,q) for p in range(12) for q in range(4)}
table = [[rows[p,q] for q in range(4)] for p in range(12)]
digest = 2166136261
for p in range(12):
    for q in [3,2,1,0]:
        for byte in struct.pack('<hh',*rows[p,q]): digest = ((digest ^ byte)*16777619)&0xffffffff
raw = (args.root/'PLACES/P528/MEGAFILE.HYP').read_bytes()
s = parse(raw)
assert s['conditions'][:3] == [[1,0,13,11,0,13],[1,1,4,0,0,4],[1,2,4,0,0,4]]
assert len(s['sprites']) == 9 and s['sprites'][8]['xy'] == [447,48]
args.out.write_text(json.dumps(dict(resource_sha256=hashlib.sha256(raw).hexdigest(),handler='4:3a3c-4520',handler_sha256=hashlib.sha256(exe[base+0x3a3c:base+0x4523]).hexdigest(),positions=table,click_order_hash=hex(digest),position_target_sprite=9,stored_coordinates_unchanged=True,first_flag_pairs=[[0,1],[6,3]],second_flag_pairs=[[0,3],[6,1]],direct_sound_files=[8,9,10],solved_local=2,solved_global=44,solved_destination=526,unsolved_destination=268),indent=2))
print('Original P528 eclipse positions: PASS',hex(digest))
