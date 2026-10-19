"""Read original aurora controls, picture commits and animation save requirements."""
from pathlib import Path
import argparse,collections,hashlib,json,struct
from astro_reader import parse
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
raw=(a.root/'PLACES/P517/MEGAFILE.HYP').read_bytes();s=parse(raw)
assert s['mode']==0 and s['layers']==1 and len(s['sprites'])==11 and len(s['scripts'])==2 and len(s['conditions'])==2
assert not s['movies'] and not s['mouse_rects']
assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled'] and not x['mouse_in'] and not x['mouse_out'] for x in s['sprites'])
def walk(v):
 if isinstance(v,dict):
  if 'opcode' in v:yield v
  else:
   for c in v.values():yield from walk(c)
 elif isinstance(v,list):
  for c in v:yield from walk(c)
commands=list(walk(s));pictures=[]
for c in commands:
 if c['opcode']!=20:continue
 name,x,y=c['args'];data=(a.root/'PLACES/P517'/name).read_bytes();w,h=struct.unpack_from('<ii',data,18)
 pictures.append(dict(file=name,x=x,y=y,width=w,height=h,sha256=hashlib.sha256(data).hexdigest(),offset=c['offset']))
assert len(pictures)==14 and len({p['file'] for p in pictures})==4
assert {(p['width'],p['height'],p['x'],p['y']) for p in pictures}=={(640,320,0,0)}
settings=[];branch=[]
for c in s['scripts'][1]:
 if c['opcode']==31 and c['args'][:2]==[1,1]:
  if branch:settings.append(branch)
  branch=[c]
 elif branch:branch.append(c)
if branch:settings.append(branch)
rows=[]
for branch in settings:
 value=branch[0]['args'][2];marker=next(c['args'][1:] for c in branch if c['opcode']==7)
 level=next(c['args'][2] for c in branch if c['opcode']==32)
 picture=next(c['args'][0] for c in branch if c['opcode']==20)
 timers=[c['args'] for c in branch if c['opcode']==19]
 stopped=[c['args'][0] for c in branch if c['opcode']==30]
 assert picture=='AURBACK'+str(level)
 assert timers==([] if level==1 else [[level+7,300 if level==4 else 100,1,0]])
 assert set(stopped)==set(range(9,12))-{level+7}
 rows.append(dict(setting=value,level=level,marker=marker,picture=picture,timers=timers,stopped=stopped))
assert [r['setting'] for r in rows]==list(range(1,15))
gauges=[c['args'] for c in s['scripts'][0] if c['opcode']==7]
assert gauges==[[7,x,361] for x in (447,477,507,536)]
comparisons=0
for first in pictures:
 for last in pictures:
  canvas=Image.new('RGB',(640,480),(17,33,65));canvas.paste(Image.open(a.root/'PLACES/P517'/first['file']).convert('RGB'),(0,0))
  canvas.paste(Image.open(a.root/'PLACES/P517'/last['file']).convert('RGB'),(0,0))
  restored=Image.new('RGB',(640,480),(17,33,65));restored.paste(Image.open(a.root/'PLACES/P517'/last['file']).convert('RGB'),(0,0))
  assert canvas.tobytes()==restored.tobytes();comparisons+=1
mutations=[c for c in commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)]
assert {c['opcode'] for c in mutations}=={7,16,17,19,30}
audio={name:hashlib.sha256((a.root/'PLACES/P517'/name).read_bytes()).hexdigest() for name in ('S0.WAV','S1.WAV')}
report=dict(date='2026-10-19',status='PASS',scope='Original resource observations; no native-save or Windows runtime claim',source_sha256=hashlib.sha256(raw).hexdigest(),original_wav_sha256=audio,conditions=s['conditions'],sprite_frames=[len(x['frames']) for x in s['sprites']],settings=rows,gauge_positions=gauges,images=pictures,image_history_comparisons=comparisons,
 opcode_counts=dict(sorted(collections.Counter(c['opcode'] for c in commands).items())),mutations=mutations,
 requirements=['Retain both locals, current picture and gauge/marker stored and rendered positions','Retain all three animation phases, stopped inactive phases and frame timers; active cycles can remain saveable','Test minimum clamp, settings1-14, first/repeated success to P512 and unsolved exit to P157','Preserve the original P517 custom25 counter and S12 behavior independently of departure voice'])
a.out.write_text(json.dumps(report,indent=2));print('P517 original save inventory PASS:',len(rows),'settings,',comparisons,'opaque picture overwrites')
