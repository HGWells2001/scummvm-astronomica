from pathlib import Path
import struct,json,sys
sys.path.insert(0,str(Path('work/fresh-20260913/deps').resolve()))
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
b=Path(r'D:\astro\SETUP\ASTRO.EXE').read_bytes(); names=['']+[x.decode('latin1') for x in b[0x61ff5:-8].split(b'\0')];syms=[]
for i in range(3686):
 name,typ,off,seg,flags=struct.unpack_from('<IIHHH',b,0x24690+14*i)
 if name>=len(names):raise ValueError((i,name))
 syms.append(dict(name=names[name],type=typ,offset=off,segment=seg,flags=flags))
Path('outputs/astronomica-cleanroom/symbols.json').write_text(json.dumps(syms,indent=2))
md=Cs(CS_ARCH_X86,CS_MODE_16)
for name in ['_load_place','_read_command_mem','_getsome','_execute_command','_load_game']:
 s=next(s for s in syms if s['name']==name);seg=s['segment'];off=s['offset'];base=struct.unpack_from('<H',b,0x290+8*(seg-1))[0]<<9
 ends=[x['offset'] for x in syms if x['segment']==seg and x['offset']>off and x['flags']==s['flags']];end=min(ends) if ends else off+1000
 print(s,'file',hex(base+off),'length',end-off)
 lines=[f'{i.address:04x}: {i.mnemonic:8} {i.op_str}' for i in md.disasm(b[base+off:base+end],off)]
 Path('work/fresh-20260913/'+name+'.asm').write_text('\n'.join(lines))
 if name in ['_read_command_mem','_getsome']:print('\n'.join(lines[:120]))
