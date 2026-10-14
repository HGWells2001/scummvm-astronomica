"""Independent BMP/mask composition for layered comet scenes and bottom clipping."""
import argparse,io,json,hashlib,re
from pathlib import Path
from PIL import Image,ImageChops
from astro_reader import parse,FormatError

ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--places',type=int,nargs='+',default=[502,503,504]);a=ap.parse_args()
rows=[]
for place in a.places:
 raw=(a.root/f'PLACES/P{place}/MEGAFILE.HYP').read_bytes()
 try:scene=parse(raw)
 except FormatError as e:
  match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e));assert match,e
  scene=parse(raw[:int(match[2],16)])
 def bmp(ref):return Image.open(io.BytesIO(raw[ref['offset']:ref['offset']+ref['size']])).convert('RGB')
 for variant in (0,1,2):
  dst=Image.new('RGB',(640,480));bg=bmp(scene['background']);control=bmp(scene['control'])
  dst.paste(bg,(0,0));dst.paste(control,(0,480-control.height))
  for layer in range(1,scene['layers']+1):
   for i,s in enumerate(scene['sprites']):
    if s['layer']!=layer:continue
    visible=s['visible'];x,y=s['xy'];f=0
    # Force paired sprites to overlap, including the graphic-area boundary.
    if variant and ((place==502 and i==19) or (place==503 and 23<=i<=32) or (place==504 and 22<=i<=29) or (place==516 and 13<=i<=20)):
     visible=1;x=300;y=150 if variant==1 else 310
    if not visible:continue
    owner=i;visited=set()
    while scene['sprites'][owner]['clone']>0:
     assert owner not in visited;visited.add(owner);owner=scene['sprites'][owner]['clone']-1
    if not scene['sprites'][owner]['frames']:continue
    image,mask=map(bmp,scene['sprites'][owner]['frames'][f]);height=max(0,min(image.height,s['rect'][1]-y))
    if height:
     dst.paste(image.crop((0,0,image.width,height)),(x,y),ImageChops.invert(mask.crop((0,0,mask.width,height))).convert('L'))
  hashes=[]
  for rgb565 in (False,True):
   h=2166136261
   for r,g,b in dst.crop((0,0,640,456)).getdata():
    if rgb565:r=(r&248)|(r>>5);g=(g&252)|(g>>6);b=(b&248)|(b>>5)
    for v in (r,g,b):h=((h^v)*16777619)&0xffffffff
   hashes.append(hex(h))
  rows.append(dict(scene=place,variant=variant,rgb888=hashes[0],rgb565=hashes[1]))
a.out.write_text(json.dumps(dict(status='Independent original resource composition; native comparison separate',rows=rows),indent=2))
print('Comet rendering reference:',len(rows),'compositions',rows)
