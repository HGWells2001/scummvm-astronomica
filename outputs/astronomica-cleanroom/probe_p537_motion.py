"""Execute original rocket callbacks over explicit SpriteWorld test fixtures.

Only callback instructions execute; external setters and success calls are
modeled. This is independent original-instruction evidence, not Windows
runtime observation or proof that every callback input is UI-reachable.
"""
import hashlib,json
import probe_p526_motion as p
import probe_p501_motion as symbols

ins={i.address:i for i in p.md.disasm(p.exe[p.base(3)+0x1631:p.base(3)+0x2036],0x1631)}
entries={'slow':(0x163f,0x1954),'orbit':(0x1969,0x1cd1),'fast':(0x1ce6,0x202f)}
mapping={i.address:i for i in p.md.disasm(p.exe[p.base(9)+0x896:p.base(9)+0x8ab],0x896)}
assert (mapping[0x896].mnemonic,mapping[0x896].op_str)==('mov','si, 1')
assert (mapping[0x89e].mnemonic,mapping[0x89e].op_str)==('shl','ax, 2')
assert (mapping[0x8a7].mnemonic,mapping[0x8a7].op_str)==('les','bx, ptr es:[bx + 0x20]')
class Machine(p.Machine):
 def invoke(self,kind):
  pc,end=entries[kind];self.reg={'ebp':0x9000,'esp':0x8d00}
  self.write(0x9006,self.sprite(34));self.write(0x900a,0x7400);compare=0
  for _ in range(3000):
   if pc==end:return
   i=ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[self.value(i,t) for t in o]
   if op=='mov':self.put(i,o[0],v[1])
   elif op=='movsx':self.put(i,o[0],p.signed(v[1],o[1].size))
   elif op=='les':self.setreg(i.reg_name(o[0].reg),v[1]&65535)
   elif op in ('add','sub','or','shl'):
    result={'add':lambda:v[0]+v[1],'sub':lambda:v[0]-v[1],'or':lambda:v[0]|v[1],'shl':lambda:v[0]<<v[1]}[op]()
    self.put(i,o[0],result);compare=p.signed(result,o[0].size)
   elif op in ('inc','dec'):self.put(i,o[0],v[0]+(1 if op=='inc' else -1))
   elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
   elif op=='imul':
    if len(o)==1:
     product=p.signed(self.getreg('ax'),2)*p.signed(v[0],2);self.setreg('ax',product);self.setreg('dx',product>>16)
    else:self.put(i,o[0],p.signed(v[-2],o[-2].size)*p.signed(v[-1],o[-1].size))
   elif op=='cdq':
    wide=0x66 in i.prefix;self.setreg('edx' if wide else 'dx',-1 if p.signed(self.getreg('eax' if wide else 'ax'),4 if wide else 2)<0 else 0)
   elif op=='idiv':
    wide=o[0].size==4;bits=32 if wide else 16;lo='eax' if wide else 'ax';hi='edx' if wide else 'dx'
    n=p.signed((self.getreg(hi)<<bits)|self.getreg(lo),bits//4);d=p.signed(v[0],o[0].size)
    q=abs(n)//abs(d)*(-1 if (n<0)!=(d<0) else 1)
    assert -(1<<(bits-1))<=q<(1<<(bits-1));self.setreg(lo,q);self.setreg(hi,n-q*d)
   elif op=='push':self.push(v[0],o[0].size)
   elif op=='pop':self.put(i,o[0],self.pop(o[0].size))
   elif op=='nop':pass
   elif op=='lcall':self.external(symbols.relocs[i.address+1])
   elif op=='call':
    assert v[0]==0x39ae;self.pop();self.success_calls+=1
   elif op in ('jmp','je','jne','jg','jge','jl','jle'):
    if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jge':compare>=0,'jl':compare<0,'jle':compare<=0}[op]:pc=v[0]
   else:raise AssertionError((hex(i.address),op,i.op_str))
  raise AssertionError('Original rocket callback did not return')
 @staticmethod
 def sprite(id):return 0x2000+id*0x100
 def external(self,name):
  sp=self.getreg('sp');s=self.read(sp)
  if name=='_SWOffsetSprite':self.locate(s,p.signed(self.read(s+0x17,2),2)+p.signed(self.read(sp+4,2),2),p.signed(self.read(s+0x19,2),2)+p.signed(self.read(sp+6,2),2))
  elif name=='_SWSetSpriteMoveDelta':self.write(s+0x7d,self.read(sp+4,2),2);self.write(s+0x7f,self.read(sp+6,2),2)
  elif name=='_SWSetSpriteMoveTime':self.write(s+0x6f,self.read(sp+4))
  elif name=='_SWSetSpriteFrameTime':self.write(s+0x39,self.read(sp+4))
  elif name=='_SWSetSpriteVisible':self.write(s+0x10,self.read(sp+4,2),2)
  elif name=='_SWSetCurrentFrameIndex':self.write(s+0x5b,self.read(sp+4,2))
  else:raise AssertionError(name)

def trace(kind,setting,already_solved):
 m=Machine();m.success_calls=0;m.write(0xc88,0x1000);m.write(0x7a8,0x7000);m.write(0x709a,already_solved);m.write(0x13f8,setting)
 for id in range(1,49):
  s=m.sprite(id);m.write(0x1020+4*id,s);m.write(s+0x1b,16,2);m.write(s+0x1d,16,2);m.write(s+0x10,1,2)
  m.write(s+0x39,0);m.write(s+0x6f,10);m.write(s+0x5b,0)
 rocket=m.sprite(34);delta={'slow':2,'orbit':4,'fast':16}[kind];m.write(rocket+0x7d,delta,2)
 m.locate(rocket,0,50 if kind=='slow' else 100)
 if kind=='slow':m.write(rocket+0x5b,9)
 for id,xy in [(30,(393,361)),(31,(462,361)),(32,(529,414))]:m.locate(m.sprite(id),*xy)
 hash=2166136261;rows=[]
 for tick in range(1,1001):
  x=p.signed(m.read(rocket+0x17,2)+m.read(rocket+0x7d,2),2)
  m.write(0x7400,x,2);m.write(0x7402,m.read(rocket+0x19,2),2);m.invoke(kind)
  m.locate(rocket,p.signed(m.read(0x7400,2),2),p.signed(m.read(0x7402,2),2))
  row=[tick,p.signed(m.read(rocket+0x7d,2),2),m.success_calls,m.read(0x709a)]
  for id in range(9,35):
   s=m.sprite(id);row += [p.signed(m.read(s+o,n),n) for o,n in [(0x17,2),(0x19,2),(0x10,2),(0x5b,4),(0x39,4),(0x6f,4)]]
  for value in row:hash=((hash^(value&0xffffffff))*16777619)&0xffffffff
  rows.append(row)
  if p.signed(m.read(rocket+0x6f),4)<0:break
 else:raise AssertionError('Rocket trace did not stop')
 assert m.success_calls==int(kind=='orbit' and not already_solved)
 return dict(kind=kind,setting=setting,already_solved=already_solved,ticks=len(rows),fnv32=f'{hash:08x}',last=rows[-1],rows=rows)

if __name__=='__main__':
 traces=[trace(kind,setting,solved) for kind in entries for setting in range(16) for solved in (0,1)]
 total_steps=sum(t['ticks'] for t in traces);combined=2166136261
 for t in traces:
  for v in [list(entries).index(t['kind']),t['setting'],t['already_solved']]:combined=((combined^v)*16777619)&0xffffffff
  for row in t['rows']:
   for v in row:combined=((combined^(v&0xffffffff))*16777619)&0xffffffff
  rows=t.pop('rows');t['raw_rows_sha256']=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
  t['samples']=[rows[i] for i in sorted({0,len(rows)//2,len(rows)-1})]
 p.args.out.write_text(json.dumps(dict(date='2026-10-20',status='PASS',scope=__doc__,exe_sha256=hashlib.sha256(p.exe).hexdigest(),
  callback_sha256=hashlib.sha256(p.exe[p.base(3)+0x1631:p.base(3)+0x2036]).hexdigest(),
  sprite_table_mapping=dict(first_id=1,pointer_offset='game+0x20+4*id',first_pointer_offset='game+0x24',
   evidence='Original hover loop9:0896 setsSI=1,9:089e multipliesby4,9:08a7 reads[game+offset+0x20]',
   code_sha256=hashlib.sha256(p.exe[p.base(9)+0x896:p.base(9)+0x8ab]).hexdigest()),
  fixture_scope='Callback kind and live setting are independently selected inputs; not all combinations are UI-reachable',
  combined_fnv32=f'{combined:08x}',steps=total_steps,
  row_schema='tick, moveDeltaX, successCallCount, global36; then IDs9..34 each renderX/renderY/visible/frameIndex/framePeriod/movePeriod',
  modeled_external_calls=['SpriteWorld rectangle/timer/frame/visibility setters','puzzle_successful call counter'],traces=traces),indent=2))
 print('Original rocket callbacks:',len(traces),'controlled traces,',total_steps,'steps, combined',f'{combined:08x}','PASS')
