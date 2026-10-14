"""Execute original P510 movie callbacks, keeping CS tables separate from DS.

External QuickTime/SpriteWorld calls are recorded, not emulated as movie playback.
The branch decisions and their arguments come from original x86 instructions.
"""
import json, struct, hashlib
import probe_p526_motion as p
import probe_comet_state as setup

code = p.exe[p.base(4):p.base(4)+0x8f7e]
ins = {i.address:i for i in p.md.disasm(code[0x735a:0x8d02],0x735a)}
dispatch = {struct.unpack_from('<I',code,0x8e6a+4*i)[0]:
            struct.unpack_from('<H',code,0x8f22+2*i)[0] for i in range(46)}

class Machine(p.Machine):
 def value(self, i, o):
  if o.type == p.X86_OP_MEM and i.reg_name(o.mem.segment) == 'cs':
   a=self.address(i,o)
   return int.from_bytes(code[a:a+o.size],'little')
  return super().value(i,o)

def run(event, choice, solved=0):
 m=Machine();m.reg={'ebp':0x9000,'esp':0x8d00}
 m.write(0xc88,0x1000);m.write(0x1028,0x2200);m.write(0x1368,0x6000)
 m.write(0x1408,choice);m.write(0xb64,0x6100)
 m.write(0x7a8,0x7000);m.write(0x7072,solved);m.write(0xc8c,510)
 m.write(0x900a,event);m.write(0xb40,1,2);m.write(0xb42,1,2)
 pc=dispatch[event];compare=0;calls=[];trace=[]
 for _ in range(500):
  if pc==0x8cfb:
   return dict(event=event,choice=choice,previously_solved=solved,calls=calls,
    solved=m.read(0x7072),place=m.read(0xc8c),change_place=m.read(0xc98,2),
    flags=[m.read(0xb40,2),m.read(0xb42,2)],trace=trace)
  i=ins[pc];trace.append(hex(pc));pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='loop':
   m.setreg('cx',m.getreg('cx')-1)
   if m.getreg('cx'):pc=v[0]
  elif op in ('jmp','je','jne','jl','jg'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jl':compare<0,'jg':compare>0}[op]:pc=v[0]
  elif op=='lcall':
   sp=m.getreg('sp');name=setup.relocs[i.address+1];call=dict(name=name)
   if name=='_SWMoveSprite':
    assert m.read(sp)==0x2200
    call['xy']=[p.signed(m.read(sp+4,2),2),p.signed(m.read(sp+6,2),2)]
   elif name=='_SetMovieActiveSegment':
    assert m.read(sp)==0x6000
    call.update(start=m.read(sp+4),duration=m.read(sp+8))
   elif name=='_CallMeWhen':
    assert m.read(sp)==0x6100
    call.update(event=m.read(sp+8),flags=m.read(sp+12),time=m.read(sp+16),scale=m.read(sp+20))
   elif name=='_StartMovie':assert m.read(sp)==0x6000
   elif name!='_puzzle_successful':raise AssertionError(name)
   calls.append(call)
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('callback did not return')

if __name__=='__main__':
 events=[e for e in dispatch if e>=20]
 rows=[run(e,c,s) for e in events for c in range(-1,7) for s in (0,1)]
 assert all(r['flags']==[0,0] for r in rows)
 p.args.out.write_text(json.dumps(dict(status='Original instruction evidence, not movie playback validation',
  code_sha256=hashlib.sha256(code).hexdigest(),dispatch={e:hex(dispatch[e]) for e in events},cases=len(rows),rows=rows),indent=2))
 print('P510 callbacks:',len(events),'events,',len(rows),'original cases PASS')
 print('Dispatch events:', events)
