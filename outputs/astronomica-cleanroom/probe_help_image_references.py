"""Independent palette/pixel and article-association references from original HLP."""
from pathlib import Path
import argparse,json,runpy,sys
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sys.argv=['probe',str(a.root),'--out',str(a.out.parent/'help-bitmaps.json')]
r=runpy.run_path(str(Path(__file__).with_name('probe_help_bitmaps.py'))); src=r['d']; directory=r['directory']; rows=[]
def fnv(b):
 h=2166136261
 for c in b:h=((h^c)*16777619)&0xffffffff
 return h
decoded=json.loads((a.out.parent/'help-compression.json').read_text());assert decoded['source_sha256']==directory['source_sha256']
article=-1;maps=[]
for record in decoded['records']:
 if record['kind']==2:article+=1;title=record['text']
 for image in record.get('inline_bitmap_ids',[]):maps.append(dict(image=image,article=article,title=title,record=record['address']))
for m in maps:
 i=m['image'];info=directory['streams'][f'|bm{i}'];b=src[info['offset']+9:info['offset']+9+info['used']];q=r['Reader'](b)
 vals=[q.packed(),q.packed(),q.packed(True),q.packed(True)]+[q.packed() for _ in range(6)]
 offset=int.from_bytes(b[q.pos:q.pos+4],'little');q.pos+=8;palette=b[q.pos:q.pos+1024];stored=b[8+offset:];pixels=r['lz'](stored) if b[9]==2 else stored
 rows.append(dict(image=i,article=m['article'],width=vals[4],height=vals[5],palette_fnv=fnv(palette),pixels_fnv=fnv(pixels)))
p=a.out;d=dict(source_sha256=directory['source_sha256'],associations=maps);d['native_references']=rows;p.write_text(json.dumps(d,indent=2))
print('Original image references:',len(rows),'images across',len(set(x['article'] for x in rows)),'articles PASS')
