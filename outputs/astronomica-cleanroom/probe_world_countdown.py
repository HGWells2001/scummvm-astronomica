"""Execute original _do_place rules, including CS switch tables.

External sound calls are recorded, never played. Original files are read only.
No native-engine implementation is imported or used as an oracle.
"""
import json, hashlib
import probe_p526_motion as p

code=p.exe[p.base(9):p.base(9)+0xd00]
ins={i.address:i for i in p.md.disasm(code[0xa09:0xcba],0xa09)}
class Machine(p.Machine):
 def value(self,i,o):
  if o.type==p.X86_OP_MEM and i.reg_name(o.mem.segment)=='cs':
   a=self.address(i,o);return int.from_bytes(code[a:a+o.size],'little')
  return super().value(i,o)

def run(mode,item,stage,started,now):
 m=Machine();m.reg={'ebp':0x9000,'esp':0x8d00}
 m.write(0x7a8,0x7000);m.write(0x70fa,mode);m.write(0x70de,item)
 m.write(0x7102,stage);m.write(0x702a,started);m.write(0xc8c,103)
 pc=0xa09;compare=0;sound=0
 for _ in range(500):
  if pc==0xcba:return [m.read(0x70fa),m.read(0x7102),m.read(0xc8c),m.read(0xc98,2),sound]
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='sub':m.put(i,o[0],v[0]-v[1])
  elif op=='xor':m.put(i,o[0],v[0]^v[1])
  elif op=='cmp':compare=v[0]-v[1]
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='pop':m.put(i,o[0],m.pop(o[0].size))
  elif op=='nop':pass
  elif op=='loop':
   m.setreg('cx',m.getreg('cx')-1)
   if m.getreg('cx'):pc=v[0]
  elif op=='lcall':m.setreg('ax',now&65535);m.setreg('dx',now>>16)
  elif op=='call':
   assert v[0]==0x3b07;m.pop(2);sound=m.read(m.getreg('sp'),2);assert 913<=sound<=919
  elif op in ('jmp','je','jne','jl','jg','jle','jge','jbe'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jl':compare<0,'jg':compare>0,'jle':compare<=0,'jge':compare>=0,'jbe':compare<=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('transition rules did not finish')

if __name__=='__main__':
 elapsed=[0,3999,4000,4001,59999,60000,60001,119999,120000,120001,179999,180000,180001,239999,240000,240001,269999,270000,270001,294999,295000,295001,299999,300000,300001,0xffffffff]
 h=2166136261;cases=0
 for mode in range(5):
  for item in range(3):
   for stage in range(9):
    for started in (0,1,0xfffffff0):
     for age in elapsed:
      result=run(mode,item,stage,started,(started+age)&0xffffffff);cases+=1
      for value in result:h=((h^value)*16777619)&0xffffffff
 p.args.out.write_text(json.dumps(dict(status='Original countdown instruction execution',cases=cases,fnv1a=f'{h:08x}',elapsed=elapsed,
  region='9:0a09-0cba',code_sha256=hashlib.sha256(code[0xa09:0xcba]).hexdigest()),indent=2))
 print(f'Original countdown: {cases} cases, FNV {h:08x}')
