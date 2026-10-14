"""Inventory the original help container; no rendering or text decompression.

The directory and title leaf layouts are checked against every entry and
page boundary in this file. No guessed topic decoding is reported as content.
"""
import argparse,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
p=a.root/'HELP/ASTRONOM.HLP';d=p.read_bytes()
magic,directory,free,size=struct.unpack_from('<4I',d)
assert magic==0x35f3f and free==0xffffffff and size==len(d)
def stream(offset):
 allocated,used,flags=struct.unpack_from('<IIB',d,offset)
 assert allocated>=9+used and offset+allocated<=len(d)
 return dict(offset=offset,allocated=allocated,used=used,flags=flags),d[offset+9:offset+9+used]
def leaves(b,fmt):
 assert len(b)>=38 and struct.unpack_from('<H',b)[0]==0x293b
 page_size=struct.unpack_from('<H',b,4)[0]
 assert b[6:22].split(b'\0')[0]==fmt
 root,pages,levels=struct.unpack_from('<HHH',b,26)[0],struct.unpack_from('<H',b,30)[0],struct.unpack_from('<H',b,32)[0]
 total=struct.unpack_from('<I',b,34)[0]
 assert len(b)==38+pages*page_size and root<pages
 page=0;previous=0xffff;seen=set();rows=[]
 while page!=0xffff:
  assert page<pages and page not in seen;seen.add(page)
  start=38+page*page_size;unused,count,prev,next_page=struct.unpack_from('<4H',b,start)
  assert prev==previous
  cursor=start+8
  for _ in range(count):
   if fmt==b'Lz':key=struct.unpack_from('<I',b,cursor)[0];cursor+=4
   end=b.index(0,cursor,start+page_size);name=b[cursor:end].decode('cp1252');cursor=end+1
   if fmt==b'z4':key=struct.unpack_from('<I',b,cursor)[0];cursor+=4
   rows.append((name,key))
  assert cursor+unused==start+page_size
  previous,page=page,next_page
 assert len(rows)==total
 return rows,dict(page_size=page_size,root_page=root,pages=pages,levels=levels,leaf_pages=len(seen),entries=total)
info,raw=stream(directory);entries,tree=leaves(raw,b'z4')
assert len(dict(entries))==len(entries)==41
streams={};ranges=[(directory,directory+info['allocated'])]
for name,offset in entries:
 info,raw=stream(offset);info['sha256']=hashlib.sha256(raw).hexdigest();streams[name]=info
 ranges.append((offset,offset+info['allocated']))
ranges.sort();assert ranges[0][0]==16 and ranges[-1][1]==len(d)
assert all(left[1]==right[0] for left,right in zip(ranges,ranges[1:]))
_,raw=stream(streams['|TTLBTREE']['offset']);titles,title_tree=leaves(raw,b'Lz')
assert len(titles)==782 and len([n for n in streams if n.startswith('|bm')])==31
_,raw=stream(streams['|SYSTEM']['offset'])
assert struct.unpack_from('<H',raw)[0]==0x36c
minor,major=struct.unpack_from('<HH',raw,2);flags=struct.unpack_from('<H',raw,10)[0];cursor=12;records=[]
while cursor<len(raw):
 kind,length=struct.unpack_from('<HH',raw,cursor);cursor+=4
 payload=raw[cursor:cursor+length];assert len(payload)==length;cursor+=length
 records.append(dict(type=kind,bytes=length,hex=payload.hex(),text=payload.rstrip(b'\0').decode('cp1252') if kind in (1,2,4) else None))
assert cursor==len(raw)
out=dict(status='Original container inventory only; topic body decoding and native help UI remain pending',
 source_sha256=hashlib.sha256(d).hexdigest(),size=len(d),directory=tree,streams=streams,
 title_tree=title_tree,titles=[dict(title=name,topic_reference=key) for name,key in titles],
 system=dict(minor=minor,major=major,flags=flags,records=records),
 coverage='All41 directory entries, all782 title entries,31 bitmap streams; all allocated extents cover the file exactly')
a.out.write_text(json.dumps(out,indent=2));print('Original help container:41 streams,782 title entries,31 bitmap streams; extent checks PASS')
