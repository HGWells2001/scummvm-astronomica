from pathlib import Path
import sys,struct
import argparse,hashlib
ap=argparse.ArgumentParser();ap.add_argument('exe',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
b=args.exe.read_bytes()
assert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
ne=struct.unpack_from('<I',b,60)[0]
table=ne+struct.unpack_from('<H',b,ne+0x22)[0]
base=struct.unpack_from('<H',b,table)[0]<<struct.unpack_from('<H',b,ne+0x32)[0]
for name,start,end in [('multiply',0xb3c,0xb54),('srand',0xb54,0xb6b),('rand',0xb6b,0xb94)]:
    lines=[f'{i.address:04x}: {i.mnemonic} {i.op_str}' for i in Cs(CS_ARCH_X86,CS_MODE_16).disasm(b[base+start:base+end],start)]
    (args.out/(name+'.asm')).write_text('\n'.join(lines)+'\n')
    print(name,'\n'+'\n'.join(lines))
