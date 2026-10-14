"""Pin P530's exceptional success semantics from the original executable."""
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
dispatch = {struct.unpack_from('<i',exe,base+0x6c94+4*i)[0]:struct.unpack_from('<H',exe,base+0x6c94+4*i+2*(34-i)+0x44)[0] for i in range(34)}
assert dispatch[530] == 0x5a64
code = exe[base+0x5a64:base+0x5a8a]
assert bytes.fromhex('66 26 83 bf c2 00 00') in code
assert bytes.fromhex('68 90 03') in code
assert bytes.fromhex('66 26 c7 87 c2 00 01 00 00 00') in code
success = next(s for s in symbols if s['name'] == '_puzzle_successful')
counter = exe[success['file_offset']:success['file_offset']+0x1c]
assert bytes.fromhex('66 ff 06 53 01') in counter
assert bytes.fromhex('66 ff 06 53 01') not in code
raw = (args.root/'PLACES/P530/MEGAFILE.HYP').read_bytes()
s = parse(raw)
assert s['movies'] == [] and len(s['scripts']) == 11
assert s['scripts'][0][0]['args'] == [1,13,3,0,0,0]
assert any(c['opcode'] == 5 and c['args'] == [228] for c in s['scripts'][0])
assert any(c['opcode'] == 39 and c['args'] == [1,11,1,9] for c in s['scripts'][10])
args.out.write_text(json.dumps(dict(scene=530,resource_sha256=hashlib.sha256(raw).hexdigest(),success_handler='4:5a64-5a88',handler_sha256=hashlib.sha256(code).hexdigest(),success_global=46,sound=912,sound_only_when_flag_zero=True,increments_puzzle_counter=False,global_sound_12_synchronous='9:3b62-3b85 selects flags 2',completion_gate=dict(local=13,value=3),destination=228,random_choice=dict(mask_local=11,value_local=9,width=5),status='Original evidence; implemented route verified separately by native runtime tests'),indent=2))
print('Original P530 special success: PASS (global46, S12, no puzzle-counter increment)')
