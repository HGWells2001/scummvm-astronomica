"""Execute the original Jupiter projectile callback, with explicit external-call models."""
import json,hashlib
import probe_comet_state as setup
p=setup.p
ins={i.address:i for i in p.md.disasm(p.exe[p.base(3)+0x34e2:p.base(3)+0x364e],0x34e2)}
def run(m):
 m.reg={'ebp':0x9000,'esp':0x8d00};m.write(0x9006,m.read(0x1020+4*13));pc=0x34e2;compare=0
 for _ in range(1800):
  if pc==0x3647:return
  i=ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[m.value(i,t) for t in o]
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='movsx':m.put(i,o[0],p.signed(v[1],o[1].size))
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='inc':m.put(i,o[0],v[0]+1)
  elif op=='shl':m.put(i,o[0],v[0]<<v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='or':m.put(i,o[0],v[0]|v[1]);compare=p.signed(v[0]|v[1],o[0].size)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='pop':m.put(i,o[0],m.pop(o[0].size))
  elif op=='nop':pass
  elif op=='lcall':
   sp=m.getreg('sp')
   if i.address==0x3595:
    x=p.signed(m.read(sp,2),2);y=p.signed(m.read(sp+2,2),2);rect=m.read(sp+4)
    left,top,right,bottom=[p.signed(m.read(rect+j*2,2),2) for j in range(4)]
    # USER PtInRect model. Fixtures avoid all four edges, so no Win16
    # boundary-convention conclusion is drawn from this callback probe.
    assert x not in (left,right) and y not in (top,bottom)
    m.setreg('ax',int(left<x<right and top<y<bottom))
   elif i.address==0x35e0:
    s=m.read(sp);m.write(s+0x79,m.read(sp+4));m.write(s+0x6f,m.read(sp+4))
   elif i.address==0x3626:m.sounds.append(m.read(sp,2))
   else:raise AssertionError(hex(i.address))
  elif op=='call':
   m.pop(2);sp=m.getreg('sp');id=m.read(sp);s=m.read(0x1020+4*id)
   if v[0]==0x33e5:
    for off in (0x39,0x6f):m.write(s+off,-1)
    for off in (0x10,0x7d,0x7f):m.write(s+off,0,2)
    m.stopped.append(id)
   elif v[0]==0x364e:m.explosions.append([m.read(sp+j*4) for j in range(4)])
   else:raise AssertionError(hex(v[0]))
  elif op in ('jmp','je','jne','jg','jge','jl','jle'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jge':compare>=0,'jl':compare<0,'jle':compare<=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('collision did not return')
rows=[]
for target in range(14,22):
 for visible in (0,1):
  for x,y in ((84,84),(130,84),(84,130),(650,84)):
   m=setup.machine(1,1,0,0);m.stopped=[];m.explosions=[]
   s=m.read(0x1020+4*13);m.locate(s,x,y);m.write(s+0x10,1,2)
   for off,value in ((0x81,0),(0x83,0),(0x85,640),(0x87,320)):m.write(s+off,value,2)
   victim=m.read(0x1020+4*target);m.locate(victim,90,90);m.write(victim+0x10,visible,2)
   run(m)
   rows.append(dict(input=[target,visible,x,y],solved=m.read(0x1400),stopped=m.stopped,sounds=m.sounds,explosions=m.explosions))
p.args.out.write_text(json.dumps(dict(status='Original callback execution; external rectangle-test edges excluded; not native validation',cases=len(rows),rows=rows,
 code_sha256=hashlib.sha256(p.exe[p.base(3)+0x34d5:p.base(3)+0x364e]).hexdigest()),indent=2))
print('Original P516 collision:',len(rows),'cases PASS')
