# Independent original-file format inventory. No engine imports or generated UI.
import argparse,collections,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
source=(a.root/'HELP/ASTRONOM.HLP').read_bytes();digest=hashlib.sha256(source).hexdigest()
directory=json.loads((a.out.parent/'help-directory.json').read_text());decoded=json.loads((a.out.parent/'help-compression.json').read_text());assert digest==directory['source_sha256']==decoded['source_sha256']
class R:
 def __init__(self,b):self.b=b;self.p=0
 def get(self,n):
  assert self.p+n<=len(self.b);v=int.from_bytes(self.b[self.p:self.p+n],'little');self.p+=n;return v
 def packed(self,small=False,signed=False):
  n=1 if small else 2;p=self.p;v=self.get(n)
  if v&1:self.p=p;n*=2;v=self.get(n)
  return (v>>1)-(1<<(8*n-2) if signed else 0)
ops=collections.Counter();fonts=collections.Counter();heads=collections.Counter()
def paragraph(r):
 text_offset=r.packed(signed=True);style=r.get(2);assert style==0
 flags=r.get(2);assert flags&~0xa04==0,(hex(flags),r.p)
 indent=r.packed(small=True,signed=True) if flags&4 else 0
 tabs=[]
 if flags&0x200:
  for _ in range(r.packed(small=True,signed=True)):
   position=r.packed(small=True);alignment=r.get(1) if position&0x4000 else 0
   tabs.append(dict(position=position&0x3fff,alignment=alignment))
 commands=[]
 while r.p<len(r.b):
  op=r.get(1);cmd={'opcode':op};ops[op]+=1
  if op==0x80:cmd['font']=r.get(2);fonts[cmd['font']]+=1
  elif op==0x86:
   assert r.b[r.p:r.p+6]==bytes.fromhex('220880020000');r.p+=6;cmd['image']=r.get(2)
  else:assert op in (0x81,0x82,0x83,255),hex(op)
  commands.append(cmd)
  if op==255:break
 assert commands[-1]['opcode']==255
 heads[flags]+=1
 return dict(text_offset=text_offset,flags=flags,indent=indent,tabs=tabs,commands=commands)
rows=[]
for rec in decoded['records']:
 if rec['kind']==2:continue
 b=bytes.fromhex(rec['format_hex']);r=R(b);length=r.packed(signed=True);characters=r.packed(small=True)
 assert length==len(b)-r.p and characters==len(rec['text'])+len(rec['inline_bitmap_ids'])
 row=dict(address=rec['address'],kind=rec['kind'])
 if rec['kind']==32:
  para=paragraph(r);assert para['text_offset']==0
  row['paragraphs']=[para]
 else:
  assert rec['kind']==35
  count=r.get(1);table_type=r.get(1);assert table_type==1 and 1<=count<=8
  row['columns']=[dict(width=r.get(2),gap=r.get(2)) for _ in range(count)]
  paras=[]
  while True:
   column=r.get(2)
   if column==65535:break
   assert column<count
   cell_type=r.get(1);assert cell_type==1
   size=r.packed(signed=True);stop=r.p+size
   para=paragraph(r);assert r.p==stop,(rec['address'],r.p,stop)
   para['column']=column;paras.append(para)
  row['paragraphs']=paras
 assert r.p==len(b)
 cursor=0;image_ids=[]
 for para in row['paragraphs']:
  assert para['text_offset']==cursor,(rec['address'],para['text_offset'],cursor)
  for cmd in para['commands']:
   end=rec['text'].index('\0',cursor);cmd['text']=rec['text'][cursor:end];cursor=end+1
   if cmd['opcode']==0x86:image_ids.append(cmd['image'])
 assert cursor==len(rec['text']) and image_ids==rec['inline_bitmap_ids']
 rows.append(row)
f=directory['streams']['|FONT'];b=source[f['offset']+9:f['offset']+9+f['used']];names,count,name_offset,font_offset=struct.unpack_from('<4H',b);assert (names,count,name_offset,font_offset)==(93,16,8,1868) and len(b)==font_offset+11*count
styles=[]
for i in range(count):
 v=b[font_offset+11*i:font_offset+11*(i+1)];name_index=int.from_bytes(v[3:5],'little');assert name_index<names
 name=b[name_offset+20*name_index:name_offset+20*(name_index+1)].split(b'\0')[0].decode('cp1252')
 styles.append(dict(index=i,flags=v[0],half_points=v[1],family=v[2],name=name,foreground=list(v[5:8]),background=list(v[8:11])))
assert set(fonts)<=set(range(count))
a.out.write_text(json.dumps(dict(source_sha256=digest,scope='All1335 body records:1031 kind32 paragraphs and304 kind35 table rows',record_count=len(rows),opcodes=dict(ops),font_uses=dict(fonts),paragraph_flags=dict(heads),styles=styles,records=rows,
 findings=['Format length matches remaining record bytes after the two packed length fields.',
 'Character count equals expanded body length plus one unit per image.',
 'Every NUL pairs with exactly one command; all31 bitmap commands match prior independent associations.',
 'Only font change80,81,82,83,image86 and endFF occur in all body records. No hyperlink opcode occurs in this HLP.',
 'Flags and font data are preserved as raw values. Pixel-exact typography is not claimed.']),indent=2))
print('Original help format:',len(rows),'body records,',sum(ops.values()),'NUL/command matches,16 font descriptions PASS')

# Independent semantic reference, serialized as little-endian words plus raw text.
j=json.loads(a.out.read_text());h=2166136261

def raw(b):
 global h
 for c in b:h=((h^c)*16777619)&0xffffffff

def word(x):raw((x&0xffffffff).to_bytes(4,'little'))
for rec in j['records']:
 word(rec['kind']);word(len(rec.get('columns',[])))
 for col in rec.get('columns',[]):word(col['width']);word(col['gap'])
 for p in rec['paragraphs']:
  if rec['kind']==35:word(p['column'])
  word(p['text_offset']);word(p['flags']);word(p['indent']);word(len(p['tabs']))
  for t in p['tabs']:word(t['position']);word(t['alignment'])
  cursor=p['text_offset']
  for c in p['commands']:
   b=c['text'].encode('cp1252');word(c['opcode']);word(cursor);word(len(b));raw(b);cursor+=len(b)+1
   if c['opcode']==0x80:word(c['font'])
   if c['opcode']==0x86:word(c['image'])
 if rec['kind']==35:word(65535)
j['semantic_hash_fnv32']=f'{h:08x}';a.out.write_text(json.dumps(j,indent=2));print('Semantic hash',hex(h))

