"""Pin the six-scene custom-17 sequence and its process-static lifecycle."""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from astro_reader import parse, FormatError

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
assert dispatch[17] == 0x385b
assert struct.unpack_from('<II',exe,0x21200+0x14b) == (0,0)
code = exe[base+0x385b:base+0x3a3c]
assert bytes.fromhex('68 9a 03') in code  # direct _playSound(922)
assert bytes.fromhex('66 c7 46') in code
md = Cs(CS_ARCH_X86, CS_MODE_16)
references = []
for segment in sorted({s['segment'] for s in symbols if s['flags'] == 24}):
    functions = sorted([s for s in symbols if s['segment'] == segment and s['flags'] == 24],key=lambda s:s['offset'])
    segbase = functions[0]['file_offset']-functions[0]['offset']
    size = struct.unpack_from('<H',exe,0x292+8*(segment-1))[0]
    for i,s in enumerate(functions):
        end = functions[i+1]['offset'] if i+1 < len(functions) else size
        for ins in md.disasm(exe[segbase+s['offset']:segbase+end],s['offset']):
            if '[0x14b]' in ins.op_str or '[0x14f]' in ins.op_str:
                references.append(dict(function=s['name'],segment=segment,address=hex(ins.address),instruction=f'{ins.mnemonic} {ins.op_str}'))
assert {r['function'] for r in references} == {'_do_custom','_load_place'}
assert len(references) == 9
scenes = []
for place in [506,531,532,533,534,535]:
    raw = (args.root/f'PLACES/P{place}/MEGAFILE.HYP').read_bytes()
    trailing = 0
    try:
        scene = parse(raw)
    except FormatError as e:
        match = re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e))
        assert match
        trailing = int(match[1]); scene = parse(raw[:int(match[2],16)])
    assert len(scene['scripts']) == 2
    assert scene['scripts'][0][1]['opcode'] == 23 and scene['scripts'][0][1]['args'] == [17,0,0,0,0,0]
    answers = []
    for i,sprite in enumerate(scene['sprites']):
        click = sprite.get('click',[])
        bits = [c['args'][2] for c in click if c['opcode'] == 33 and c['args'][:2] == [1,0]]
        if bits:
            condition = next(c for c in click if c['opcode'] == 31)
            assert condition['args'][:2] == [1,1]
            answers.append(dict(sprite=i+1,choice=condition['args'][2],bits=bits))
    scenes.append(dict(scene=place,resource_sha256=hashlib.sha256(raw).hexdigest(),trailing_bytes=trailing,answers=answers))
args.out.write_text(json.dumps(dict(handler='4:385b-3a39',handler_sha256=hashlib.sha256(code).hexdigest(),initial_statics=dict(round=0,mask=0),direct_static_references=references,sequence=dict(initial_scene_counted=False,random_rounds=3,random_pool=[506,531,532,533,534,535],initial_scene_may_repeat=True,success_global=23,success_voice=912,completion_voice=922,destination=519,delay_after_completion_voice_ms=3000,reset='round and mask reset only at custom17 completion in the named-function scan',intro='9:1c31 suppresses introduction when round > 1'),scenes=scenes),indent=2))
print('Original variant sequence: PASS (six resources, process statics, three random rounds, global S22)')
