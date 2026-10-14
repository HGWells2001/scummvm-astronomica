"""Execute original _do_place rules, including CS switch tables.

External sound calls are recorded, never played. Original files are read only.
No native-engine implementation is imported or used as an oracle.
"""
import json, hashlib
import probe_p526_motion as p

code=p.exe[p.base(9):p.base(9)+0x800]
ins={i.address:i for i in p.md.disasm(code[0x289:0x66c],0x289)}
class Machine(p.Machine):
 def value(self,i,o):
  if o.type==p.X86_OP_MEM and i.reg_name(o.mem.segment)=='cs':
   a=self.address(i,o);return int.from_bytes(code[a:a+o.size],'little')
  return super().value(i,o)

def run(previous,destination,values):
 m=Machine();m.reg={'ebp':0x9000,'esp':0x8d00,'esi':1}
 m.write(0xc94,previous);m.write(0xc8c,destination);m.write(0x7a8,0x2000)
 for index,value in enumerate(values):m.write(0x200a+4*index,value)
 pc=0x289;compare=0;sound=0
 for _ in range(1000):
  if pc==0x66c:return [p.signed(m.read(0xc8c),4),p.signed(m.read(0x20ee),4),int(m.getreg('si')==0),sound]
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='xor':m.put(i,o[0],v[0]^v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='pop':m.put(i,o[0],m.pop(o[0].size))
  elif op=='nop':pass
  elif op=='loop':
   m.setreg('cx',m.getreg('cx')-1)
   if m.getreg('cx'):pc=v[0]
  elif op=='call':
   assert v[0]==0x3b07;m.pop(2);sound=m.read(m.getreg('sp'),2);assert sound==910
  elif op in ('jmp','je','jne','jl','jg','jle','jge'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jl':compare<0,'jg':compare>0,'jle':compare<=0,'jge':compare>=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('transition rules did not finish')

if __name__=='__main__':
 h=2166136261;count=0
 def fold(previous,destination,values):
  global h,count
  result=run(previous,destination,values);count+=1
  for v in result:h=((h^(v&0xffffffff))*16777619)&0xffffffff
  return result
 destinations=[-1,117,408,409,500,501,502,503,504,506,507,508,513,515,520,531,535,536,537,538,599,600]
 for previous in list(range(501,538))+[500,538,599,600,408,409,103]:
  for destination in destinations:
   for pattern in range(-2,47):
    values=[int(pattern==-2 or i==pattern) for i in range(100)]
    fold(previous,destination,values)
 pairs=[(307,414),(271,298),(284,289),(324,329),(101,110),(120,144),(177,182),(139,151),(160,168),(208,117),(387,117)]
 examples=[]
 for previous,destination in pairs:
  for reverse in range(2):
   a,b=(destination,previous) if reverse else (previous,destination)
   for permit in (-1,0,1,2):
    values=[0]*100;values[57]=permit
    result=fold(a,b,values)
    examples.append(dict(previous=a,requested=b,permit=permit,result=result))
 result=dict(status='Original instructions executed independently of native engine',
  region='9:0289-066c; CS switch table through078f',
  code_sha256=hashlib.sha256(code[0x289:0x797]).hexdigest(),
  cases=count,native_comparison_fnv1a=f'{h:08x}',examples=examples,
  result_fields=['destination','global57','deferred_failure_voice','immediate_direct_sound'])
 p.args.out.write_text(json.dumps(result,indent=2))
 print(f'Original transition rules: {count} cases, FNV {h:08x}')
