"""Reconstruct P513 answer comparisons by executing original custom10/1."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args();sys.path.insert(0,str(Path('work/fresh-20260913/deps-verified').resolve()))
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
exe=(args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols=json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
s=next(s for s in symbols if s['name']=='_do_custom');base=s['file_offset']-s['offset']
md=Cs(CS_ARCH_X86,CS_MODE_16);ins={i.address:i for i in md.disasm(exe[base+0x20e3:base+0x23b7],0x20e3)}
def execute(setting,scenario):
    pc=0x20e3;compare=0;stack=[];result=None;sound=None
    values={'dword ptr es:[bx + 0x3f8]':setting,'dword ptr es:[bx + 0x3fc]':scenario}
    for _ in range(300):
        if pc in (0x23b2,0x23b4):return result,sound
        i=ins[pc];pc+=i.size;op=i.mnemonic
        if op=='les':assert i.op_str=='bx, ptr [0xc88]'
        elif op=='cmp':a,b=i.op_str.split(', ');compare=values[a]-int(b,0)
        elif op=='mov':
            a,b=i.op_str.split(', ');assert a=='dword ptr es:[bx + 0x404]';result=int(b,0)
        elif op=='push':stack.append(int(i.op_str,0))
        elif op=='pop':stack.pop()
        elif op=='lcall':sound=stack[-1];assert sound in (10,11)
        elif op in ('jmp','je','jne','jge'):
            if {'jmp':True,'je':compare==0,'jne':compare!=0,'jge':compare>=0}[op]:pc=int(i.op_str,16)
        else:raise AssertionError((hex(i.address),op))
    raise AssertionError('No return')
required={1:7,2:2,3:2,4:2,5:8,6:1,7:8,8:7,9:6,10:2,11:5,12:9,13:4,14:5}
h=2166136261;rows=[]
for scenario in range(1,15):
    for setting in range(-1,11):
        result,sound=execute(setting,scenario);target=required[scenario]
        assert (result,sound)==(int(setting==target),None if setting==target else 10 if setting<target else 11)
        if 1<=setting<=9:
            for value in (result,255 if sound is None else sound):h=((h^value)*16777619)&0xffffffff
        rows.append(dict(scenario=scenario,setting=setting,accepted=result,sound=sound))
raw=(args.root/'PLACES/P513/MEGAFILE.HYP').read_bytes();scene=parse(raw)
assert len(scene['sprites'])==32 and len(scene['scripts'])==4
success={struct.unpack_from('<I',exe,base+0x6c94+4*i)[0]:struct.unpack_from('<H',exe,base+0x6c94+136+2*i)[0] for i in range(34)}
assert success[513]==0x5808
success_ins={i.address:i for i in md.disasm(exe[base+0x5808:base+0x5829],0x5808)}
success_rows=[]
for flag in (-1,0,1,2):
    for count in (0,29):
        original_flag=flag;original_count=count;pc=0x5808;compare=0
        for _ in range(12):
            if pc==0x5a8e:break
            i=success_ins[pc];pc+=i.size
            if i.mnemonic=='les':assert i.op_str=='bx, ptr [0x7a8]'
            elif i.mnemonic=='cmp':assert i.op_str=='dword ptr es:[bx + 0x7e], 0';compare=flag
            elif i.mnemonic=='jne':
                if compare:pc=int(i.op_str,16)
            elif i.mnemonic=='inc':assert i.op_str=='dword ptr [0x153]';count+=1
            elif i.mnemonic=='mov':assert i.op_str=='dword ptr es:[bx + 0x7e], 1';flag=1
            elif i.mnemonic=='jmp':pc=int(i.op_str,16)
            else:raise AssertionError(('Unexpected success operation',i.mnemonic,i.op_str))
        assert pc==0x5a8e and flag==1 and count==original_count+(original_flag==0)
        success_rows.append(dict(initial_flag=original_flag,initial_counter=original_count,flag=flag,counter=count))
args.out.write_text(json.dumps(dict(scene=513,status='Original evidence; native checks recorded separately',cases=len(rows),normal_cases=126,
 fnv1a32=hex(h),required=required,rows=rows,success_cases=success_rows,
 original_quirks=['Setting3/scenario11 comparisons have no accepting branch; correct setting is5',
 'Success custom25 at4:5808 increments counter directly and sets global29; no common success sound',
 'Seven correct answers OR all14 scenario bits win; ten wrong answers exit'],
 motion=dict(callback='3:06ee',sprite=32,period_ms=10,delta_x='10-local0',finish='proposed x>442 and visible'),
 resource_sha256=hashlib.sha256(raw).hexdigest(),code_sha256=hashlib.sha256(exe[base+0x203d:base+0x23b7]).hexdigest()),indent=2))
print('Original P513 answers: PASS (%d cases, %s)' % (len(rows),hex(h)))
