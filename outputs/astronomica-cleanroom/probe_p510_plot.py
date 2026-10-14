"""Inventory original plot custom23 and its movie/script dependencies."""
import json,struct,hashlib,re
import probe_p526_motion as p
import probe_comet_state as setup
from astro_reader import parse,FormatError
symbols=json.loads((p.Path(__file__).parent/'evidence/debug/symbols.json').read_text())
base=p.base(4);table=0x72a0
dispatch={struct.unpack_from('<I',p.exe,base+table+4*i)[0]:struct.unpack_from('<H',p.exe,base+table+124+2*i)[0] for i in range(31)}
start=dispatch[23];end=dispatch[24];assert start<end
raw=(p.args.root/'PLACES/P510/MEGAFILE.HYP').read_bytes()
try:scene=parse(raw)
except FormatError as e:
 match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e));assert match,e
 scene=parse(raw[:int(match[2],16)])
def commands(obj):
 if isinstance(obj,dict):
  if 'opcode' in obj:yield obj
  else:
   for v in obj.values():yield from commands(v)
 elif isinstance(obj,list):
  for v in obj:yield from commands(v)
relevant=[c for c in commands(scene) if c['opcode'] in (4,23,36,37)]
decoded={i.address:i for i in p.md.disasm(p.exe[base+start:base+end],start)}
ins=[f'{i.address:04x}: {i.mnemonic} {i.op_str}' for i in decoded.values()]
modes={struct.unpack_from('<I',p.exe,base+0x6d9c+4*i)[0]:struct.unpack_from('<H',p.exe,base+0x6da8+2*i)[0] for i in range(3)}
rows=[]
for mode,entry in modes.items():
 m=setup.machine(0,0,0,0);m.reg={'ebp':0x9000,'esp':0x8d00};pc=entry;calls=[]
 m.write(0x1368,0x6000);m.write(0xb64,0x6100)
 for _ in range(100):
  if pc==0x528b:break
  i=decoded[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o]
  if i.mnemonic=='push':m.push(v[0],o[0].size)
  elif i.mnemonic=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif i.mnemonic=='add':m.put(i,o[0],v[0]+v[1])
  elif i.mnemonic=='jmp':pc=v[0]
  elif i.mnemonic=='lcall':
   sp=m.getreg('sp');name=setup.relocs[i.address+1]
   if name=='_SWMoveSprite':
    x=p.signed(m.read(sp+4,2),2);y=p.signed(m.read(sp+6,2),2);m.locate(m.read(sp),x,y);calls.append(dict(name=name,xy=[x,y]))
   elif name=='_SetMovieActiveSegment':calls.append(dict(name=name,start=m.read(sp+4),duration=m.read(sp+8)))
   elif name=='_CallMeWhen':calls.append(dict(name=name,user_data=m.read(sp+8),flags=m.read(sp+12),time=m.read(sp+16),time_scale=m.read(sp+20),callback=setup.relocs.get(0x527a)))
   else:raise AssertionError(name)
  else:raise AssertionError((hex(i.address),i.mnemonic))
 else:raise AssertionError('custom23 did not return')
 rows.append(dict(mode=mode,entry=hex(entry),calls=calls))
p.args.out.write_text(json.dumps(dict(status='Original research only; P510 not enabled',custom23_entry=hex(start),custom23_end=hex(end),
 custom23_sha256=hashlib.sha256(p.exe[base+start:base+end]).hexdigest(),resource_sha256=hashlib.sha256(raw).hexdigest(),
 movies=scene['movies'],conditions=scene['conditions'],commands=relevant,modes=rows,instructions=ins),indent=2))
print('Original P510 custom23:',hex(start),hex(end),len(ins),'instructions; movies',scene['movies'])
print(json.dumps(rows,indent=2))
