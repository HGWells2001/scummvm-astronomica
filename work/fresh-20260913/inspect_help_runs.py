import json,collections
from pathlib import Path
rs=json.loads(Path('outputs/astronomica-cleanroom/evidence/help-compression.json').read_text())['records']
counts=collections.Counter();bad=[]; starts=collections.Counter()
for r in rs:
 if r['kind']!=32:continue
 b=bytes.fromhex(r['format_hex']); n=r['text'].count('\0'); candidates=[]
 for st in range(len(b)):
  p=st;ops=[]
  while p<len(b):
   op=b[p];p+=1;ops.append(op)
   if op==0x80:p+=2
   elif op==0x86:
    if b[p:p+6]!=bytes.fromhex('220880020000'):break
    p+=8
   elif op not in (0x81,0x82,0x83,0xff):break
   if op==255:break
  else:continue
  if p==len(b) and len(ops)==n and ops[-1]==255:candidates.append((st,ops))
 if len(candidates)!=1:bad.append((r['address'],b.hex(),repr(r['text'][:80]),n,len(candidates)))
 else:starts[candidates[0][0]]+=1;counts.update(candidates[0][1])
print('starts',starts,'opcodes',counts,'bad',len(bad));print(*bad[:20],sep='\n')
