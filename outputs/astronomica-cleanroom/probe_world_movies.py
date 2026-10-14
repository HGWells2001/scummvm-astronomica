"""Fresh original resource inventory and opcode50/path relocation evidence."""
from pathlib import Path
import sys,json,struct,hashlib,re
import probe_p526_motion as p
from astro_reader import parse,FormatError
root=p.args.root;rows=[];errors=[]
for folder in sorted((root/'PLACES').glob('P*'),key=lambda x:int(x.name[1:])):
 f=folder/'MEGAFILE.HYP'
 if not f.exists() or int(folder.name[1:])>=500:continue
 try:s=parse(f.read_bytes())
 except FormatError as e:
  match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e))
  if not match:errors.append(dict(place=folder.name,error=str(e)));continue
  s=parse(f.read_bytes()[:int(match[2],16)])
 if s['movies']:
  rows.append(dict(place=int(folder.name[1:]),mode=s['mode'],layers=s['layers'],sprites=len(s['sprites']),movies=s['movies'],entry=s['scripts'],files={m:(folder/m).exists() for m in s['movies']},resource_sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
names={(s['segment'],s['offset']):s['name'] for s in json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())}
seg=15;size=struct.unpack_from('<H',p.exe,p.table+(seg-1)*8+2)[0];calls={}
for j in range(struct.unpack_from('<H',p.exe,p.base(seg)+size)[0]):
 typ,flags,src,t1,t2=struct.unpack_from('<BBHHH',p.exe,p.base(seg)+size+2+8*j);seen=set()
 while src!=65535 and src not in seen and src+2<=size:
  seen.add(src)
  if 0x721<=src<0x80e:calls[hex(src)]=dict(name=names.get((t1,t2)),target=[t1,t2],flags=flags)
  if flags&4:break
  src=struct.unpack_from('<H',p.exe,p.base(seg)+src)[0]
redirect=p.exe[p.base(20)+0x3c0:p.base(20)+0x3ce];assert redirect==b'%s/PLACES/P2/\0'
palettes={}
for name in ('BLACK_B','OPEN1_B','OPEN2_B'):
 b=(root/'PLACES/P2'/name).read_bytes();assert b[:2]==b'BM'
 offset=struct.unpack_from('<I',b,10)[0]
 palettes[name]=dict(sha256=hashlib.sha256(b).hexdigest(),dimensions=struct.unpack_from('<ii',b,18),pixel_indices=sorted(set(b[offset:])),palette_sha256=hashlib.sha256(b[54:1078]).hexdigest())
p.args.out.write_text(json.dumps(dict(status='Original resource and instruction research only',rows=rows,parse_errors=errors,opcode50_region='15:0721-080e',opcode50_calls=calls,p4_redirect=redirect[:-1].decode(),p4_code_sha256=hashlib.sha256(p.exe[p.base(9)+0x2612:p.base(9)+0x2630]).hexdigest(),opcode50_sha256=hashlib.sha256(p.exe[p.base(15)+0x721:p.base(15)+0x80e]).hexdigest(),intro_palettes=palettes),indent=2))
print('World movies:',len(rows),'scenes;',len(errors),'parse errors; original redirect and palette call records saved')
