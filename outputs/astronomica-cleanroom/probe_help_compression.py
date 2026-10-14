"""Validate inferred compression against the original help container's sizes.

This is file-format research, not a help viewer or an original-code execution
comparison. LZ references are bounded; phrase output is checked against lengths.
"""
import argparse,hashlib,json,struct,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
d=(a.root/'HELP/ASTRONOM.HLP').read_bytes()
def stream(offset):
 size=struct.unpack_from('<I',d,offset+4)[0];return d[offset+9:offset+9+size]
def lz(c):
 out=bytearray();pos=0
 while pos<len(c):
  bits=c[pos];pos+=1
  for bit in range(8):
   if pos>=len(c):break
   if bits&(1<<bit):
    assert pos+2<=len(c)
    word=struct.unpack_from('<H',c,pos)[0];pos+=2;distance=(word&4095)+1;count=(word>>12)+3
    assert distance<=len(out)
    for _ in range(count):out.append(out[-distance])
   else:out.append(c[pos]);pos+=1
   assert len(out)<=65536
 return bytes(out)
b=stream(16);n,tag,size=struct.unpack_from('<HHI',b);assert tag==256
offsets=struct.unpack_from(f'<{n+1}H',b,8);assert offsets[0]==2*(n+1)
text=lz(b[8+offsets[0]:]);assert len(text)==size==offsets[-1]-offsets[0]
phrases=[text[offsets[i]-offsets[0]:offsets[i+1]-offsets[0]] for i in range(n)]
def expand(raw):
 out=bytearray();i=0
 while i<len(raw):
  ch=raw[i];i+=1
  if 1<=ch<=15:
   assert i<len(raw)
   token=(ch-1)*256+raw[i];i+=1;index=token>>1
   assert index<len(phrases);out.extend(phrases[index])
   if token&1:out.append(32)
  else:out.append(ch)
 return bytes(out)
topic=stream(0x307d);blocks=[];headers=[]
for offset in range(0,len(topic),4096):
 block=topic[offset:offset+4096];assert len(block)>=12
 headers.append(struct.unpack_from('<III',block));blocks.append(lz(block[12:]))
def read(address,size):
 index=address>>14;offset=(address&16383)-12;result=bytearray()
 assert index<len(blocks) and 0<=offset<len(blocks[index])
 while size:
  count=min(size,len(blocks[index])-offset);assert count>0
  result.extend(blocks[index][offset:offset+count]);size-=count;index+=1;offset=0
 return bytes(result)
address=12;previous=0xffffffff;records=[];seen=set();text_records=0
while address!=0xffffffff:
 assert address not in seen;seen.add(address)
 size,expanded,prev,next_address,text_offset,kind=struct.unpack('<5IB',read(address,21))
 assert prev==previous and size>=21 and 21<=text_offset<=size
 raw=read(address,size);body=expand(raw[text_offset:])
 assert len(body)==expanded,(hex(address),kind,len(body),expanded)
 records.append(dict(address=address,kind=kind,stored=size,expanded=len(body),format_hex=raw[21:text_offset].hex(),text_sha256=hashlib.sha256(body).hexdigest(),text=body.decode('cp1252')))
 text_records+=bool(body);previous,address=address,next_address
 assert len(records)<10000
directory=json.loads((a.out.parent/'help-directory.json').read_text())
assert directory['source_sha256']==hashlib.sha256(d).hexdigest()
heads=[r for r in records if r['kind']==2]
assert [r['text'] for r in heads]==[r['title'] for r in directory['titles']]
# Title references count expanded body characters plus one unit per embedded
# bitmap, with a32768-unit base for each16384-address topic block.
index=0;block=-1;characters=0;bitmap_ids=[]
for record in records:
 current=record['address']>>14
 if current!=block:block=current;characters=0
 if record['kind']==2:
  reference=(block<<15)+characters
  assert reference==directory['titles'][index]['topic_reference']
  record['topic_reference']=reference;index+=1
 else:
  pattern=bytes.fromhex('86220880020000')+b'(..)'
  ids=[int.from_bytes(m[1],'little') for m in re.finditer(pattern,bytes.fromhex(record['format_hex']),re.S)]
  record['inline_bitmap_ids']=ids;bitmap_ids.extend(ids);characters+=record['expanded']+len(ids)
assert bitmap_ids==list(range(31))
out=dict(topic_reference_matches=index,inline_bitmap_ids=bitmap_ids,title_index_matches=len(heads),status='Inferred decoding validated against original stored lengths and record links; native help UI not implemented',
 source_sha256=hashlib.sha256(d).hexdigest(),phrase_count=n,phrase_bytes=len(text),phrase_sha256=hashlib.sha256(text).hexdigest(),
 topic_blocks=len(blocks),block_sizes=[len(b) for b in blocks],block_sha256=[hashlib.sha256(b).hexdigest() for b in blocks],
 records=records,text_records=text_records,scope='LZ and phrase decoding, linked record traversal; formatting and clickable links remain undecoded')
a.out.write_text(json.dumps(out,indent=2));print('Help compression:',n,'phrases',len(blocks),'blocks',len(records),'records',text_records,'text records PASS')
