"""Original HLP command placement and font-use inventory, independent of native UI."""
from pathlib import Path
import argparse,collections,hashlib,json

ap=argparse.ArgumentParser()
ap.add_argument('root',type=Path)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
source=a.root/'HELP/ASTRONOM.HLP'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
decoded=json.loads((a.out.parent/'help-compression.json').read_text())
formatted=json.loads((a.out.parent/'help-format.json').read_text())
assert digest==decoded['source_sha256']==formatted['source_sha256']
formats={r['address']:r for r in formatted['records']}
fonts={f['index']:f for f in formatted['styles']}
uses=collections.defaultdict(list)
article=-1
images=[]
for rec in decoded['records']:
 if rec['kind']==2:
  article+=1;title=rec['text'];font=3;position=0
  continue
 row=formats[rec['address']]
 for para in row['paragraphs']:
  cursor=para['text_offset']
  for number,cmd in enumerate(para['commands']):
   text=cmd['text']
   assert rec['text'][cursor:cursor+len(text)]==text
   if text:
    uses[font].append(dict(article=article,title=title,record=rec['address'],offset=cursor,text=text))
   position+=len(text);cursor+=len(text)+1
   if cmd['opcode']==0x80:font=cmd['font']
   elif cmd['opcode']==0x86:
    assert rec['kind']==32 and 'column' not in para
    images.append(dict(image=cmd['image'],article=article,title=title,record=rec['address'],command=number,
                       body_offset=cursor,text_characters_before=position,kind=rec['kind']))
assert [i['image'] for i in images]==list(range(31))
assert len({i['article'] for i in images})==20
font_rows=[]
for index,description in fonts.items():
 rows=uses[index]
 chars=collections.Counter(c for row in rows for c in row['text'])
 font_rows.append(dict(**description,nonempty_runs=len(rows),characters=sum(chars.values()),
                       character_counts={f'{ord(c):02x}':n for c,n in sorted(chars.items())},
                       runs=rows if description['name'] not in ('Arial','Helv') or description['flags']&~3 else []))
result=dict(date='2026-10-13',source_sha256=digest,images=images,font_usage=font_rows,
            findings=['All 31 image commands are in paragraph records, none in table cells.',
                      'Image order is derived from original NUL/command pairs, not inferred from captions.',
                      'Font usage is raw evidence; flag meanings and symbol mappings are not inferred from appearance.'])
a.out.write_text(json.dumps(result,indent=2))
print('Original inline placement: 31 images in 20 articles; paragraph-only PASS')
for row in font_rows:
 print(row['index'],row['name'],'flags',row['flags'],'runs',row['nonempty_runs'],'characters',row['characters'])
