"""Execute custom1's position instructions with exact x87 intermediates.

Products/subtractions here fit the x87 64-bit significand exactly. Using binary64
temporaries instead incorrectly rounds multiples of20 onto integer boundaries.
"""
import json,struct,hashlib
from fractions import Fraction
import probe_p526_motion as p
import probe_comet_state as setup
code=p.exe[p.base(4)+0xed:p.base(4)+0x17c]
ins={i.address:i for i in p.md.disasm(code,0xed)}
ds=struct.unpack_from('<H',p.exe,p.ne+0xe)[0]
factor=Fraction.from_float(struct.unpack_from('<d',p.exe,p.base(ds)+0x16b)[0])
origin=Fraction.from_float(struct.unpack_from('<f',p.exe,p.base(ds)+0x173)[0])
rows=[];h=2166136261
for value in range(100):
 m=setup.machine(0,0,0,0);m.reg={'ebp':0x9000,'esp':0x8d00};pc=0xed;stack=[];moves=[]
 for a in (0x145,0x147,0x149):m.write(a,value,2)
 for _ in range(100):
  if pc==0x17c:break
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='wait':pass
  elif op=='fild':stack.append(Fraction(p.signed(v[0],o[0].size)))
  elif op=='fmul':
   assert m.address(i,o[0])==0x16b
   stack[-1]*=factor
  elif op=='fsubr':
   assert m.address(i,o[0])==0x173
   stack[-1]=origin-stack[-1]
  elif op=='lcall':
   if i.address in (0x101,0x131,0x162):m.setreg('ax',int(stack.pop()))
   else:
    assert setup.relocs[i.address+1]=='_SWMoveSprite'
    sp=m.getreg('sp');moves.append([m.read(sp+4,2),m.read(sp+6,2)])
  else:raise AssertionError((hex(i.address),op))
 else:raise AssertionError('position code did not finish')
 for xy in moves:
  for v in xy:h=((h^v)*16777619)&0xffffffff
 rows.append(dict(value=value,moves=moves))
out=dict(status='Original position instructions, exact intermediates',code_sha256=hashlib.sha256(code).hexdigest(),
 factor=[factor.numerator,factor.denominator],hash=hex(h),cases=len(rows),rows=rows)
p.args.out.write_text(json.dumps(out,indent=2));print('Original positions:',len(rows),'cases',hex(h),'factor',factor)
