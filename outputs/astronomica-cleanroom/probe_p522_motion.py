"""Execute original P522 callbacks, preserving the caller's computed point.

Only SpriteWorld API effects and nested ellipse execution are supplied by the
existing original-code interpreter. No engine implementation is imported.
"""
import json,struct,hashlib
from probe_p514_motion import Machine as RegionMachine,p
from astro_reader import parse
ins={i.address:i for i in p.md.disasm(p.exe[p.base(3)+0xb2b:p.base(3)+0x10e3],0xb2b)}
custom_ins={i.address:i for i in p.md.disasm(p.exe[p.base(4)+0x32c4:p.base(4)+0x33b7],0x32c4)}
class Machine(RegionMachine):
 def run(self,sprite,point,entry):
  code=custom_ins if entry==0x32c4 else ins
  self.reg={'ebp':0x9000,'esp':0x8f00};self.write(0x9006,sprite);self.write(0x900a,point)
  pc=entry;compare=0
  for _ in range(1000):
   if pc in (0xd61,0xe3e,0x10db,0x33b4):return
   i=code[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[self.value(i,t) for t in o]
   if op=='mov':self.put(i,o[0],v[1])
   elif op=='movsx':self.put(i,o[0],p.signed(v[1],o[1].size))
   elif op=='les':self.setreg(i.reg_name(o[0].reg),v[1]&65535)
   elif op in ('add','sub','xor','or'):
    r={'add':lambda:v[0]+v[1],'sub':lambda:v[0]-v[1],'xor':lambda:v[0]^v[1],'or':lambda:v[0]|v[1]}[op]()
    self.put(i,o[0],r);compare=p.signed(r,o[0].size)
   elif op in ('inc','dec'):self.put(i,o[0],v[0]+(1 if op=='inc' else -1))
   elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
   elif op=='imul':self.put(i,o[0],p.signed(v[-2],o[-2].size)*p.signed(v[-1],o[-1].size))
   elif op=='cdq':self.setreg('edx',0xffffffff if self.getreg('eax')&0x80000000 else 0)
   elif op=='cwde':self.setreg('eax',p.signed(self.getreg('ax'),2))
   elif op=='idiv':
    size=o[0].size;num=p.signed((self.getreg('dx')<<16)|self.getreg('ax'),4) if size==2 else p.signed((self.getreg('edx')<<32)|self.getreg('eax'),8)
    den=p.signed(v[0],size);q=abs(num)//abs(den)*(-1 if (num<0)!=(den<0) else 1)
    self.setreg('ax' if size==2 else 'eax',q);self.setreg('dx' if size==2 else 'edx',num-q*den)
   elif op=='push':self.push(v[0],o[0].size)
   elif op=='nop':pass
   elif op in ('jmp','je','jne','jg','jge','jl','jle'):
    if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jge':compare>=0,'jl':compare<0,'jle':compare<=0}[op]:pc=v[0]
   elif op=='call':
    self.pop();sp=self.getreg('sp')
    if v[0]==0x2733:self.callback(self.read(sp),self.read(sp+4),ellipse=True)
    elif v[0]==0x3748:
     val=self.call_region(*[p.signed(self.read(sp+4*j),4) for j in range(6)]);self.setreg('ax',val);self.setreg('dx',0)
    else:raise AssertionError(('call',hex(i.address),v))
   elif op=='lcall':
    sp=self.getreg('sp');s=self.read(sp)
    if i.address==0x32d6:self.write(s+0x204,1)
    elif i.address==0x3317:
     val=self.call_region(*[p.signed(self.read(sp+2*j,2),2) for j in range(4)],p.signed(self.read(sp+8),4),p.signed(self.read(sp+12),4));self.setreg('ax',val)
    elif i.address in (0xb6d,0xe36):self.locate(s,p.signed(self.read(sp+4,2),2),p.signed(self.read(sp+6,2),2))
    elif i.address in (0xc2a,0xcf9,0xd10,0xd27,0xd3e):self.write(s+0x5b,self.read(sp+4,2))
    elif i.address in (0x1002,0x1019,0x1030,0x1047):
     x=p.signed(self.read(sp+4,2),2);y=p.signed(self.read(sp+6,2),2);l,t,r,b=[p.signed(self.read(s+off,2),2) for off in (0x17,0x19,0x1b,0x1d)]
     self.setreg('ax',int(l<=x<=r and t<=y<=b))
    elif i.address==0x106b:self.write(s+0x10,self.read(sp+4,2),2)
    elif i.address==0x107c:self.write(s+0x204,self.read(sp+4)) # callback removed
    else:raise AssertionError(('lcall',hex(i.address)))
   else:raise AssertionError((hex(i.address),op))
  raise AssertionError('callback did not return')

def setup():
 m=Machine();m.write(0xc88,0x1000);m.write(0xc8c,522);m.write(0x157,1991)
 scene=parse((p.args.root/'PLACES/P522/MEGAFILE.HYP').read_bytes())
 for id in range(9,18):
  s=0x2000+id*0x300;m.write(0x1020+4*id,s);d=scene['sprites'][id-1]
  if id>=15:
   f=d['frames'][0][0];m.write(s+0x1b,f['width'],2);m.write(s+0x1d,f['height'],2);m.locate(s,*d['xy'])
   for off,value in ((0xa5,300),(0xa9,140),(0xb1,226 if id==16 else 120),(0xb5,113 if id==16 else 60)):m.write(s+off,value)
   m.write(s+0x7d,2,2);m.write(s+0x10,id!=17,2)
 return m

def step(m,id):
 s=m.read(0x1020+4*id);point=0x8000
 m.write(point,m.read(s+0x17,2)+p.signed(m.read(s+0x7d,2),2),2)
 m.write(point+2,m.read(s+0x19,2)+p.signed(m.read(s+0x7f,2),2),2)
 if id!=17 or m.read(s+0x204):m.run(s,point,{15:0xb2b,16:0xd75,17:0xe52}[id])
 m.locate(s,p.signed(m.read(point,2),2),p.signed(m.read(point+2,2),2))

m=setup();years=[];h=2166136261
for tick in range(1,20001):
 before=m.read(0x157);step(m,15);step(m,16);step(m,17)
 vals=[m.read(0x157),m.read(0x15b),m.read(m.read(0x1044)+0x5b)]
 for id in (15,16,17):
  s=m.read(0x1020+id*4);vals += [p.signed(m.read(s+o,2),2) for o in (0x17,0x19,0x7d,0x7f)]
 for value in vals:
  for b in struct.pack('<i',value):h=((h^b)*16777619)&0xffffffff
 if m.read(0x157)!=before:years.append(dict(tick=tick,year=m.read(0x157),digits=[m.read(m.read(0x1020+4*i)+0x5b) for i in range(10,14)]))
 if m.read(0xc98,2):break
assert m.read(0xc8c)==388 and years[-1]['year']==2003
result=dict(status='Original evidence; native checks recorded separately',calendar_ticks=tick,calendar_hash=hex(h),years=years)
print('Original P522 calendar: PASS',tick,hex(h),years)

launches=[]
for year,month in [(1991,8),(1992,8),(1994,10),(1997,0),(1999,3),(2001,5)]:
 m=setup();launched=False;trace=2166136261
 for tick in range(1,6001):
  step(m,15);step(m,16)
  if not launched:
   earth=m.read(0x105c);x=p.signed(m.read(earth+0x17,2),2);y=p.signed(m.read(earth+0x19,2),2)
   current=(8-m.call_region(300,140,300,20,x,y))%12
   if m.read(0x157)==year and current==month:
    m.run(0,0,0x32c4);launched=True;launch_tick=tick;m.write(m.read(0x1064)+0x10,1,2)
  if launched:
   probe=m.read(0x1064)
   step(m,17)
   row=[m.read(0x13fc),m.read(0x15f),m.read(probe+0xb1),m.read(probe+0xb5)]+[p.signed(m.read(probe+o,2),2) for o in (0x17,0x19,0x7d,0x7f)]
   for value in row:
    for b in struct.pack('<i',value):trace=((trace^b)*16777619)&0xffffffff
   if m.read(0x13fc)!=1:
    launches.append(dict(year=year,month=month,launch_tick=launch_tick,end_tick=tick,state=m.read(0x13fc),special=m.read(0x15f),hash=hex(trace),radius=m.read(probe+0xb1),visible=m.read(probe+0x10,2)));break
  if m.read(0xc98,2):raise AssertionError(('expired',year,month))
 else:raise AssertionError(('launch not resolved',year,month))
assert [r['state'] for r in launches]==[0,2,2,2,2,2],launches
result['launches']=launches
# Collision tests use the original rectangle before the caller commits its point.
collisions=[]
for state in (0,1,2):
 for special in (0,1):
  for dx,dy in ((-40,0),(-20,0),(-1,0),(0,0),(1,0),(20,0),(40,0),(0,-40),(0,-1),(0,1),(0,40)):
   m=setup();probe=m.read(0x1064);mars=m.read(0x1060)
   m.locate(probe,300,140);m.locate(mars,300+dx,140+dy)
   m.write(probe+0xb1,226);m.write(probe+0xb5,113);m.write(probe+0x10,1,2);m.write(probe+0x204,1)
   m.write(0x13fc,state);m.write(0x15f,special)
   l,t,r,b=[p.signed(m.read(probe+o,2),2) for o in (0x17,0x19,0x1b,0x1d)]
   ml,mt,mr,mb=[p.signed(m.read(mars+o,2),2) for o in (0x17,0x19,0x1b,0x1d)]
   hit=bool(special or any(l<=x<=r and t<=y<=b for x,y in ((ml,mt),(mr,mt),(ml,mb),(mr,mb))))
   step(m,17);expected=(2 if hit else 0) if state==1 else state
   assert m.read(0x13fc)==expected,(state,special,dx,dy,expected)
   if state==1 and not hit:assert m.read(probe+0x10,2)==0 and m.read(probe+0x204)==0 and m.read(probe+0xb1)==120
   collisions.append([state,special,dx,dy,m.read(0x13fc),m.read(probe+0xb1),m.read(probe+0x10,2)])
corrections=[]
for state in (0,1,2):
 for special in (0,1):
  for radius in (173,174):
   for dx in (-10,0,10):
    for dy in (-10,0,10):
     m=setup();mars=m.read(0x1060);probe=m.read(0x1064)
     # Compute this exact Mars step once without the correction conditions.
     step(m,16);mx=p.signed(m.read(mars+0x17,2),2);my=p.signed(m.read(mars+0x19,2),2)
     m=setup();m.locate(probe,mx+dx,my+dy);m.write(probe+0xb1,radius);m.write(0x13fc,state);m.write(0x15f,special)
     step(m,16);active=state==1 and special and radius>173
     expected=[mx+dx-((dx>0)-(dx<0))*bool(active),my+dy-((dy>0)-(dy<0))*bool(active)]
     actual=[p.signed(m.read(probe+o,2),2) for o in (0x17,0x19)]
     assert actual==expected,(state,special,radius,dx,dy,actual,expected)
     corrections.append([state,special,radius,dx,dy]+actual)
result['collision_cases']=len(collisions);result['collision_sha256']=hashlib.sha256(json.dumps(collisions).encode()).hexdigest()
result['correction_cases']=len(corrections);result['correction_sha256']=hashlib.sha256(json.dumps(corrections).encode()).hexdigest()
p.args.out.write_text(json.dumps(result,indent=2))
print('Original P522 launches: PASS',launches)
print('Collision/correction cases: PASS',len(collisions),len(corrections))
