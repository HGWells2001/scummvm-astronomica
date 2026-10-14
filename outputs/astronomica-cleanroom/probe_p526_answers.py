"""Extract P526 answer acceptance by interpreting the original comparison chain.

This independently checks the original comparison chain used by the engine.
Only LES, CMP, conditional jumps and the result MOV are accepted here.
"""
import argparse
import hashlib
import json
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
s = next(s for s in symbols if s['name'] == '_do_custom')
base = s['file_offset']-s['offset']
md = Cs(CS_ARCH_X86, CS_MODE_16)
instructions = {i.address:i for i in md.disasm(exe[base+0x2851:base+0x2e22],0x2851)}

def accepted(scenario, frame, choice):
    values = {'dword ptr es:[bx + 0x400]':scenario,
              'dword ptr es:[bx + 0x404]':choice,
              'dword ptr es:[bx + 0x5b]':frame}
    pc = 0x2851
    comparison = None
    for step in range(400):
        i = instructions[pc]
        pc += i.size
        op = i.mnemonic
        if op == 'les':
            assert i.op_str in ['bx, ptr [0xc88]','bx, ptr es:[bx + 0x68]']
        elif op == 'cmp':
            lhs,rhs = i.op_str.split(', ')
            comparison = values[lhs]-int(rhs,0)
        elif op == 'mov':
            lhs,rhs = i.op_str.split(', ')
            assert lhs == 'dword ptr es:[bx + 0x408]' and rhs in ['0','1']
            return int(rhs)
        elif op in ['je','jne','jg','jmp']:
            jump = op == 'jmp' or (op == 'je' and comparison == 0) or (op == 'jne' and comparison != 0) or (op == 'jg' and comparison > 0)
            if jump:
                pc = int(i.op_str,0)
        else:
            raise AssertionError((hex(i.address),op,i.op_str))
    raise AssertionError('No result reached')

matrix = {str(scenario):{str(frame):[choice for choice in range(7) if accepted(scenario,frame,choice)] for frame in range(14)} for scenario in range(1,7)}
assert all(matrix[str(s)] == matrix['1'] for s in [2,3,4])
assert matrix['5'] == matrix['6']
assert matrix['1']['0'] == [1,3] and matrix['1']['5'] == [5,6]
assert matrix['5']['6'] == [1,3,4] and matrix['5']['10'] == [1,2,5,6]
for scenario in (-1,0,7):
    for frame in range(14):
        for choice in range(7):
            assert accepted(scenario,frame,choice) == accepted(1 if scenario <= 4 else 5,frame,choice)
raw = (args.root/'PLACES/P526/MEGAFILE.HYP').read_bytes()
scene = parse(raw)
assert len(scene['scripts']) == 2
args.out.write_text(json.dumps(dict(scene=526,status='Original comparison-chain evidence; engine integration verified separately',resource_sha256=hashlib.sha256(raw).hexdigest(),answer_handler='4:2851-2e1d',answer_code_sha256=hashlib.sha256(exe[base+0x2851:base+0x2e22]).hexdigest(),inputs=dict(scenario='local2',choice='local3',frame='sprite18 current frame'),output='local4, 1 for accepted else 0',cases_executed=6*14*7,extra_scenario_boundary_cases=3*14*7,accepted_choices_by_scenario_and_frame=matrix,movement_dependencies=['4:26a4-284e custom13 mode0','3:1199-15fc _fxm_eclipse','3:2733-33e4 _fxm_move_ellipse']),indent=2))
print('Original P526 acceptance: PASS (588 input cases interpreted from x86)')
