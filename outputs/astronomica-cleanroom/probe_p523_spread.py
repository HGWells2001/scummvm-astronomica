"""Run original _spread x86/x87 instructions for the P523 three controls.

All original float32 stores are rounded through struct.pack. Integer conversion
uses the original truncation helper. This is research, not native scene support.
"""
import json,struct,hashlib,collections
import probe_p526_motion as p

code=p.exe[p.base(3)+0xab:p.base(3)+0x234]
ins={i.address:i for i in p.md.disasm(code,0xab)}
data_segment=struct.unpack_from('<H',p.exe,p.ne+0xe)[0]
constant=p.exe[p.base(data_segment)+0x104:p.base(data_segment)+0x108]
assert struct.unpack('<f',constant)[0]==99.0

def spread(values,delta):
 m=p.Machine();m.reg={'ebp':0x9000,'esp':0x8d00};m.mem[0x104:0x108]=constant
 for i,value in enumerate(values):m.write(0x9006+4*i,0x1000+2*i);m.write(0x1000+2*i,value,2)
 m.write(0x9012,delta,2);pc=0xab;stack=[];compare=0
 def fp(o,i):return struct.unpack('<f',bytes(m.mem[m.address(i,o):m.address(i,o)+4]))[0]
 for _ in range(300):
  if pc==0x234:return tuple(m.read(0x1000+2*i,2) for i in range(3))
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op in ('wait','nop','sahf'):pass
  elif op=='fild':stack.append(float(p.signed(v[0],o[0].size)))
  elif op=='fld':stack.append(fp(o[0],i))
  elif op=='fldz':stack.append(0.0)
  elif op=='fld1':stack.append(1.0)
  elif op=='fstp':
   a=m.address(i,o[0]);m.mem[a:a+4]=struct.pack('<f',stack.pop())
  elif op=='fadd':stack[-1]+=fp(o[0],i)
  elif op=='fmul':stack[-1]*=fp(o[0],i)
  elif op=='fsubr':stack[-1]=fp(o[0],i)-stack[-1]
  elif op=='fdivr':stack[-1]=fp(o[0],i)/stack[-1]
  elif op=='fcompp':
   a=stack.pop();b=stack.pop();compare=(a>b)-(a<b)
  elif op=='fcomp':
   a=stack.pop();b=fp(o[0],i);compare=(a>b)-(a<b)
  elif op=='fnstsw':m.put(i,o[0],0x100 if compare<0 else 0x4000 if compare==0 else 0)
  elif op=='lcall':
   assert i.address in (0x20b,0x21a,0x229)
   m.setreg('ax',int(stack.pop()))
  elif op in ('jbe','jmp'):
   if op=='jmp' or compare<=0:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('spread did not return')

def step(state,button):
 selected=(button-1)%3
 # The original argument permutation keeps the first remaining channel
 # first, and computes the final channel as a residual after rounding.
 order=([0,1,2],[1,0,2],[2,1,0])[selected]
 values=spread(tuple(state[i] for i in order),-10 if button<=3 else 10)
 result=list(state)
 for i,v in zip(order,values):result[i]=v
 return tuple(result)

if __name__=='__main__':
 seen={(33,33,33)};pending=collections.deque(seen);h=hashlib.sha256();edges=0
 samples=[]
 while pending:
  state=pending.popleft()
  for button in range(1,7):
   result=step(state,button);edges+=1
   assert all(0<=v<=99 for v in result),result
   h.update(struct.pack('<7H',*state,button,*result))
   if state in ((33,33,33),(99,0,0),(0,99,0),(0,0,99)):
    samples.append(dict(state=state,button=button,result=result))
   if result not in seen:seen.add(result);pending.append(result)
 output=dict(status='Original instruction research only; P523 not enabled',
  code_sha256=hashlib.sha256(code).hexdigest(),states=len(seen),transitions=edges,
  graph_sha256=h.hexdigest(),possible_sums=sorted({sum(s) for s in seen}),
  samples=samples,states_sha256=hashlib.sha256(json.dumps(sorted(seen)).encode()).hexdigest())
 p.args.out.write_text(json.dumps(output,indent=2))
 print('P523 original spread:',len(seen),'reachable states,',edges,'transitions; sums',output['possible_sums'])
