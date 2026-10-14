"""Execute original P501 ball callbacks; no prior engine implementation used."""
import json, struct, hashlib
import probe_p526_motion as p

symbols=json.loads((p.Path(__file__).parent/'evidence/debug/symbols.json').read_text())
names={(s['segment'],s['offset']):s['name'] for s in symbols}
size=struct.unpack_from('<H',p.exe,p.table+16+2)[0];relocs={}
for j in range(struct.unpack_from('<H',p.exe,p.base(3)+size)[0]):
 typ,flags,src,t1,t2=struct.unpack_from('<BBHHH',p.exe,p.base(3)+size+2+8*j);seen=set()
 while src!=65535 and src not in seen and src+2<=size:
  seen.add(src);relocs[src]=names.get((t1,t2),'import')
  if flags&4:break
  src=struct.unpack_from('<H',p.exe,p.base(3)+src)[0]
ins={i.address:i for i in p.md.disasm(p.exe[p.base(3)+0x23b:p.base(3)+0x6ee],0x23b)}

def run(m,scenario,sprite,point):
 m.reg={'ebp':0x9000,'esp':0x8f00};m.write(0x9006,sprite);m.write(0x900a,point)
 pc={1:0x60f,4:0x248,5:0x481}[scenario];compare=0
 for _ in range(500):
  if pc in (0x46d,0x5fb,0x6e8):return
  i=ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[m.value(i,t) for t in o]
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='movsx':m.put(i,o[0],p.signed(v[1],o[1].size))
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='lea':m.put(i,o[0],m.address(i,o[1]))
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='sub':m.put(i,o[0],v[0]-v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='imul':m.put(i,o[0],p.signed(v[0],o[0].size)*p.signed(v[1],o[1].size))
  elif op=='cwde':m.setreg('eax',p.signed(m.getreg('ax'),2))
  elif op=='cdq':m.setreg('edx',0xffffffff if m.getreg('eax')&0x80000000 else 0)
  elif op=='idiv':
   n=p.signed((m.getreg('edx')<<32)|m.getreg('eax'),8);d=p.signed(v[0],4)
   q=abs(n)//abs(d)*(-1 if (n<0)!=(d<0) else 1);m.setreg('eax',q);m.setreg('edx',n-q*d)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='pop':m.put(i,o[0],m.pop(o[0].size))
  elif op=='nop':pass
  elif op=='call':
   assert v[0]==0x33e5;m.pop();assert m.read(m.getreg('sp'),2)==25
   for off in (0x39,0x6f):m.write(sprite+off,-1)
   for off in (0x10,0x7d,0x7f):m.write(sprite+off,0,2)
  elif op=='lcall':
   sp=m.getreg('sp');name=relocs[i.address+1]
   if name=='_SWSetSpriteMoveTime':
    target=m.read(sp);period=m.read(sp+4)
    for off in (0x79,0x6f):m.write(target+off,period)
   elif name=='_pend_command':
    cmd=m.read(sp);m.commands.append([m.read(cmd),m.read(cmd+4),m.read(cmd+8),m.read(cmd+0x34)])
   elif i.address==0x2e6:m.setreg('ax',0);m.setreg('dx',0)
   else:raise AssertionError((hex(i.address),name))
  elif op in ('jmp','je','jne','jg','jge','jl','jle'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jge':compare>=0,'jl':compare<0,'jle':compare<=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('callback did not return')

def machine(scenario,x,y):
 m=p.Machine();s=0x2000;m.commands=[];m.write(s+0x1b,16,2);m.write(s+0x1d,16,2);m.locate(s,x,y)
 for off,value in ((0x10,1),(0x85,640),(0x87,320),(0x7d,5 if scenario==1 else 2),(0x7f,-3 if scenario==1 else -2 if scenario==4 else 0)):
  m.write(s+off,value,2)
 for off,value in ((0xa5,x+(320 if scenario==4 else 200)),(0xa9,y),(0xbd,2),(0x79,10),(0x6f,10)):
  m.write(s+off,value)
 return m,s

def step(m,scenario,s):
 point=0x8000
 m.write(point,m.read(s+0x17,2)+p.signed(m.read(s+0x7d,2),2),2)
 m.write(point+2,m.read(s+0x19,2)+p.signed(m.read(s+0x7f,2),2),2)
 run(m,scenario,s,point);m.locate(s,p.signed(m.read(point,2),2),p.signed(m.read(point+2,2),2))
 return [p.signed(m.read(s+off,2),2) for off in (0x17,0x19,0x7d,0x7f,0x10)]+[p.signed(m.read(s+off),4) for off in (0x79,0x6f,0xbd)]

if __name__=='__main__':
 traces=[]
 for scenario,y in ((1,207),(4,182),(5,197)):
  for x in (210,240,260):
   m,s=machine(scenario,x,y);h=2166136261;now=0;events=[]
   for tick in range(1,1601):
    now+=m.read(s+0x6f);row=step(m,scenario,s)
    for b in struct.pack('<9i',now,*row):h=((h^b)*16777619)&0xffffffff
    if tick<=3 or row[5]!=10:events.append(dict(tick=tick,time=now,values=row))
    if not row[4] or now>=16000:break
   traces.append(dict(scenario=scenario,start=[x,y],ticks=tick,time=now,last=row,events=events,commands=m.commands,fnv1a32=hex(h)))
 edges=[]
 for scenario in (1,4,5):
  for x,y in ((640,180),(641,180),(-16,180),(-17,180),(240,320),(240,321),(240,-16),(240,-17)):
   m,s=machine(scenario,x,y);edges.append(dict(scenario=scenario,start=[x,y],after=step(m,scenario,s),commands=m.commands))
 p.args.out.write_text(json.dumps(dict(scene=501,status='Original instruction evidence; not native validation',traces=traces,edges=edges,timer='SWSetSpriteMoveTime writes both 0x79 and 0x6f; Vesta pauses 5000 ms once after wrapping, then restores 10 ms',code_sha256=hashlib.sha256(p.exe[p.base(3)+0x23b:p.base(3)+0x6ee]).hexdigest()),indent=2))
 print('Original P501 motion: PASS',len(traces),'traces;',len(edges),'boundary cases')
