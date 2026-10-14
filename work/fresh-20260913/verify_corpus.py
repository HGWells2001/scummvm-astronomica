from pathlib import Path
import sys,json,collections,io,hashlib,re
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path('outputs/astronomica-cleanroom').resolve()))
from astro_reader import parse,Reader,FormatError
root=Path(r'D:\astro');out=Path('outputs/astronomica-cleanroom');rows=[];bmp_count=0;ops=collections.Counter();texts=[]
def walk(x):
 if isinstance(x,dict):
  if 'opcode' in x:ops[x['opcode']]+=1
  if 'bpp' in x:yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
for p in sorted((root/'PLACES').glob('P*/MEGAFILE.HYP'),key=lambda p:int(p.parent.name[1:])):
 data=p.read_bytes();d=None
 try:d=parse(data)
 except FormatError as e:
  if 'trailing ' in str(e):
   end=int(str(e).split('0x')[1],16);d=parse(data[:end]);d['trailing_bytes']=len(data)-end
  else:rows.append(dict(place=p.parent.name,error=str(e)));continue
 for bm in walk(d):
  blob=data[bm['offset']:bm['offset']+bm['size']];im=Image.open(io.BytesIO(blob));im.load();assert im.size==(bm['width'],abs(bm['height']));bmp_count+=1
 row=dict(place=p.parent.name,mode=d['mode'],navigation=d['navigation'],sprites=d['sprite_count'],movies=d['movies'],trailing_bytes=d.get('trailing_bytes',0),consumed=d['consumed'],size=len(data))
 rows.append(row)
 if int(p.parent.name[1:]) in [1,3,27,29,98,103,187,219,408,433,512,513,514,519,521,530]:
  bm=d['background']
  if bm and 'offset' in bm:
   im=Image.open(io.BytesIO(data[bm['offset']:bm['offset']+bm['size']])).convert('RGB');im.thumbnail((320,240));texts.append((p.parent.name,im))
 if p.parent.name in ['P0','P29','P103']: (out/(p.parent.name+'-decoded.json')).write_text(json.dumps(d,indent=2))
# The contact sheet contains original backgrounds only; it is not a game screenshot.
canvas=Image.new('RGB',(4*340,((len(texts)+3)//4)*280),'#161d29');dr=ImageDraw.Draw(canvas)
for i,(name,im) in enumerate(texts):x=i%4*340+10;y=i//4*280+10;dr.text((x,y),name,fill='white');canvas.paste(im,(x,y+24))
canvas.save(out/'backgrounds.png')
(out/'scene-index.json').write_text(json.dumps(rows,indent=2))
(out/'corpus-summary.json').write_text(json.dumps(dict(scene_count=len(rows),decoded_structure=sum('error' not in x for x in rows),fully_consumed=sum('error' not in x and not x.get('trailing_bytes') for x in rows),validated_embedded_bitmaps=bmp_count,opcode_counts=dict(sorted(ops.items())),placedef_count=len(list(root.rglob('PLACEDEF')))),indent=2))
print((out/'corpus-summary.json').read_text())
