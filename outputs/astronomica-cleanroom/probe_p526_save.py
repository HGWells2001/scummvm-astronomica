"""Read original P526 save requirements without claiming save implementation."""
from pathlib import Path
import argparse,hashlib,json,struct
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
folder=a.root/'PLACES/P526';raw=(folder/'MEGAFILE.HYP').read_bytes();scene=parse(raw)
assert scene['mode']==0 and scene['layers']==1 and len(scene['sprites'])==23
assert len(scene['scripts'])==2 and len(scene['mouse_rects'])==6 and not scene['movies']
assert [c[2] for c in scene['conditions']]==[6,9,6,6,1,4,1]
animations=[dict(index=i,frames=len(s['frames']),parameters=s['frame_data'],xy=s['xy']) for i,s in enumerate(scene['sprites']) if s['auto_frame']]
assert [(x['index'],x['frames'],x['parameters']) for x in animations]==[(17,12,[100,1,0]),(19,12,[30,1,0]),(21,12,[30,1,0])]
scripts=[(f'program{i}',s) for i,s in enumerate(scene['scripts'])]
for kind,items in [('sprite',scene['sprites']),('rect',scene['mouse_rects'])]:
 for i,s in enumerate(items):
  for event in ('click','drag','mouse_in','mouse_out'):
   if s.get(event):scripts.append((f'{kind}{i}.{event}',s[event]))
pictures=[];custom=[];hover=[]
for source,script in scripts:
 if source.endswith(('mouse_in','mouse_out')):hover.append(dict(source=source,commands=script))
 for n,c in enumerate(script):
  if c['opcode']==20:
   name,x,y=c['args'];data=(folder/name.upper()).read_bytes();w,h=struct.unpack_from('<ii',data,18)
   assert data[:2]==b'BM' and (x,y)==(90,361) and script[n+1]['opcode']==49
   pictures.append(dict(file=name.upper(),x=x,y=y,width=w,height=h,sha256=hashlib.sha256(data).hexdigest(),offset=c['offset']))
  if c['opcode']==23 and c['args'][0]==13:custom.append(dict(source=source,args=c['args'],offset=c['offset']))
assert len(pictures)==6 and len({(p['width'],p['height']) for p in pictures})==1
assert [c['args'] for c in custom if c['args'][1]==0]==[[13,0,20,0,0,0],[13,0,22,0,0,0],[13,0,23,13,-50,0]]
result=dict(date='2026-10-18',status='PASS',scope='Original resource inventory; not native save support',source_sha256=hashlib.sha256(raw).hexdigest(),local_conditions=scene['conditions'],animations=animations,pictures=pictures,orbit_commands=custom,hover=hover,
 requirements=['Preserve all three animation states, including hidden sprites','Preserve moved render coordinates separately from original orbital center coordinates','Preserve stopped orbit parameters, frame/range, move/frame epochs, deltas and quadrant flags','Track the committed scenario image, including pre-experiment absence','Retain hover-entered state for six answer rectangles and sprite targets','Prove answer identity and full subsequent trajectories after restore'])
a.out.write_text(json.dumps(result,indent=2));print('P526 original save inventory PASS: six images, three animations, orbit commands and hover scripts')
