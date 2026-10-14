from pathlib import Path
import sys,struct
sys.path.insert(0,str(Path('work/fresh-20260913/deps-verified').resolve()))
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
b=Path('D:/astro/SETUP/ASTRO.EXE').read_bytes()
ne=struct.unpack_from('<I',b,60)[0]
table=ne+struct.unpack_from('<H',b,ne+0x22)[0]
base=struct.unpack_from('<H',b,table)[0]<<struct.unpack_from('<H',b,ne+0x32)[0]
for name,start,end in [('multiply',0xb3c,0xb54),('srand',0xb54,0xb6b),('rand',0xb6b,0xb94)]:
    lines=[f'{i.address:04x}: {i.mnemonic} {i.op_str}' for i in Cs(CS_ARCH_X86,CS_MODE_16).disasm(b[base+start:base+end],start)]
    print(name,'\n'+'\n'.join(lines))
