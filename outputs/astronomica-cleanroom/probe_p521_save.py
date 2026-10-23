"""Fresh static P521 profile. No engine, script or original-runtime execution."""
from pathlib import Path
import argparse,collections,hashlib,json,sys
sys.dont_write_bytecode=True
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here))
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path)
ap.add_argument('--out',type=Path,default=here/'evidence/p521-save-original.json')
a=ap.parse_args();p=a.root/'PLACES/P521/MEGAFILE.HYP';raw=p.read_bytes();s=parse(raw)
sha=lambda b:hashlib.sha256(b).hexdigest()
assert len(raw)==717441 and sha(raw)=='fd9e9e50e785604aec367a90213c5454c179fa5f93e81da50bed1cf095017f47'
assert s['mode']==0 and s['layers']==1 and len(s['sprites'])==27 and not s['conditions']
assert len(s['scripts'])==1 and s['scripts'][0][0]['args']==[13,15,251,2]
commands=[]
def walk(v,path):
    if isinstance(v,dict):
        if 'opcode' in v:commands.append(dict(path=path,**v))
        for k,x in v.items():walk(x,path+'/'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v):walk(x,path+'/'+str(i))
walk(s,'scene');assert len(commands)==175
sprites=[]
for i,v in enumerate(s['sprites']):
    owner=i
    while s['sprites'][owner]['clone']!=-1:
        parent=s['sprites'][owner]['clone']-1;assert 0<=parent<owner;owner=parent
    frames=s['sprites'][owner]['frames']
    sprites.append(dict(id=i+1,frame_owner=owner+1,geometry=[[f[0]['width'],f[0]['height']] for f in frames],**{k:x for k,x in v.items() if k!='frames'}))
assets=[]
for f in sorted(p.parent.iterdir()):
    if not f.is_file() or f==p:continue
    b=f.read_bytes();assets.append(dict(name=f.name,size=len(b),sha256=sha(b)))
earth=next(f for f in p.parent.iterdir() if f.name.upper()=='EARTH_B').read_bytes()
bg=s['background'];assert earth==raw[bg['offset']:bg['offset']+bg['size']]
fnv=2166136261
for b in raw:fnv=((fnv^b)*16777619)&0xffffffff
anchors={}
for name,terms in {'astronomica.cpp':['stageBackgroundImage(', 'displayBackgroundImage()', 'verifyP521Puzzle(', 'p526SpriteWords(', 'p526RestoreSprite('], 'script.cpp':['if (c.opcode == 24)', 'c.opcode == 30', 'c.opcode == 49'], 'sprites.cpp':['advanceSpriteMove(', 'advanceSpriteFrame(']}.items():
    f=here/'engine/astronomica'/name;text=f.read_text();lines=text.splitlines()
    anchors[name]=dict(sha256=sha(f.read_bytes()),references={term:[i+1 for i,line in enumerate(lines) if term in line] for term in terms})
assert all(refs for row in anchors.values() for refs in row['references'].values())
result=dict(status='STATIC_ORIGINAL_PROFILE_ONLY',source=dict(path=str(p),size=len(raw),sha256=sha(raw),fnv1a32=fnv),reader_sha256=sha((here/'astro_reader.py').read_bytes()),
 mode=s['mode'],layers=s['layers'],sprite_count=27,condition_count=0,startup_program_count=1,command_count=175,opcode_counts=dict(sorted(collections.Counter(c['opcode'] for c in commands).items())),
 background=s['background'],control=s['control'],intro_sound=s.get('intro_sound_id'),sounds=s['sounds'],movies=s['movies'],conditions=s['conditions'],programs=s['scripts'],sprites=sprites,commands=commands,assets=assets,source_anchors=anchors,
 script_graph=[dict(control=i+1,commands=v['click'],transition=next((c['args'] for c in v['click'] if c['opcode']==5),None)) for i,v in enumerate(s['sprites']) if v.get('click')],
 findings=['Exactly one startup program; opcode24 means stored+render XY and frame, not a private callback.',
 'Clones inherit frames only, retaining original own positions and flags.',
 'Sprite12 autoFrame400 remains active at settled boundaries; sprite11 retains hidden 20ms animation history.',
 'Control5 stages ROCKS_b then EARTH_b and displays each via49; ROCKS display and pending image occur inside queued locked work.',
 'EARTH_B is byte-identical to embedded background, but displayed identity must still be preserved after control5.',
 'Fragments14..23 retain hidden stopped movement/frame parameters, coordinates, selected frames and epochs; repeated explosions do not reset them.',
 'No P521 private callback state beyond27-word sprite records was identified; orbit/planet private defaults must be checked explicitly.'],
 proposed_contract=dict(boundary='scriptsIdle, no queue/actions/button/hover/foreground/movie/pending-image, loop enabled',image_identity={'0':'original embedded background','1':'EARTH_B displayed at0,0; lower HYP/control preserved'},persistent='605 words including historical unknown local values, RNG, global/local metadata and variant',sprite_words=27,sprites=27,header_words=11,stream_bytes_including_magic_version=5392),
 unknowns=['Static evidence does not prove reachable history bounds or serializer correctness.','Native staged audit must observe repeated/mixed choices, hidden fragments and frame/timer ties before restrictive validators.','No format/support claim or original-runtime execution in this report.'])
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(a.out)
