"""Inventory original exploration scripts and custom26; no playability inference."""
import json,re,struct,hashlib
import probe_p526_motion as p
from astro_reader import parse,FormatError
code=p.exe[p.base(4):p.base(4)+0x8000]
def table(address,count):
 rows=[]
 for i in range(count):
  key=struct.unpack_from('<I',code,address+4*i)[0]
  target=struct.unpack_from('<H',code,address+4*i+2*(count-i)+2*count)[0]
  rows.append(dict(key=key,target=hex(target)))
 return rows
rows=[];invalid=[]
for path in sorted(p.Path('D:/astro/PLACES').glob('P*/MEGAFILE.HYP'),key=lambda q:int(q.parent.name[1:])):
 data=path.read_bytes()
 try:scene=parse(data)
 except FormatError as error:
  match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(error))
  if not match:invalid.append(dict(place=path.parent.name,error=str(error)));continue
  scene=parse(data[:int(match[2],16)])
 def walk(obj):
  if isinstance(obj,dict):
   if 'opcode' in obj:yield obj
   else:
    for value in obj.values():yield from walk(value)
  elif isinstance(obj,list):
   for value in obj:yield from walk(value)
 custom=[c for c in walk(scene) if c['opcode']==23 and c['args'][0]==26]
 if custom or int(path.parent.name[1:]) in (197,425,426,427,428,429,432):
  rows.append(dict(place=path.parent.name,sha256=hashlib.sha256(data).hexdigest(),
   mode=scene['mode'],movies=scene['movies'],custom26=custom,entry_scripts=scene['scripts'],mouse_rects=scene['mouse_rects']))
output=dict(status='Original inventory only; custom26 remains unimplemented',rows=rows,invalid=invalid,
 custom26=dict(address='4:5a91-6310',sha256=hashlib.sha256(code[0x5a91:0x6310]).hexdigest(),
 modes=table(0x6c88,2),reads=table(0x6c34,14),writes=table(0x6b56,10),
 disassembly=[f'{i.address:04x} {i.mnemonic} {i.op_str}' for i in p.md.disasm(code[0x5a91:0x6310],0x5a91)]))
p.args.out.write_text(json.dumps(output,indent=2));print('Original progression inventory:',len(rows),'scenes;',len(invalid),'invalid resource')
