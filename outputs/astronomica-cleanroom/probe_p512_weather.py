"""Derive P512's setting validation and movie operations from original files."""
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
custom = next(s for s in symbols if s['name'] == '_do_custom')
base = custom['file_offset']-custom['offset']
def dispatch(address, count):
    return {struct.unpack_from('<I',exe,base+address+4*i)[0]:struct.unpack_from('<H',exe,base+address+4*count+2*i)[0] for i in range(count)}
assert dispatch(0x72a0,31)[24] == 0x528e
modes = dispatch(0x6d84,4)
assert modes == {0:0x52bc,1:0x5634,2:0x5676,3:0x569a}
scenarios = dispatch(0x6d60,6)
md = Cs(CS_ARCH_X86, CS_MODE_16)
ins = {i.address:i for i in md.disasm(exe[base+0x52f1:base+0x5634],0x52f1)}

def execute(scenario, settings):
    values = dict(zip(['dword ptr es:[bx + 0x3f8]','dword ptr es:[bx + 0x3fc]','dword ptr es:[bx + 0x400]'],settings))
    pc = scenarios[scenario]; comparison = None; sound = None; stack = []
    for _ in range(100):
        i = ins[pc]; pc += i.size; op = i.mnemonic
        if op == 'les': assert i.op_str == 'bx, ptr [0xc88]'
        elif op == 'cmp':
            lhs,rhs = i.op_str.split(', '); comparison = values[lhs]-int(rhs,0)
        elif op == 'mov':
            lhs,rhs = i.op_str.split(', ')
            assert lhs == 'dword ptr es:[bx + 0x40c]' and rhs in ('0','1')
            return int(rhs),sound
        elif op == 'push': stack.append(int(i.op_str,0))
        elif op == 'pop': assert i.op_str == 'cx'; stack.pop()
        elif op == 'lcall':
            assert stack[-1] in (10,11,12)
            sound = stack[-1]
        elif op in ('je','jne','jg','jle','jmp'):
            if {'je':comparison==0,'jne':comparison!=0,'jg':comparison>0,'jle':comparison<=0,'jmp':True}[op]: pc = int(i.op_str,0)
        else: raise AssertionError((hex(i.address),op,i.op_str))
    raise AssertionError('No result')

# Independently summarized from the disassembly, then checked exhaustively.
targets = {1:(None,None,15),2:(15,None,None),3:(15,None,None),4:(15,None,None),5:(None,15,None),6:(None,15,15)}
rows = []; digest = 2166136261
for scenario in range(1,7):
    count = 0; sounds = {10:0,11:0,12:0}
    for a in range(16):
        for b in range(16):
            for c in range(16):
                settings = (a,b,c)
                result,sound = execute(scenario,settings)
                wrong = [i for i,t in enumerate(targets[scenario]) if (settings[i] > 8 if t is None else settings[i] != t)]
                assert (result,sound) == (int(not wrong),12-wrong[0] if wrong else None)
                count += result
                if sound is not None: sounds[sound] += 1
                for byte in (result,255 if sound is None else sound): digest = ((digest ^ byte)*16777619)&0xffffffff
    rows.append(dict(scenario=scenario,entry=hex(scenarios[scenario]),setting_requirements=['0..8' if t is None else str(t) for t in targets[scenario]],accepted=count,wrong_sound_counts=sounds))
raw = (args.root/'PLACES/P512/MEGAFILE.HYP').read_bytes()
scene = parse(raw)
assert len(scene['sprites']) == 64 and len(scene['scripts']) == 6
segments = [c['args'] for c in scene['scripts'][2] if c['opcode'] == 37]
seeks = [c['args'] for c in scene['scripts'][2] if c['opcode'] == 36]
assert [s[:2] for s in segments] == seeks
assert segments == [[0,0,150],[0,150,204],[0,1272,184],[0,1456,186],[0,1642,189],[0,1834,85]]
assert [c['args'] for c in scene['scripts'][2] if c['opcode']==23] == [[24,1,160,57,0,0],[24,3,160,57,0,0]]
buttons = []
for i,s in enumerate(scene['sprites']):
    if s.get('click_enabled'):
        buttons.append(dict(sprite=i+1,xy=s['xy'],commands=[dict(op=c['opcode'],args=c['args'],delay=c['delay']) for c in s['click']]))
show = next(s for s in symbols if s['name'] == '_ShowMovie')
show_base = show['file_offset']-show['offset']
assert exe[show_base+0x48d:show_base+0x48f] == bytes.fromhex('6a08')
assert next(s for s in symbols if s['segment']==1 and s['offset']==0x632)['name'] == '_GetMoviePreferredRate'
assert next(s for s in symbols if s['segment']==1 and s['offset']==0x7d4)['name'] == '_MCDoAction'
show_code = exe[show_base+0x3aa:show_base+0x4c7]
result = dict(scene=512,status='Original-file evidence; native engine validation recorded separately',cases=6*16**3,fnv1a32=hex(digest),modes={str(k):hex(v) for k,v in modes.items()},answers=rows,wrong_sound_priority='first wrong setting in order local0, local1, local2 -> direct S12, S11, S10',movie='FLATPHEN.MOV',segments=segments,movie_position=[160,57],movie_semantics={'1':'ShowMovie: position; MCActionPlay at preferred rate (17:0494); restore selected segment','2':'StartMovie: PlayMovie at existing position','3':'fxm_UpdateMovie: redraw current frame','opcode36':'SetMovieTimeValue: seek in movie time-scale units'},show_movie_sha256=hashlib.sha256(show_code).hexdigest(),quicktime_action_reference='Apple Inside Macintosh QuickTime Components 1993, pp. 2-17/2-18; mcActionPlay=8, mcActionGoToTime=12. https://vintageapple.org/inside_r/pdf/QuickTime_Components_1993.pdf',resource_sha256=hashlib.sha256(raw).hexdigest(),custom24_sha256=hashlib.sha256(exe[base+0x528e:base+0x56b5]).hexdigest(),buttons=buttons)
args.out.write_text(json.dumps(result,indent=2))
print('Original P512 validation: PASS (%d combinations, hash %s)' % (result['cases'],result['fnv1a32']))
