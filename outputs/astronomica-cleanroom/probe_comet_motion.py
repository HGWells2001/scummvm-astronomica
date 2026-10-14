"""Original comet approach, crash, escape and orbit callbacks with partner swaps."""
import json,struct,hashlib
import probe_p526_motion as p
import probe_comet_state as setup
import probe_p501_motion as calls
ins={i.address:i for i in p.md.disasm(p.exe[p.base(3)+0x22b3:p.base(3)+0x2733],0x22b3)}
class Machine(p.Machine):
 def custom_call(self,addr,sp):
  name=calls.relocs[addr+1];s=self.read(sp)
  if name in ('_SWMoveSprite','_SWSetSpriteLocation'):
   self.locate(s,p.signed(self.read(sp+4,2),2),p.signed(self.read(sp+6,2),2))
  elif name=='_SWSetSpriteVisible':self.write(s+0x10,self.read(sp+4,2),2)
  elif name=='_SWSetCurrentFrameIndex':self.write(s+0x5b,self.read(sp+4,2))
  elif name=='_SWSetSpriteMoveProc':
   assert addr==0x233a;self.procs[s]='_fxm_move_ellipse'
  elif name=='_playSound':self.sounds.append(self.read(sp,2))
  else:raise AssertionError((hex(addr),name))
 def run(self,s,point):
  kind=self.procs[s]
  if kind=='_fxm_move_ellipse':
   if not self.read(s+0x10,2) and not self.read(s+0x7d,2) and not self.read(s+0x7f,2):return
   self.callback(s,point,entry=0x27a9);return
  pc={'_fxm_move_comet':0x22c0,'_fxm_move_comet_to_sun':0x251d,'_fxm_move_comet_off_screen':0x269a}[kind]
  self.reg={'ebp':0x9000,'esp':0x8d00};self.write(0x9006,s);self.write(0x900a,point);compare=0
  for _ in range(500):
   if pc in (0x23ea,0x2686,0x272d):return
   i=ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[self.value(i,t) for t in o]
   if op=='mov':self.put(i,o[0],v[1])
   elif op=='movsx':self.put(i,o[0],p.signed(v[1],o[1].size))
   elif op=='les':self.setreg(i.reg_name(o[0].reg),v[1]&65535)
   elif op in ('add','sub','or'):
    result=v[0]+v[1] if op=='add' else v[0]-v[1] if op=='sub' else v[0]|v[1];self.put(i,o[0],result);compare=p.signed(result,o[0].size)
   elif op=='dec':self.put(i,o[0],v[0]-1)
   elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
   elif op=='cwde':self.setreg('eax',p.signed(self.getreg('ax'),2))
   elif op=='imul':
    if len(o)==1:
     product=p.signed(self.getreg('ax'),2)*p.signed(v[0],2);self.setreg('ax',product);self.setreg('dx',product>>16)
    else:self.put(i,o[0],p.signed(v[-2],o[-2].size)*p.signed(v[-1],o[-1].size))
   elif op=='cdq':
    # Capstone labels opcode99 cdq even in this 16-bit image; 66 selects32.
    wide=0x66 in i.prefix;self.setreg('edx' if wide else 'dx',-1 if p.signed(self.getreg('eax' if wide else 'ax'),4 if wide else 2)<0 else 0)
   elif op=='idiv':
    wide=o[0].size==4;bits=32 if wide else 16;lo='eax' if wide else 'ax';hi='edx' if wide else 'dx'
    n=p.signed((self.getreg(hi)<<bits)|self.getreg(lo),bits//4);d=p.signed(v[0],o[0].size)
    q=abs(n)//abs(d)*(-1 if (n<0)!=(d<0) else 1);self.setreg(lo,q);self.setreg(hi,n-q*d)
   elif op=='push':self.push(v[0],o[0].size)
   elif op=='pop':self.put(i,o[0],self.pop(o[0].size))
   elif op=='nop':pass
   elif op=='lcall':self.custom_call(i.address,self.getreg('sp'))
   elif op=='call':
    self.pop();sp=self.getreg('sp');id=self.read(sp);target=self.read(0x1020+4*id)
    if v[0]==0x33e5:
     for off in (0x39,0x6f):self.write(target+off,-1)
     for off in (0x10,0x7d,0x7f):self.write(target+off,0,2)
    elif v[0]==0x364e:self.explosions.append([id,self.read(sp+4),self.read(sp+8),self.read(sp+12)])
    else:raise AssertionError(hex(v[0]))
   elif op in ('jmp','je','jne','jg','jge','jl','jle'):
    if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jge':compare>=0,'jl':compare<0,'jle':compare<=0}[op]:pc=v[0]
   else:raise AssertionError((hex(i.address),op))
  raise AssertionError('callback did not return')

def trace(target,speed,direction):
 m=setup.machine(direction,speed,target,0);m.__class__=Machine;m.explosions=[];setup.run(m,1)
 ids=sorted((s-0x2000)//0x100 for s in m.procs);primary=20 if target==10 else target+(22 if target<=4 else 19)
 # SpriteWorld traverses appended layers1 then2; the primary is always layer1.
 ids.sort(key=lambda id:(id!=primary,id));h=2166136261;events=[];previous=None
 for now in range(10,20001,10):
  for id in ids:
   s=m.read(0x1020+4*id);period=p.signed(m.read(s+0x6f),4)
   if period<0 or now-m.read(s+0x6b)<period:continue
   m.write(s+0x6b,now);point=0x8000
   m.write(point,m.read(s+0x17,2)+p.signed(m.read(s+0x7d,2),2),2);m.write(point+2,m.read(s+0x19,2)+p.signed(m.read(s+0x7f,2),2),2)
   m.run(s,point);m.locate(s,p.signed(m.read(point,2),2),p.signed(m.read(point+2,2),2))
  row=[]
  for id in ids:
   s=m.read(0x1020+4*id)
   row += [p.signed(m.read(s+o,2),2) for o in (0x17,0x19,0x7d,0x7f,0x10)]+[p.signed(m.read(s+o),4) for o in (0x5b,0x6f,0xbd,0xc1)]
  for b in struct.pack('<'+'i'*len(row),*row):h=((h^b)*16777619)&0xffffffff
  visible=[m.read(m.read(0x1020+4*id)+0x10,2) for id in ids]
  if visible!=previous:events.append(dict(time=now,values=row));previous=visible
  if not any(visible):break
 return dict(target=target,speed=speed,direction=direction,ids=ids,time=now,values=row,visibility_events=events,sounds=m.sounds,explosions=m.explosions,fnv1a32=hex(h))

if __name__=='__main__':
 rows=[trace(t,s,d) for t in range(1,11) for s,d in ((0,1),(15,1),(13 if t==10 else 11-t,1 if t==10 or t==9 else t if t<=4 else t-4))]
 p.args.out.write_text(json.dumps(dict(status='Original callback execution; not native validation',traces=rows),indent=2))
 print('Original comet motion:',len(rows),'traces PASS')
