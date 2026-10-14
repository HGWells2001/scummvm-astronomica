from pathlib import Path
import json,struct,hashlib
r=Path('outputs/astronomica-cleanroom'); ev=r/'evidence'
d=json.loads((ev/'help-directory.json').read_text()); src=Path('D:/astro/HELP/ASTRONOM.HLP').read_bytes(); refs=json.loads((ev/'help-compression.json').read_text())
article=-1; mappings=[]
for rec in refs['records']:
 if rec['kind']==2:article+=1;title=rec['text']
 for image in rec.get('inline_bitmap_ids',[]):mappings.append(dict(image=image,article=article,title=title,record=rec['address']))
assert len(mappings)==31
(ev/'help-image-articles.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(src).hexdigest(),associations=mappings),indent=2))
print([(m['image'],m['article'],m['title']) for m in mappings])
