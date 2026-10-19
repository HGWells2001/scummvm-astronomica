"""Inventory original six-scene custom17 resources for settled saves."""
from pathlib import Path
import argparse,collections,hashlib,json,re
from astro_reader import parse,FormatError
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
rows=[]
for place in (506,531,532,533,534,535):
 raw=(a.root/f'PLACES/P{place}/MEGAFILE.HYP').read_bytes()
 try:s=parse(raw)
 except FormatError as e:
  m=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e));assert m
  s=parse(raw[:int(m[2],16)])
 commands=[]
 def walk(v,path):
  if isinstance(v,dict):
   if 'opcode' in v:commands.append(dict(path=path,**v))
   for k,c in v.items():walk(c,path+'/'+k)
  elif isinstance(v,list):
   for i,c in enumerate(v):walk(c,path+'/'+str(i))
 walk(s,'scene');counts=collections.Counter(c['opcode'] for c in commands)
 assert s['mode']==0 and s['layers']==1 and len(s['conditions'])==7 and len(s['scripts'])==2 and not s['movies']
 assert s['conditions'][:3]==[[0,0,6,1,1,6],[0,1,6,0,0,63],[0,2,6,0,0,63]]
 answer_count={506:3,531:4,532:3,533:3,534:5,535:3}[place]
 choice_count={506:5,531:5,532:4,533:4,534:7,535:4}[place]
 assert [c[:3] for c in s['conditions'][3:]]==[[1,0,answer_count],[1,1,8 if place==534 else 6],[1,2,1],[1,3,1]]
 assert not any(c['opcode'] in (20,24) for c in commands)
 assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled'] and not x['has_cursor'] for x in s['sprites'])
 assert all(not x['mouse_in'] and not x['mouse_out'] for x in s['sprites']+s['mouse_rects'])
 assert [len(x['frames']) for x in s['sprites']]==[2]*(4+choice_count)+[1]*(len(s['sprites'])-4-choice_count)
 mutations=[c for c in commands if c['opcode'] in (7,15,16,17,18,19,30,47,48)]
 row=dict(scene=place,source_sha256=hashlib.sha256(raw).hexdigest(),conditions=s['conditions'],
  sprites=[dict(index=i,clone=x['clone'],frames=len(x.get('frames',[])),visible=x['visible'],xy=x['xy'],click_type=x.get('click_type'),hover_in=x['mouse_in'],hover_out=x['mouse_out']) for i,x in enumerate(s['sprites'])],
  startup=s['scripts'],mouse_rectangles=s['mouse_rects'],opcode_counts=dict(sorted(counts.items())),mutations=mutations,
  sound_ids=s['sounds'],intro=s.get('intro_sound_id'),background=s['background'],control=s['control'])
 rows.append(row)
 print(place,'sprites',len(s['sprites']),'conditions',s['conditions'],'mutations',dict(collections.Counter(c['opcode'] for c in mutations)),'hover',sum(bool(x['mouse_in'] or x['mouse_out']) for x in s['sprites']))
a.out.write_text(json.dumps(dict(date='2026-10-19',status='PASS',scope='Original resource inventory only; no native variant save claim',scenes=rows),indent=2))
