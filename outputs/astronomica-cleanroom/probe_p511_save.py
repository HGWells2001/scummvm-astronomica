"""Fresh original P511 resource profile; no engine or original runtime execution."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RESEARCH=ROOT/'outputs/astronomica-cleanroom'
sys.path.insert(0,str(RESEARCH))
from astro_reader import parse

ap=argparse.ArgumentParser()
ap.add_argument('--scene',type=int,required=True)
ap.add_argument('--original-root',type=Path,default=Path('D:/astro'))
ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args()
assert args.scene==511
path=args.original_root/f'PLACES/P{args.scene}/MEGAFILE.HYP'
raw=path.read_bytes()
assert len(raw)==635643 and hashlib.sha256(raw).hexdigest()=='c3e2e2c92289a076b686e8f6a408d9fc13fe9fdf4fad2934aaca57b4ffd7df3f'
scene=parse(raw)
sha=lambda b:hashlib.sha256(b).hexdigest()
commands=[]
def walk(value,location):
    if isinstance(value,dict):
        if 'opcode' in value:commands.append(dict(location=location,**value))
        for key,child in value.items():walk(child,location+'/'+key)
    elif isinstance(value,list):
        for i,child in enumerate(value):walk(child,location+'/'+str(i))
walk(scene,'scene')
sprites=[]
for i,sprite in enumerate(scene['sprites']):
    owner=i
    while scene['sprites'][owner]['clone']!=-1:
        parent=scene['sprites'][owner]['clone']-1
        assert 0<=parent<owner
        owner=parent
    sprites.append(dict(id=i+1,frame_owner=owner+1,
        geometry=[[f[0]['width'],f[0]['height']] for f in scene['sprites'][owner]['frames']],
        **{k:v for k,v in sprite.items() if k!='frames'}))
assets=[dict(name=p.name,size=p.stat().st_size,sha256=sha(p.read_bytes()))
    for p in sorted(path.parent.iterdir()) if p.is_file() and p!=path]
result=dict(status='STATIC_ORIGINAL_INVENTORY_ONLY',date='2026-10-25',scene=args.scene,
    source=dict(path=str(path),size=len(raw),sha256=sha(raw)),
    reader_sha256=sha((RESEARCH/'astro_reader.py').read_bytes()),
    mode=scene['mode'],layers=scene['layers'],background=scene['background'],control=scene['control'],
    sprite_count=len(sprites),condition_count=len(scene['conditions']),
    startup_program_count=len(scene['scripts']),command_count=len(commands),
    opcode_counts=dict(sorted(collections.Counter(c['opcode'] for c in commands).items())),
    sprites=sprites,programs=scene['scripts'],conditions=scene['conditions'],
    mouse_rects=scene['mouse_rects'],sounds=scene['sounds'],movies=scene['movies'],
    commands=commands,assets=assets,
    limitations=['Original resource parsing only; no native or original runtime execution',
        'No new save format, eligibility, reachability or continuation claim'])
assert len(sprites)==35 and len(scene['conditions'])==6 and len(scene['scripts'])==5 and len(commands)==221
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(json.dumps(result,indent=2)+'\n')
print('Static original inventory',args.scene,'sprites',len(sprites),'programs',len(scene['scripts']),'commands',len(commands),flush=True)


