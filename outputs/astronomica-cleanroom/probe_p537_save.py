"""Inventory original rocket save boundaries; no new runtime/save support claim."""
from pathlib import Path
import argparse,collections,hashlib,json
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
raw=(a.root/'PLACES/P537/MEGAFILE.HYP').read_bytes();s=parse(raw)
assert s['mode']==0 and s['layers']==1 and len(s['sprites'])==48 and len(s['scripts'])==1
assert s['conditions']==[[1,0,16,0,0,15]] and not s['movies'] and not s['mouse_rects']
assert all(not x.get('auto_frame') and not x.get('auto_move') and not x.get('drag_enabled') and not x.get('mouse_in') and not x.get('mouse_out') for x in s['sprites'])
def walk(v):
 if isinstance(v,dict):
  if 'opcode' in v:yield v
  else:
   for c in v.values():yield from walk(c)
 elif isinstance(v,list):
  for c in v:yield from walk(c)
commands=list(walk(s));counts=collections.Counter(c['opcode'] for c in commands)
assert not any(counts[x] for x in (20,49,21))
launch=s['sprites'][32]['click'];custom=next(i for i,c in enumerate(launch) if c['opcode']==23 and c['args'][0]==14)
assert launch[0]['opcode']==28 and launch[-1]['opcode']==29
assert any(c['delay']>0 for c in launch[custom+1:])
assert any(c['opcode']==23 and c['args'][0]==25 for c in launch[custom+1:])
assert any(c['opcode']==5 and c['args']==[321] for c in launch[custom+1:])
for i,delta,bound,limit in [(4,-1,-1,0),(5,1,16,15)]:
 click=s['sprites'][i]['click']
 assert any(c['opcode']==46 and c['args']==[1,0,delta] for c in click)
 assert any(c['opcode']==31 and c['args'][:3]==[1,0,bound] for c in click)
 assert any(c['opcode']==32 and c['args']==[1,0,limit] for c in click)
rows=[]
for i,x in enumerate(s['sprites']):
 source=x;clone=x['clone']
 if clone>0:source=s['sprites'][clone-1];assert source['clone']==-1
 rows.append(dict(id=i+1,clone=clone,frames=len(source['frames']),xy=source['xy'],visible=source['visible'],click_enabled=source['click_enabled']))
report=dict(date='2026-10-19',status='PASS',scope='Original resource observations only; no new save support or Windows runtime claim',
 source_sha256=hashlib.sha256(raw).hexdigest(),conditions=s['conditions'],sprites=rows,opcode_counts=dict(sorted(counts.items())),
 startup_scripts=s['scripts'],launch_control=33,launch_commands=launch,launch_custom_index=custom,
 mutations=[c for c in commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)],
 original_wav_sha256={name:hashlib.sha256((a.root/'PLACES/P537'/name).read_bytes()).hexdigest() for name in ('S0.WAV','S1.WAV')},
 requirements=['Retain selector0..15 and cloned indicator frames/visibility',
 'Launch custom14 has a delayed script continuation under click blocking; a settled-only format cannot infer that continuation from rocket coordinates',
 'Consider separate native RocketMotion kind/delta/since as well as all sprite records, even for a stopped rocket',
 'Retain dormant cross-puzzle state; test live selector changes only where actual controls permit them',
 'Original callback and success observations remain separately recorded by probe_rocket.py and its evidence'])
a.out.write_text(json.dumps(report,indent=2));print('P537 original save requirements PASS:',len(rows),'sprites; pending launch continuation recorded')
