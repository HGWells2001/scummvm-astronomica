import sys,struct,json
from pathlib import Path
sys.path.insert(0,str(Path('outputs/astronomica-cleanroom').resolve()))
import probe_p526_motion as p
rows=[]
for seg in range(1,21):
 size=struct.unpack_from('<H',p.exe,p.table+8*(seg-1)+2)[0];count=struct.unpack_from('<H',p.exe,p.base(seg)+size)[0]
 for n in range(count):
  typ,flags,src,a,b=struct.unpack_from('<BBHHH',p.exe,p.base(seg)+size+2+8*n)
  if (flags&3)!=0 or (a,b) not in ((9,0x40c9),(9,0x4275)):continue
  seen=set()
  while src!=65535 and src not in seen and src+2<=size:
   seen.add(src);rows.append(dict(segment=seg,address=src,target=b))
   if flags&4:break
   src=struct.unpack_from('<H',p.exe,p.base(seg)+src)[0]
for row in rows:
 print(row)
 seg=row['segment'];off=row['address'];start=max(0,off-65)
 for i in p.md.disasm(p.exe[p.base(seg)+start:p.base(seg)+off+40],start):print(f'{i.address:04x} {i.mnemonic} {i.op_str}')
