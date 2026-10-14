"""Execute custom27 from original ASTRO.EXE; record external movie calls.

No native-engine tables are inputs. Separate CS switch tables from DS state.
Untouched stack output is rejected instead of inventing a default movie range.
"""
import json, struct, hashlib
import probe_p526_motion as p
import probe_comet_state as setup

code=p.exe[p.base(4):p.base(4)+0x8f7e]
ins={i.address:i for i in p.md.disasm(code[0x6313:0x67d6],0x6313)}
class Machine(p.Machine):
 def value(self,i,o):
  if o.type==p.X86_OP_MEM and i.reg_name(o.mem.segment)=='cs':
   a=self.address(i,o);return int.from_bytes(code[a:a+o.size],'little')
  return super().value(i,o)

def run(previous,completed,solved,stage,flag55,flag56,draws):
 m=Machine();m.reg={'ebp':0x9000,'esp':0x8d00}
 m.write(0xc94,previous);m.write(0x153,completed);m.write(0x7a8,0x7000)
 for n,value in ((45,solved),(6,stage),(55,flag55),(56,flag56)):m.write(0x700a+n*4,value)
 m.write(0xc88,0x1000);m.write(0x1368,0x6000)
 m.write(0x8ff2,0xdeadbeef);m.write(0x8fee,0xdeadbeef)
 pc=0x6313;compare=0;calls=[];used=0
 for _ in range(1000):
  if pc==0x38f2:
   return dict(side=m.read(0x13f8),stage=m.read(0x7022),flag55=m.read(0x70e6),flag56=m.read(0x70ea),calls=calls,random_calls=used)
  if pc==0x678c:assert m.read(0x8ff2)!=0xdeadbeef and m.read(0x8fee)!=0xdeadbeef
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='sub':m.put(i,o[0],v[0]-v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='loop':
   m.setreg('cx',m.getreg('cx')-1)
   if m.getreg('cx'):pc=v[0]
  elif op in ('jmp','je','jne','jg','jl'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jl':compare<0}[op]:pc=v[0]
  elif op=='movzx':m.put(i,o[0],v[1])
  elif op=='lcall':
   sp=m.getreg('sp');name=setup.relocs[i.address+1]
   if name=='_RangedRdm':
    low,high=m.read(sp,2),m.read(sp+2,2);value=draws[used];used+=1
    assert low<=value<=high,(value,low,high);m.setreg('ax',value)
   else:
    assert m.read(sp)==0x6000
    if name=='_SetMovieActiveSegment':calls.append(dict(name=name,start=m.read(sp+4),duration=m.read(sp+8)))
    else:assert name=='_StopMovie';calls.append(dict(name=name))
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('custom27 did not return')

if __name__=='__main__':
 draws=[(0,n) for n in range(1,14)]+[(1,n,k) for n in range(1,5) for k in range(1,5)]
 rows=[];h=2166136261;cases=0
 for previous in (103,208):
  for completed in (0,1,2,8,9,21,22,25,26,27):
   for solved in (0,1,2):
    for stage in (0,1,2,3):
     for flag55,flag56 in ((0,0),(1,0),(0,1),(1,1),(2,2)):
      for random in draws:
       result=run(previous,completed,solved,stage,flag55,flag56,random);cases+=1
       clip=result['calls'][0]
       for value in (result['side'],result['stage'],result['flag55'],result['flag56'],clip['start'],clip['duration'],result['random_calls']):h=((h^value)*16777619)&0xffffffff
 for random in draws:rows.append(dict(draws=random,result=run(103,0,0,0,0,0,random)))
 p.args.out.write_text(json.dumps(dict(status='Original custom27 research only; not integrated',cases=cases,
  original_fnv1a=f'{h:08x}',random_branches=rows,code_sha256=hashlib.sha256(code[0x6313:0x67d6]).hexdigest()),indent=2))
 print(f'Original custom27: {cases} cases, FNV {h:08x}')
