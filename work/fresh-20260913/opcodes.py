from pathlib import Path
import struct,sys,json
sys.path.insert(0,str(Path('work/fresh-20260913/deps').resolve()))
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
b=Path(r'D:\astro\SETUP\ASTRO.EXE').read_bytes(); base=0x14600
md=Cs(CS_ARCH_X86,CS_MODE_16); ins={i.address:i for i in md.disasm(b[base+0x2ff2:base+0x3528],0x2ff2)}
rows=[]
for i in range(49):
 op=struct.unpack_from('<I',b,base+0x3528+4*i)[0]; addr=struct.unpack_from('<H',b,base+0x35ec+2*i)[0]; entry=addr;reads=[];size=4;seen=set()
 while addr!=0x33f4:
  if addr in seen:raise ValueError(addr)
  seen.add(addr);inst=ins[addr];s=inst.op_str
  if inst.mnemonic=='push' and s=='0xff':size=255
  if inst.mnemonic=='call' and s=='0x2fcd':reads.append(size);size=4
  if inst.mnemonic=='jmp':addr=int(s,16)
  else:addr+=inst.size
 rows.append(dict(opcode=op,entry=entry,reads=reads))
print(rows)
Path('outputs/astronomica-cleanroom/opcode-layout.json').write_text(json.dumps(rows,indent=2))
