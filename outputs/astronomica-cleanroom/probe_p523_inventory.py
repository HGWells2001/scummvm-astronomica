"""Inventory original P523 resources and custom dispatch without enabling it."""
import json,struct,re,hashlib
import probe_p526_motion as p
from astro_reader import parse,FormatError

raw=(p.args.root/'PLACES/P523/MEGAFILE.HYP').read_bytes()
try:scene=parse(raw)
except FormatError as e:
 match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e));assert match,e
 scene=parse(raw[:int(match[2],16)])
code=p.exe[p.base(4):p.base(4)+0x8f7e]
dispatch={struct.unpack_from('<I',code,0x72a0+4*i)[0]:struct.unpack_from('<H',code,0x731c+2*i)[0] for i in range(31)}
def walk(x,path='scene'):
 if isinstance(x,dict):
  if 'opcode' in x:yield path,x
  else:
   for k,v in x.items():yield from walk(v,path+'/'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,path+'/'+str(i))
commands=[dict(path=path,**c) for path,c in walk(scene) if c['opcode'] in (3,4,23,36,37)]
customs=sorted({c['args'][0] for c in commands if c['opcode']==23})
ops=[]
for custom in customs:
 start=dispatch[custom];end=min(v for v in dispatch.values() if v>start)
 instructions=[dict(address=hex(i.address),mnemonic=i.mnemonic,operands=i.op_str) for i in p.md.disasm(code[start:end],start)]
 ops.append(dict(custom=custom,start=hex(start),end=hex(end),instructions=instructions,sha256=hashlib.sha256(code[start:end]).hexdigest()))
out=dict(status='Original resource and disassembly inventory only; P523 not enabled',
 resource_sha256=hashlib.sha256(raw).hexdigest(),movies=scene['movies'],conditions=scene['conditions'],
 layers=scene['layers'],sprites=len(scene['sprites']),commands=commands,operations=ops,
 visibility_helpers=dict(segment=3,show='0x0000-0x002c',hide='0x002c-0x0058',hide_em='0x0058-0x009e',
 hide_em_sprite_ids=list(range(9,38)),sha256=hashlib.sha256(p.exe[p.base(3):p.base(3)+0x9e]).hexdigest()),
 button_dispatch={struct.unpack_from('<I',code,0x727c+4*i)[0]:hex(struct.unpack_from('<H',code,0x7294+2*i)[0]) for i in range(6)})
p.args.out.write_text(json.dumps(out,indent=2))
print('P523:',len(scene['sprites']),'sprites; movies',scene['movies'])
print('Custom operations:',[(o['custom'],o['start'],o['end'],len(o['instructions'])) for o in ops])
print('Commands:',commands)
