"""Fresh static P518 original inventory; no original/runtime/callback execution."""
from pathlib import Path
import argparse,collections,hashlib,json,sys,wave
sys.dont_write_bytecode=True
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,default=here/'evidence/p518-save-original.json');args=ap.parse_args()
p=args.root/'PLACES/P518/MEGAFILE.HYP';raw=p.read_bytes();s=parse(raw)
assert s['size']==s['consumed']==489731 and s['mode']==0 and s['layers']==1 and len(s['sprites'])==32 and len(s['scripts'])==3
assert s['conditions']==[[1,0,20,0,0,20],[1,1,9,0,0,511],[1,2,9,1,1,9],[1,3,20,0,0,20]]
commands=[]
def walk(v,path):
 if isinstance(v,dict):
  if 'opcode' in v:commands.append(dict(path=path,**v))
  for k,x in v.items():walk(x,path+'/'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):walk(x,path+'/'+str(i))
walk(s,'scene');counts=collections.Counter(c['opcode'] for c in commands)
assert len(commands)==111 and counts[39]==3 and not any(counts[k] for k in (3,20,49))
assert not s['movies'] and not s['mouse_rects']
sprites=[]
for i,x in enumerate(s['sprites']):
 owner=i;seen=set()
 while s['sprites'][owner]['clone']!=-1:
  assert owner not in seen;seen.add(owner);owner=s['sprites'][owner]['clone']-1;assert 0<=owner<i
 frames=s['sprites'][owner]['frames'];row={k:v for k,v in x.items() if k!='frames'};row.update(id=i+1,frame_owner=owner+1,frame_count=len(frames),dimensions=sorted({(f[0]['width'],f[0]['height']) for f in frames}));sprites.append(row)
assert [x['id'] for x in sprites if x['clone']!=-1]==list(range(19,33))
assert all(x['frame_owner']==7 for x in sprites[18:])
refs={}
for name,anchors in {'sprites.cpp':['int advancePlanet(','bool advanceSpriteMove('],'astronomica.cpp':['planet.planetMotion = 1;','planet.planetMotion = 2;','const int result = advancePlanet(','bool AstronomicaEngine::verifyP518Puzzle()'],'script.cpp':['else if (c.args[0] == 12) {','} else if (c.opcode == 39) {'],'resource.h':['int planetMotion =','int32 planetPeriod =']}.items():
 f=here/'engine/astronomica'/name;b=f.read_bytes();lines=b.decode().splitlines();refs[name]=dict(path=str(f),sha256=hashlib.sha256(b).hexdigest(),anchors={a:next(i+1 for i,l in enumerate(lines) if a in l) for a in anchors})
audio=[]
for f in sorted(p.parent.glob('*.WAV')):
 with wave.open(str(f),'rb') as w:meta=dict(channels=w.getnchannels(),sample_rate=w.getframerate(),frames=w.getnframes(),seconds=w.getnframes()/w.getframerate())
 audio.append(dict(name=f.name,size=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),**meta))
h=2166136261
for b in raw:h=((h^b)*16777619)&0xffffffff
probe=here/'probe_p518_planets.py';prior=here/'evidence/p518-planets.json'
report=dict(status='STATIC_ORIGINAL_INVENTORY_ONLY',evidence_id='p518-save-original-static-cleanroom',source=dict(path=str(p),size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),fnv1a32=f'{h:08x}'),mode=s['mode'],layers=s['layers'],conditions=s['conditions'],initial_values=[x[3] for x in s['conditions']],sprites=sprites,programs=s['scripts'],commands=commands,command_count=len(commands),opcode_counts={str(k):v for k,v in sorted(counts.items())},movies=s['movies'],mouse_rects=s['mouse_rects'],sounds=s['sounds'],intro_sound_id=s['intro_sound_id'],audio=audio,source_references=refs,prior_original_probe=dict(path=str(probe),sha256=hashlib.sha256(probe.read_bytes()).hexdigest(),consulted_as_text_only=True,evidence_path=str(prior),evidence_sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),original_callbacks=['3:15fd _fxm_set_idplanet','3:2036 _fxm_move_idplanet','4:2427..2664 custom12']),corrections=['Opcode39 randomly chooses an unset mask bit and consumes RNG; it is not an external-image command','No opcode20/49 or movie/external-picture work in P518 original scripts','Four locals have initial values0,0,1,0 from raw field3','Clones19..32 inherit ONLY sprite7 frames; own flags/xy remain independent'],script_graph=dict(startup=[0,1,2],speed_controls={'5':'decrement/clamp0 then queue program0','6':'increment/clamp15 then queue program0'},release_control={'8':'if setting>0 custom12release; correctcount9 completion6500ms+exit2000ms; count8 random after5000ms+follow; otherwise positive setting random after500ms+follow; unlock200ms'},recurring_poll=False),future_state=dict(sprite_words=29,base_sprite_words=27,extra_fields=['planetMotion','planetPeriod'],full_sprite_count=32,runner_words=605,header_proposal_words=10,proposed_payload_bytes=6184,format_assigned=False),requirements=['Admit scriptsIdle with active launcher/follow/released/frame-animation work; do not equate idle with noflight','Retain all32 own sprite records, both extra motion fields, complete RNG605, mask/count/selected/settings, clock/count/audio/dormantvariant/comet','Do not infer count from landed planets or popcount(mask); correctcount increments on release, wrongbit clears only on arrival','Native rapid-launch/full-mask audit is required before strengthening reachability validation','With available0 opcode39 still consumes RNG but leaves selectedid unchanged; subsequent follow may reattach just-released object','Stopped hidden wrong planets keep planetMotion2, planetPeriod-1, selectedframe/frameepoch/autoframe,coords,storedid and setting; correct arrivals retainvisibility','Follow proposed point uses old velocity before copying launcher delta; release preserves actual period/epoch and stores setting separately','Rebuild trusted bindings through original scene, never serialize callbacks or pending code'],unknowns=['No native boundary/save roundtrip or fresh-process verification performed by this static inventory','Exact concurrent-flight/full-mask histories need an independent native diagnostic before a restrictive validator','No format version assigned and no save support claim','Prior original probe assertions were not rerun; no original Win16 application runtime executed'])
args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2));print(json.dumps(dict(source=report['source'],commands=len(commands),opcodes=report['opcode_counts'],proposed_payload_bytes=6184),indent=2))
