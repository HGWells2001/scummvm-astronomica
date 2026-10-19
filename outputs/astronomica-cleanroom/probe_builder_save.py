"""Inventory original builder save state without executing or guessing scripts."""
from pathlib import Path
import argparse,collections,hashlib,json,struct
from astro_reader import parse
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
def walk(v):
 if isinstance(v,dict):
  if 'opcode' in v:yield v
  else:
   for c in v.values():yield from walk(c)
 elif isinstance(v,list):
  for c in v:yield from walk(c)
rows=[]
for n in (515,536):
 raw=(a.root/f'PLACES/P{n}/MEGAFILE.HYP').read_bytes();s=parse(raw);commands=list(walk(s))
 assert s['mode']==0 and s['layers']==1 and len(s['sprites'])==60 and len(s['conditions'])==13 and len(s['scripts'])==7
 assert not s['movies'] and not s['mouse_rects']
 assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled'] and not x['mouse_in'] and not x['mouse_out'] for x in s['sprites'])
 frames=[len(x['frames']) if x['clone']<0 else len(s['sprites'][x['clone']-1]['frames']) for x in s['sprites']]
 assert frames==[2 if 4<=i<=13 else 1 for i in range(60)]
 images=[]
 for c in commands:
  if c['opcode']!=20:continue
  name,x,y=c['args'];data=(a.root/f'PLACES/P{n}'/name).read_bytes();w,h=struct.unpack_from('<ii',data,18)
  images.append(dict(file=name,x=x,y=y,width=w,height=h,sha256=hashlib.sha256(data).hexdigest(),offset=c['offset']))
 assert len(images)==2 and {p['file'] for p in images}=={'drydock','pad'}
 assert {(p['width'],p['height'],p['x'],p['y']) for p in images}=={(250,330,0,0)}
 comparisons=0
 for first in images:
  for last in images:
   canvas=Image.new('RGB',(640,480),(17,33,65));canvas.paste(Image.open(a.root/f'PLACES/P{n}'/first['file']).convert('RGB'),(0,0))
   canvas.paste(Image.open(a.root/f'PLACES/P{n}'/last['file']).convert('RGB'),(0,0))
   restored=Image.new('RGB',(640,480),(17,33,65));restored.paste(Image.open(a.root/f'PLACES/P{n}'/last['file']).convert('RGB'),(0,0))
   assert canvas.tobytes()==restored.tobytes();comparisons+=1
 mutations={op:sorted({tuple(c['args']) for c in commands if c['opcode']==op}) for op in (7,15,16,17,18,19,24,30,47,48)}
 assert {op for op,v in mutations.items() if v}=={7,15,16,17,47}
 invalid_frames=[dict(sprite=args[0],requested_frame=args[1],loaded_frames=frames[args[0]-1]) for args in mutations[15] if args[1]>=frames[args[0]-1]]
 assert invalid_frames==[dict(sprite=15,requested_frame=1,loaded_frames=1)]
 launch=s['sprites'][7]['click'];choose=s['sprites'][4]['click']
 first_condition=next(c for c in launch if c['opcode']==31)
 first_mask=next(c for c in launch if c['opcode']==32)
 assert first_condition['args']==[1,2,4,0,1,0] and first_mask['args']==[1,0,7]
 assert next(c['args'] for c in choose if c['opcode']==39)==[1,0,1,1]
 rows.append(dict(scene=n,status='PASS',source_sha256=hashlib.sha256(raw).hexdigest(),conditions=s['conditions'],sprite_frames=frames,sprite_initials=[dict(id=i+1,xy=x['xy'],visible=x['visible'],click_enabled=x['click_enabled'],clone=x['clone']) for i,x in enumerate(s['sprites'])],images=images,image_history_comparisons=comparisons,
  literal_mutations=mutations,ignored_frame_requests=invalid_frames,early_launch_prefix=dict(condition=first_condition,mask_assignment=first_mask),
  local_assignments={i:sorted({c['args'][2] for c in commands if c['opcode']==32 and c['args'][:2]==[1,i]}) for i in range(13)},
  local_additions=sorted({tuple(c['args']) for c in commands if c['opcode']==46}),opcode_counts=dict(sorted(collections.Counter(c['opcode'] for c in commands).items()))))
report=dict(date='2026-10-19',status='PASS',scope='Original resource observations only; no script execution, native save or Windows runtime claim',scenes=rows,
 requirements=['Preserve13 locals/RNG and all60 sprite records, including stored/rendered coordinates after offsets','Retain no picture or the last original250x330 picture; account for all480 screen rows','Do not save launch/assembly programs or button pulses while pending','Retain original P515 no-op success dispatch and P536 first/repeated global31 count','Verify all five designs, both phases, undersize/removal recovery, partial parts, reset controls and fresh-process continuation'],
 observations=['Launch begins with stage<4 and sets local0=7; choosing uses that mask through original command39','Literal setters include opcode7(0,0); native stored/rendered effects require separate boundary observations'],
 unknowns=['Literal mutation sets do not establish reachable combinations or coordinate extrema','Local/sprite/background relations require native boundary observations before defining a save validator','Complete manual audiovisual playthrough remains outstanding'])
a.out.write_text(json.dumps(report,indent=2));print('Builder original save inventory PASS: two scenes,60 sprites each,eight opaque image overwrites')
