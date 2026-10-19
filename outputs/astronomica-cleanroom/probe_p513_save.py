"""Original photon-puzzle resources and stopped-save image requirements."""
from pathlib import Path
import argparse,collections,hashlib,json,struct
from astro_reader import parse
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
raw=(a.root/'PLACES/P513/MEGAFILE.HYP').read_bytes();s=parse(raw);commands=[]
def walk(v,path):
 if isinstance(v,dict):
  if 'opcode' in v:commands.append(dict(path=path,**v))
  for k,c in v.items():walk(c,path+'/'+k)
 elif isinstance(v,list):
  for i,c in enumerate(v):walk(c,path+'/'+str(i))
walk(s,'scene')
assert s['mode']==0 and s['layers']==1 and len(s['sprites'])==32 and len(s['conditions'])==6 and len(s['scripts'])==4 and not s['movies']
assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled'] for x in s['sprites'])
assert not s['mouse_rects'] and all(not x['mouse_in'] and not x['mouse_out'] for x in s['sprites'])
images=[]
for c in commands:
 if c['opcode']!=20:continue
 name,x,y=c['args'];data=(a.root/'PLACES/P513'/name.upper()).read_bytes();assert data[:2]==b'BM'
 w,h=struct.unpack_from('<ii',data,18)
 images.append(dict(file=name.upper(),x=x,y=y,width=w,height=h,sha256=hashlib.sha256(data).hexdigest(),offset=c['offset']))
assert len(images)==33 and len({x['file'] for x in images})==17
assert {(i['x'],i['y'],i['width'],i['height']) for i in images}=={(177,22,313,320)}
mutations=[c for c in commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)]
assert {c['opcode'] for c in mutations}=={7,16,17}
comparisons=0
if images and len({(i['x'],i['y'],i['width'],i['height']) for i in images})==1:
 pictures=[Image.open(a.root/'PLACES/P513'/i['file']).convert('RGB') for i in images]
 canvas=Image.new('RGB',(640,480),(17,33,65));xy=(images[0]['x'],images[0]['y'])
 for first in pictures:
  for last in pictures:
   continuous=canvas.copy();continuous.paste(first,xy);continuous.paste(last,xy)
   restored=canvas.copy();restored.paste(last,xy);assert continuous.tobytes()==restored.tobytes();comparisons+=1
report=dict(date='2026-10-19',status='PASS',scope='Original resource inventory only; no native save claim',source_sha256=hashlib.sha256(raw).hexdigest(),conditions=s['conditions'],sprite_frames=[len(x.get('frames',[])) for x in s['sprites']],sprite_clones=[x['clone'] for x in s['sprites']],
 startup=s['scripts'],mouse_rectangles=s['mouse_rects'],mutations=mutations,opcode_counts=dict(sorted(collections.Counter(c['opcode'] for c in commands).items())),images=images,image_history_comparisons=comparisons,
 image_history_scope='Original opaque RGB BMP overwrite on sentinel canvas; not native continuation',
 requirements=['Retain six locals, RNG and fourteen-scenario mask, first/repeat silent success count and error limit','Use complete settled sprite records including hidden photon endpoint, retained standardMotion flag and stopped timer fields','Reject an active photon trajectory or pending work until all timers settle','Retain the full current cube picture; intermediate half-step pictures occur inside pending knob programs','Check all nine settings/digit results, bounds, first/repeated success, errors and physical fresh-process continuation'])
a.out.write_text(json.dumps(report,indent=2));print('P513 original save inventory PASS; picture overwrite comparisons',comparisons)
