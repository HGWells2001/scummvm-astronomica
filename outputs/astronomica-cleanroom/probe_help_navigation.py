"""Check original help context and keyword B-trees against decoded title references."""
import argparse,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
d=(a.root/'HELP/ASTRONOM.HLP').read_bytes();directory=json.loads((a.out.parent/'help-directory.json').read_text())
assert hashlib.sha256(d).hexdigest()==directory['source_sha256']
def stream(name):
 info=directory['streams'][name];return d[info['offset']+9:info['offset']+9+info['used']]
def leaf_rows(name,fmt):
 b=stream(name);assert b[6:22].split(b'\0')[0]==fmt
 size=struct.unpack_from('<H',b,4)[0];pages=struct.unpack_from('<H',b,30)[0];total=struct.unpack_from('<I',b,34)[0]
 assert len(b)==38+pages*size
 page=0;previous=65535;seen=set();rows=[]
 while page!=65535:
  assert page<pages and page not in seen;seen.add(page);start=38+page*size
  unused,count,prev,next_page=struct.unpack_from('<4H',b,start);assert prev==previous;cursor=start+8
  for _ in range(count):
   if fmt==b'L4':
    key,value=struct.unpack_from('<II',b,cursor);cursor+=8;rows.append(dict(context_hash=key,reference=value))
   else:
    end=b.index(0,cursor,start+size);key=b[cursor:end].decode('cp1252');cursor=end+1
    n,offset=struct.unpack_from('<HI',b,cursor);cursor+=6;data=stream('|KWDATA');assert offset+4*n<=len(data)
    refs=struct.unpack_from(f'<{n}I',data,offset);rows.append(dict(keyword=key,references=refs))
  assert cursor+unused==start+size
  previous,page=page,next_page
 assert len(rows)==total
 return rows
contexts=leaf_rows('|CONTEXT',b'L4');keywords=leaf_rows('|KWBTREE',b'i24')
titles={r['topic_reference']:r['title'] for r in directory['titles']}
decoded=json.loads((a.out.parent/'help-compression.json').read_text())
assert decoded['source_sha256']==directory['source_sha256']
# Context and keyword references address character positions inside topics,
# usually title+3, rather than always naming a topic header.
spans=[];block=-1;characters=0;title=''
for record in decoded['records']:
 current=record['address']>>14
 if current!=block:block=current;characters=0
 if record['kind']==2:title=record['text'];continue
 size=record['expanded']+len(record['inline_bitmap_ids'])
 spans.append(((block<<15)+characters,(block<<15)+characters+size,title))
 characters+=size

def resolve(reference):
 matches=[title for start,end,title in spans if start<=reference<end]
 assert len(matches)==1,(hex(reference),matches)
 return matches[0]
assert len({r['context_hash'] for r in contexts})==len(contexts)
for r in contexts:r['title']=resolve(r['reference'])
for r in keywords:r['titles']=[resolve(v) for v in r['references']]
out=dict(status='Original index navigation verified; inline hyperlink bytecode and native UI still pending',source_sha256=hashlib.sha256(d).hexdigest(),contexts=contexts,keywords=keywords,
 context_count=len(contexts),keyword_count=len(keywords),keyword_references=sum(len(r['references']) for r in keywords))
a.out.write_text(json.dumps(out,indent=2));print('Help navigation:',out['context_count'],'contexts',out['keyword_count'],'keywords',out['keyword_references'],'references PASS')
