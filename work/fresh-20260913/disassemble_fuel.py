from pathlib import Path
import json,struct,sys
sys.path.insert(0,str(Path('work/fresh-20260913/deps-verified').resolve()))
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
b=Path('D:/astro/SETUP/ASTRO.EXE').read_bytes();syms=json.loads(Path('outputs/astronomica-cleanroom/evidence/debug/symbols.json').read_text())
name=sys.argv[1] if len(sys.argv)>1 else '_fxm_move_fuel'
s=next(s for s in syms if s['name']==name);seg=s['segment'];start=s['offset'];base=s['file_offset']-start
segment_size=struct.unpack_from('<H',b,0x292+8*(seg-1))[0]
end=min([s['offset'] for s in syms if s['segment']==seg and s['offset']>start and s['flags']==24] or [segment_size])
names={(s['segment'],s['offset']):s['name'] for s in syms if s['flags']==24}
size=struct.unpack_from('<H',b,0x292+8*(seg-1))[0];relocs={}
for j in range(struct.unpack_from('<H',b,base+size)[0]):
 typ,flags,src,t1,t2=struct.unpack_from('<BBHHH',b,base+size+2+8*j);seen=set()
 while src!=65535 and src not in seen and src+2<=size:
  seen.add(src);relocs[src]=names.get((t1,t2),f'{t1}:{t2:x}')
  if flags&4:break
  src=struct.unpack_from('<H',b,base+src)[0]
lines=[]
for i in Cs(CS_ARCH_X86,CS_MODE_16).disasm(b[base+start:base+end],start):
 lines.append(f'{i.address:04x}: {i.mnemonic:8} {i.op_str}'+(' ; '+relocs.get(i.address+1,'') if i.mnemonic=='lcall' else ''))
Path('work/fresh-20260913/interpreter',name+'.asm').write_text('\n'.join(lines))
print('Original callback:',name,hex(start),hex(end))
