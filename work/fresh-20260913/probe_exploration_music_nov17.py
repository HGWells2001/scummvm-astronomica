"""Bounded execution of the original exploration music selector; no Win16 program execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,struct,sys,wave
w=Path(__file__).resolve().parent;sys.path.insert(0,str(w/'deps-verified'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
from capstone.x86_const import X86_OP_MEM,X86_OP_IMM
root=Path('D:/astro');exe=(root/'SETUP/ASTRO.EXE').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(exe)=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
ne=struct.unpack_from('<I',exe,0x3c)[0];table=ne+struct.unpack_from('<H',exe,ne+0x22)[0];shift=struct.unpack_from('<H',exe,ne+0x32)[0];base=struct.unpack_from('<H',exe,table+8*8)[0]<<shift
md=Cs(CS_ARCH_X86,CS_MODE_16);md.detail=True;ins={i.address:i for i in md.disasm(exe[base+0x154d:base+0x1714],0x154d)}
assert ins[0x1647].op_str=='dword ptr [0x1bb], 0x38c'and ins[0x163e].op_str=='dword ptr es:[bx + 0xfa], 1'
assert [ins[a].operands[0].imm for a in(0x15f1,0x1608,0x161f)]==[0x3d04]*3
def original(place,mode,g60,prior):
 pc=0x154d;loop=prior;stops=0;cmp=0
 for step in range(120):
  if pc==0x1714:return loop,stops
  if pc==0x15d6:pc=0x163a;continue # three modeled four-byte NAV reads,not audio/scalar writes
  i=ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands
  def value(t):
   if t.type==X86_OP_IMM:return t.imm
   assert t.type==X86_OP_MEM
   if i.reg_name(t.mem.base)=='bp':assert t.mem.disp==-0x24;return mode
   if i.reg_name(t.mem.segment)=='es':assert t.mem.disp==0xfa;return g60
   assert t.mem.disp in(0xc8c,0x1bb);return place if t.mem.disp==0xc8c else loop
  if op=='cmp':cmp=value(o[0])-value(o[1])
  elif op in('je','jne','jl','jle','jmp'):
   if op=='jmp'or{'je':cmp==0,'jne':cmp!=0,'jl':cmp<0,'jle':cmp<=0}.get(op,False):pc=o[0].imm
  elif op=='mov':
   assert o[0].type==X86_OP_MEM and o[1].type==X86_OP_IMM
   if o[0].mem.disp==0x1bb:loop=o[1].imm
   else:assert o[0].mem.disp in(0xc9a,0xc9e)
  elif op=='call':assert o[0].imm==0x3abe;stops+=1
  else:assert op in('nop','push','add','les'),(hex(i.address),op)
 raise AssertionError('selector did not terminate')
def expected(place,mode,g60,old):
 loop=old;stops=0
 if mode==0:loop=901 if place==1 else 902 if place==422 else 0;stops+=1
 if mode==3 or place==402:loop=900;stops+=1
 if mode==1:
  chosen=908 if g60==1 else 901 if 219<=place<=251 or place in(410,1)else 903 if 361<=place<=389 or place==420 else 902
  stops+=loop!=chosen;loop=chosen
 return loop,stops
count=0;h=hashlib.sha256()
for place in range(538):
 for mode in(0,1,3):
  for g60 in(-1,0,1,2):
   for old in(-1,0,900,901,902,903,908):
    result=original(place,mode,g60,old);assert result==expected(place,mode,g60,old),(place,mode,g60,old,result)
    h.update(struct.pack('<6i',place,mode,g60,old,*result));count+=1
audio={}
for id in(901,902,903,908):
 p=root/'SOUNDS'/('S%d.WAV'%(id-900))
 with wave.open(str(p))as f:audio[str(id)]=dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes()),rate=f.getframerate(),channels=f.getnchannels(),frames=f.getnframes())
proof=dict(status='ORIGINAL_EXPLORATION_MUSIC_SELECTOR_PASS',at=datetime.now(timezone.utc).isoformat(),original_exe_sha256=sha(exe),selector_bytes_sha256=sha(exe[base+0x154d:base+0x1714]),cases=count,aggregate=h.hexdigest(),global60_offset=10+4*60,shared_audio=audio,limits=['Bounded original selector instructions with stop-sound calls recorded and NAV reads modeled','Global60 interpretation uses the accepted current-cleanroom scalar object layout:10-byte header plus100DWORD values','Not original Windows runtime playback; original bytes and disassembly remain local','Production change targets mode1 exploration; mode0/mode3 behavior is separately scoped'])
(w/'exploration-music-original-nov17.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'],count)
