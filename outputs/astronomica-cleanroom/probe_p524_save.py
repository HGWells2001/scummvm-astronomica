"""Original-resource requirements for P524 saves; independent of native tests."""
from pathlib import Path
import argparse,hashlib,json,struct
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
p=a.root/'PLACES/P524';raw=(p/'MEGAFILE.HYP').read_bytes();s=parse(raw)
assert s['mode']==0 and s['layers']==1 and len(s['sprites'])==32 and len(s['scripts'])==5 and not s['mouse_rects'] and not s['movies']
assert [c[2] for c in s['conditions']]==[8,8,1,3,1,4]
assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled'] for x in s['sprites'])
frame_counts=[len(x['frames']) for x in s['sprites']]
assert frame_counts==[2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,2,8]
scripts=[(f'program{i}',x) for i,x in enumerate(s['scripts'])]
for i,sprite in enumerate(s['sprites']):
 for ev in ('click','drag','mouse_in','mouse_out'):
  if sprite.get(ev):scripts.append((f'sprite{i}.{ev}',sprite[ev]))
pictures=[];timers=[];stops=[];transfers=[]
for source,script in scripts:
 for i,c in enumerate(script):
  if c['opcode']==20:
   name,x,y=c['args'];data=(p/name.upper()).read_bytes()
   assert (x,y)==(0,0) and data[:2]==b'BM' and struct.unpack_from('<ii',data,18)==(640,320)
   assert script[i+1]['opcode']==49
   pictures.append(dict(file=name.upper(),width=640,height=320,x=x,y=y,sha256=hashlib.sha256(data).hexdigest()))
  if c['opcode']==19:timers.append(dict(source=source,args=c['args'],offset=c['offset']))
  if c['opcode']==30:stops.append(dict(source=source,args=c['args'],offset=c['offset']))
  if c['opcode']==23 and c['args'][0]==28:transfers.append(dict(source=source,args=c['args'],offset=c['offset']))
assert len(pictures)==9 and len({x['file'] for x in pictures})==9
assert len(timers)==1 and timers[0]['args']==[32,200,1,0] and timers[0]['source']=='program3'
assert len(stops)==1 and stops[0]['args']==[32] and stops[0]['source']=='program1'
assert len(s['sprites'][31]['frames'])==8
moon=s['scripts'][2]
assert moon[3]['args']==[1,1,255,0,0,0] and moon[4]['args']==[1,0,9]
assert moon[5]['args']==['viewmoon',0,0]
assert [(x['source'],x['args'][:2]) for x in transfers]==[('program0',[28,1]),('sprite30.click',[28,0])]
a.out.write_text(json.dumps(dict(date='2026-10-18',status='PASS',source_sha256=hashlib.sha256(raw).hexdigest(),local_conditions=s['conditions'],pictures=pictures,animation_start=timers,animation_stop=stops,animated_sprite_index=31,animated_frame_count=8,help_transfers=transfers,requirements=['Reconstruct one committed 640x320 image, including final Moon after the eight randomized choices','Serialize sprite31 animation enable, selected frame, frame period/range and last-frame epoch','Keep all global/local known/width/value metadata across mentor-help transfer','Validate continuation immediately before and at the 200ms frame boundary and after clock wrap','Exclude queued actions and foreground audio, preserve native help return behavior'],moon_sequence=dict(mask=255,scenario=9,condition_offset=moon[3]['offset'],image_offset=moon[5]['offset']),limitation='Original-resource inventory only; native save tests are recorded separately.'),indent=2))
print('Original P524 save requirements PASS: nine images, eight-frame Triton animation, two help-transfer commands')
report=json.loads(a.out.read_text())
report['sprite_frame_counts']=frame_counts
report['sprite31_original_geometry']={key:s['sprites'][31][key] for key in ('xy','layer','visible','click_enabled','drag_enabled')}
a.out.write_text(json.dumps(report,indent=2))
