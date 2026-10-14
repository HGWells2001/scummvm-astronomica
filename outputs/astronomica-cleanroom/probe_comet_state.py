"""Execute original custom8 (P502/P503/P504), including its setup setters."""
import json,struct,hashlib
import probe_p526_motion as p
import probe_p501_state as base
ins={i.address:i for i in p.md.disasm(p.exe[p.base(4)+0xca5:p.base(4)+0x1c36],0xca5)}
relocs=base.relocs
def run(m,mode,entry=None,end=0x1c33):
 m.reg={'ebp':0x9000,'esp':0x8d00};pc=entry if entry is not None else 0xca5 if mode==0 else 0xfd9;compare=0
 for _ in range(3000):
  if pc==end:return
  i=ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[m.value(i,t) for t in o]
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='movsx':m.put(i,o[0],p.signed(v[1],o[1].size))
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='lea':m.put(i,o[0],m.address(i,o[1]))
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='sub':m.put(i,o[0],v[0]-v[1])
  elif op=='inc':m.put(i,o[0],v[0]+1)
  elif op=='shl':m.put(i,o[0],v[0]<<v[1])
  elif op=='imul':m.put(i,o[0],p.signed(v[-2],o[-2].size)*p.signed(v[-1],o[-1].size))
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='cdq':m.setreg('edx',0xffffffff if m.getreg('eax')&0x80000000 else 0)
  elif op=='idiv':
   n=p.signed((m.getreg('edx')<<32)|m.getreg('eax'),8);d=p.signed(v[0],4);q=abs(n)//abs(d)*(-1 if (n<0)!=(d<0) else 1)
   m.setreg('eax',q);m.setreg('edx',n-q*d)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='pop':m.put(i,o[0],m.pop(o[0].size))
  elif op=='lcall':
   sp=m.getreg('sp');name=relocs[i.address+1];s=m.read(sp)
   if name=='_pend_command':m.commands.append([m.read(s),m.read(s+4),m.read(s+8),m.read(s+0x34)])
   elif name=='_playSound':m.sounds.append(m.read(sp,2))
   elif name=='_hide_and_stop':
    target=m.read(0x1020+4*s)
    for off in (0x39,0x6f):m.write(target+off,-1)
    for off in (0x10,0x7d,0x7f):m.write(target+off,0,2)
   elif name=='_SWSetSpriteMoveProc':
    ref=max(r for r in relocs if r<i.address and relocs[r] and relocs[r].startswith('_fxm_'))
    assert i.address-ref<100,(hex(i.address),hex(ref));m.procs[s]=relocs[ref]
   elif name=='_SWSetSpriteMoveDelta':m.write(s+0x7d,m.read(sp+4,2),2);m.write(s+0x7f,m.read(sp+6,2),2)
   elif name=='_SWSetSpriteMoveBounds':assert m.read(sp+4)==s+0x81
   elif name in ('_SWSetSpriteMoveTime','_SWSetSpriteFrameTime'):
    for off in ((0x79,0x6f) if name=='_SWSetSpriteMoveTime' else (0x39,)):m.write(s+off,m.read(sp+4))
   elif name=='_SWSetSpriteLocation':m.locate(s,p.signed(m.read(sp+4,2),2),p.signed(m.read(sp+6,2),2))
   elif name=='_SWSetSpriteVisible':m.write(s+0x10,m.read(sp+4,2),2)
   elif name=='_SWSetCurrentFrameIndex':m.write(s+0x5b,m.read(sp+4,2))
   elif i.address in (0x18e3,0x1b97):m.setreg('ax',0);m.setreg('dx',0)
   else:raise AssertionError((hex(i.address),name))
  elif op in ('jmp','je','jne','jg','jge','jl','jle'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jge':compare>=0,'jl':compare<0,'jle':compare<=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('custom8 did not return')

def machine(direction,speed,target,mask):
 m=p.Machine();m.commands=[];m.sounds=[];m.procs={};m.write(0xc88,0x1000)
 for id in range(1,50):
  s=0x2000+id*0x100;m.write(0x1020+4*id,s);m.write(s+0x1b,16,2);m.write(s+0x1d,16,2)
  m.write(s+0x39,-1);m.write(s+0x6f,-1)
 for id,value in enumerate([direction,speed,target]+[(mask>>(i-3))&1 for i in range(3,9)]):m.write(0x13f8+4*id,value)
 return m
def snapshot(m):
 sprites=[]
 for id in range(1,50):
  s=m.read(0x1020+4*id)
  vals=[p.signed(m.read(s+o,2),2) for o in (0x10,0x17,0x19,0x7d,0x7f)]+[p.signed(m.read(s+o),4) for o in (0x5b,0x39,0x6f,0xa5,0xa9,0xad,0xb1,0xb5,0xb9,0xbd,0xc1)]
  if s in m.procs or vals[:6]!=[0]*6 or vals[6:8]!=[-1,-1] or any(vals[8:]):sprites.append(dict(id=id,fields=vals,callback=m.procs.get(s)))
 return dict(local=[m.read(0x13f8+4*n) for n in range(9)],locked=m.read(0x6a5,2),commands=m.commands,sounds=m.sounds,sprites=sprites)
if __name__=='__main__':
 rows=[]
 for mode in (0,1):
  for target in range(1,11):
   for speed in range(16):
    for direction in range(1,5):
     for mask in ((0,) if mode==0 else (0,31)):
      m=machine(direction,speed,target,mask);run(m,mode);rows.append(dict(input=[mode,target,speed,direction,mask],**snapshot(m)))
 p.args.out.write_text(json.dumps(dict(status='Original instruction evidence; not native validation',cases=len(rows),rows=rows,code_sha256=hashlib.sha256(p.exe[p.base(4)+0xc74:p.base(4)+0x1c36]).hexdigest()),indent=2))
 print('Original comet setup:',len(rows),'cases PASS')
