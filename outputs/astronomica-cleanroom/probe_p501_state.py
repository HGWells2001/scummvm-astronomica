"""Original custom7 state transitions, generated commands, sounds and hit windows."""
import json,struct,hashlib
import probe_p526_motion as p
symbols=json.loads((p.Path(__file__).parent/'evidence/debug/symbols.json').read_text())
names={(s['segment'],s['offset']):s['name'] for s in symbols}
size=struct.unpack_from('<H',p.exe,p.table+24+2)[0];relocs={}
for j in range(struct.unpack_from('<H',p.exe,p.base(4)+size)[0]):
 typ,flags,src,t1,t2=struct.unpack_from('<BBHHH',p.exe,p.base(4)+size+2+8*j);seen=set()
 while src!=65535 and src not in seen and src+2<=size:
  seen.add(src);relocs[src]=names.get((t1,t2),'import')
  if flags&4:break
  src=struct.unpack_from('<H',p.exe,p.base(4)+src)[0]
ins={i.address:i for i in p.md.disasm(p.exe[p.base(4)+0x29e:p.base(4)+0xc74],0x29e)}
def run(m,mode,depth=0):
 saved=m.reg.copy();bp=0x9000-0x400*depth;m.reg={'ebp':bp,'esp':bp-0x200}
 for off,value in ((0x102,30),(0xfe,25),(0xfa,0),(0xd2,0),(0xce,500),(0xd6,0),(0xca,0)):m.write(bp-off,value)
 pc={0:0x30e,1:0x8ab,2:0xa63,3:0xacc,4:0xb49}[mode];compare=0
 for _ in range(700):
  if pc==0xc71:m.reg=saved;return
  i=ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[m.value(i,t) for t in o]
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='movsx':m.put(i,o[0],p.signed(v[1],o[1].size))
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='lea':m.put(i,o[0],m.address(i,o[1]))
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='sub':m.put(i,o[0],v[0]-v[1])
  elif op=='inc':m.put(i,o[0],v[0]+1)
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='cwde':m.setreg('eax',p.signed(m.getreg('ax'),2))
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='pop':m.put(i,o[0],m.pop(o[0].size))
  elif op=='call':
   assert v[0]==0x25;m.pop();cmd=m.read(m.getreg('sp'));assert m.read(cmd+4)==7
   run(m,m.read(cmd+8),depth+1)
  elif op=='lcall':
   sp=m.getreg('sp');name=relocs[i.address+1];target=m.read(sp)
   if name=='_pend_command':m.commands.append([m.read(target),m.read(target+4),m.read(target+8),m.read(target+0x34),bool(m.read(target+0x2c))])
   elif name in ('_playSound','_stop_sounds'):m.sounds.append([name,p.signed(m.read(sp,2),2)])
   elif name=='_SWSetSpriteMoveProc':m.proc={0x3b1:1,0x481:5,0x6f7:4}[i.address]
   elif name=='_SWSetSpriteMoveDelta':m.write(target+0x7d,m.read(sp+4,2),2);m.write(target+0x7f,m.read(sp+6,2),2)
   elif name=='_SWSetSpriteMoveBounds':assert m.read(sp+4)==target+0x81
   elif name=='_SWSetSpriteMoveTime':
    for off in (0x79,0x6f):m.write(target+off,m.read(sp+4))
   elif name=='_malloc':m.setreg('ax',0x6000);m.setreg('dx',0)
   elif i.address==0xbaf:assert m.read(sp+4)==0x177
   else:raise AssertionError((hex(i.address),name))
  elif op in ('jmp','je','jne','jg','jge','jl','jle'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jge':compare>=0,'jl':compare<0,'jle':compare<=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('custom7 did not return')

def case(mode,scenario,state,miss,diff):
 m=p.Machine();m.commands=[];m.sounds=[];m.proc=0;m.write(0xc88,0x1000);m.write(0x1084,0x2000);m.write(0x1088,0x2400)
 for n,value in enumerate((scenario,state,miss,0)):m.write(0x13f8+4*n,value)
 m.write(0x24a5,157)
 m.write(0x201f,157+diff,2);m.write(0x2017,157+diff,2);m.write(0x2019,182,2)
 run(m,mode)
 return dict(input=[mode,scenario,state,miss,diff],local=[m.read(0x13f8+4*n) for n in range(4)],commands=m.commands,sounds=m.sounds,callback=m.proc,motion=[p.signed(m.read(0x2000+off),4) for off in (0xa5,0xa9,0xad,0xb1,0xb5,0xbd,0xc1,0x6f)])

if __name__=='__main__':
 rows=[case(mode,scenario,state,miss,diff) for mode in range(5) for scenario in (0,1,2,3,4,5) for state in range(4) for miss in range(3) for diff in (-31,-30,-29,0,40,41,59,60,99,100)]
 assert p.exe[p.base(20)+0x177:p.base(20)+0x180]==b'backorbi\0'
 p.args.out.write_text(json.dumps(dict(scene=501,status='Original instruction evidence; not native validation',cases=len(rows),rows=rows,background='backorbi',code_sha256=hashlib.sha256(p.exe[p.base(4)+0x29e:p.base(4)+0xc74]).hexdigest()),indent=2))
 print('Original P501 state: PASS',len(rows),'cases')

