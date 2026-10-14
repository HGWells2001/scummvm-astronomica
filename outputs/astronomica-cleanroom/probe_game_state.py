"""Execute original custom26 state transfers. No native-engine code is read.

This is research evidence only; it does not implement the missing command.
"""
import json, hashlib
import probe_p526_motion as p

code=p.exe[p.base(4):p.base(4)+0x8000]
ins={i.address:i for i in p.md.disasm(code[0x5a91:0x6310],0x5a91)}
class Machine(p.Machine):
 def value(self,i,o):
  if o.type==p.X86_OP_MEM and i.reg_name(o.mem.segment)=='cs':
   a=self.address(i,o);return int.from_bytes(code[a:a+o.size],'little')
  return super().value(i,o)

def run(key,local,mode,selector,completed,setting,helpRunning,availableBytes):
 m=Machine();m.reg={'ebp':0x9000,'esp':0x8d00,'esi':1}
 m.write(0x9006,0x2000);m.write(0xc88,0x3000);m.write(0x7a8,0x6000)
 for index,value in enumerate((26,key,local,mode,selector,0)):m.write(0x2004+4*index,value)
 for index in range(100):
  m.write(0x600a+4*index,0x12340000+index)
  m.write(0x33f8+4*index,0x45670000+index)
 m.write(0x153,completed);m.write(0x7a0,setting,2);m.write(0x79c,helpRunning,2);m.write(0xbd0,availableBytes)
 pc=0x5a91;compare=0
 for _ in range(1000):
  if pc==0x6310:
   return [m.read(0x33f8+4*i) for i in range(100)]+[m.read(0x600a+4*i) for i in range(100)]
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='shl':m.put(i,o[0],v[0]<<v[1])
  elif op=='xor':m.put(i,o[0],v[0]^v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='pop':m.put(i,o[0],m.pop(o[0].size))
  elif op=='nop':pass
  elif op=='loop':
   m.setreg('cx',m.getreg('cx')-1)
   if m.getreg('cx'):pc=v[0]
  elif op in ('jmp','je','jne','jl','jg','jle','jge'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jl':compare<0,'jg':compare>0,'jle':compare<=0,'jge':compare>=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('custom26 did not finish')

if __name__=='__main__':
 h=2166136261;count=0
 for key in range(1,15):
  for local in (0,3,99):
   for mode in (0,1):
    for selector in range(29):
     result=run(key,local,mode,selector,31,1,0,0)
     count+=1
     for value in result:h=((h^value)*16777619)&0xffffffff
 boundary=[]
 for setting in (0,1,2):
  for flag in (0,1):
   for availableBytes in (0,1649999,1650000,1650001,2399999,2400000,2400001):
    boundary.append(dict(setting=setting,help_running=flag,availableBytes=availableBytes,
     key13=run(13,0,0,0,31,setting,flag,availableBytes)[0],key14=run(14,0,0,0,31,setting,flag,availableBytes)[0]))
 bh=2166136261
 for row in boundary:
  for value in (row['key13'],row['key14']):bh=((bh^value)*16777619)&0xffffffff
 output=dict(boundary_fnv1a=f'{bh:08x}',status='Research only; original custom26 instruction execution',
  cases=count,native_comparison_fnv1a=f'{h:08x}',boundaries=boundary,
  result_layout='100 local values followed by100 globals',
  initial_values='local[i]=0x45670000+i; global[i]=0x12340000+i',
  code_sha256=hashlib.sha256(code[0x5a91:0x6310]).hexdigest())
 p.args.out.write_text(json.dumps(output,indent=2));print(f'Original custom26: {count} cases, FNV {h:08x}')
