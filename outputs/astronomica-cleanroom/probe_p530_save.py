"""Original P530 save requirements; no new save implementation."""
from pathlib import Path
import argparse,collections,hashlib,json,struct
from astro_reader import parse
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
raw=(a.root/'PLACES/P530/MEGAFILE.HYP').read_bytes();s=parse(raw)
assert s['mode']==0 and s['layers']==1 and len(s['sprites'])==29 and len(s['scripts'])==11 and not s['movies']
assert [c[2] for c in s['conditions']]==[1,1,1,1,1,1,1,1,1,5,5,5,1,5]
assert [len(x['frames']) for x in s['sprites']]==[2]*4+[1]*25
assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled'] for x in s['sprites'])
commands=[]
def walk(value,path):
 if isinstance(value,dict):
  if 'opcode' in value:commands.append(dict(path=path,**value))
  for key,child in value.items():walk(child,path+'/'+key)
 elif isinstance(value,list):
  for i,child in enumerate(value):walk(child,path+'/'+str(i))
walk(s,'scene')
counts=collections.Counter(c['opcode'] for c in commands)
assert counts[20]==25 and counts[24]==0
images=[]
for c in commands:
 if c['opcode']!=20:continue
 name,x,y=c['args'];data=(a.root/'PLACES/P530'/name.upper()).read_bytes()
 assert data[:2]==b'BM' and [x,y]==[460,10]
 width,height=struct.unpack_from('<ii',data,18)
 images.append(dict(file=name.upper(),x=x,y=y,width=width,height=height,sha256=hashlib.sha256(data).hexdigest(),command_offset=c['offset']))
assert len({i['file'] for i in images})==25 and {(i['width'],i['height']) for i in images}=={(172,172)}
decoded=[Image.open(a.root/'PLACES/P530'/i['file']).convert('RGB') for i in images]
canvas=Image.new('RGB',(640,480),(17,33,65));comparisons=0
for first in decoded:
 for last in decoded:
  continuous=canvas.copy();continuous.paste(first,(460,10));continuous.paste(last,(460,10))
  restored=canvas.copy();restored.paste(last,(460,10));assert continuous.tobytes()==restored.tobytes();comparisons+=1
assert comparisons==625
mutations=[c for c in commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)]
assert {c['opcode'] for c in mutations}=={7,16,17}
assert all(1<=c['args'][0]<=29 for c in mutations)
random=[c for c in commands if c['opcode']==39];assert len(random)==1 and random[0]['args']==[1,11,1,9]
assert s['scripts'][0][0]['args']==[1,13,3,0,0,0]
assert any(c['opcode']==5 and c['args']==[228] for c in s['scripts'][0])
report=dict(date='2026-10-18',status='PASS',scope='Original resource requirements only; P530 native saves not implemented',source_sha256=hashlib.sha256(raw).hexdigest(),
 conditions=s['conditions'],sprite_frames=[len(x['frames']) for x in s['sprites']],startup_programs=len(s['scripts']),mouse_rectangles=len(s['mouse_rects']),
 command_count=len(commands),opcode_counts={str(k):v for k,v in sorted(counts.items())},image_commits=25,images=images,image_history_comparisons=625,image_history_scope='Opaque original RGB pictures on a sentinel canvas; common172x172 footprint, no native state restoration claim',movies=0,automatic_animation=False,automatic_movement=False,
 mutation_commands=mutations,mutated_sprites=sorted({c['args'][0]-1 for c in mutations}),random_selection=random,
 completion_gate=dict(local=13,value=3,destination=228),
 requirements=['Snapshot14 locals and all runner metadata/RNG, including choice local9 and mask local11','Preserve partially placed component flags, all mutable visibility/frame state and mouse rectangle hover','Reject pending commands, foreground audio and button pulses; preflight the last committed picture or absence and prove its overwrite/history footprint','Verify three randomized rounds, both component orders, wrong/repeated selection, unsolved exit and fresh-process continuation','P530 has exceptional completion semantics: original global46 and S12 voice, without increasing the puzzle counter; use the separate original executable proof'])
a.out.write_text(json.dumps(report,indent=2));print('P530 save inventory PASS:',len(commands),'commands,25 image commits, dimensions',sorted({(i['width'],i['height']) for i in images}))
