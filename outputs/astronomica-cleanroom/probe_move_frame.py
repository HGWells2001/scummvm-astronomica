"""Pin opcode 24's native handler and all seven P525 call sites."""
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
assert dispatch[24] == 0xa94
code = exe[base+0xa94:base+0xb2d]
assert bytes.fromhex('66 26 89 87 a5 00') in code
assert bytes.fromhex('66 26 89 87 a9 00') in code
raw = (args.root/'PLACES/P525/MEGAFILE.HYP').read_bytes()
s = parse(raw)
sites = [c['args'] for c in s['sprites'][21]['click'] if c['opcode'] == 24]
assert sites == [[21,291,131,5],[21,286,125,4],[21,281,112,3],[21,282,115,3],[21,277,110,2],[21,270,94,1],[21,263,82,0]]
assert len(s['sprites'][20]['frames']) == 7
args.out.write_text(json.dumps(dict(opcode=24,handler='15:0a94-0b2a',handler_sha256=hashlib.sha256(code).hexdigest(),resource_sha256=hashlib.sha256(raw).hexdigest(),call_sites=sites,semantics='absolute move; store full coordinates; set frame; preserve visibility and animation state',scope='Command verification, not a complete P525 solution'),indent=2))
print('Original move/frame command and P525 call sites: PASS')
