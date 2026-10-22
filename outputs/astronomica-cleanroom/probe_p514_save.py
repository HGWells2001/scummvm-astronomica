"""Read only original P514 resource inventory; no target/callback/runtime execution."""
from pathlib import Path
import argparse,collections,hashlib,json,sys,wave
sys.dont_write_bytecode=True
here=Path(__file__).resolve().parent
cleanroom=here if (here/'astro_reader.py').is_file() else here.parents[2]/'outputs/astronomica-cleanroom'
sys.path.insert(0,str(cleanroom))
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,default=here/'evidence/p514-save-original.json');args=ap.parse_args()
p=args.root/'PLACES/P514/MEGAFILE.HYP';raw=p.read_bytes();d=parse(raw)
assert d['size']==d['consumed']==586435 and d['mode']==0 and d['layers']==1
assert d['conditions']==[[1,0,20,0,0,19],[1,1,19,-1,0,18],[1,2,2,0,0,2],[1,3,52,54,0,52],[1,4,1,1,1,1],[1,5,16,0,0,15],[1,6,16,0,0,15],[1,7,1,0,0,1]]
assert len(d['sprites'])==20 and len(d['scripts'])==2 and not d['movies'] and not d['mouse_rects']
sprites=[]
for i,s in enumerate(d['sprites']):
 owner=i;seen=set()
 while d['sprites'][owner]['clone']!=-1:
  assert owner not in seen;seen.add(owner);owner=d['sprites'][owner]['clone']-1;assert 0<=owner<i
 frames=d['sprites'][owner]['frames'];row={k:v for k,v in s.items() if k!='frames'}
 row.update(id=i+1,frame_owner=owner+1,frame_count=len(frames),dimensions=sorted({(f[0]['width'],f[0]['height']) for f in frames}));sprites.append(row)
assert [s['frame_count'] for s in sprites]==[2]*6+[16]+[10]*6+[1,2,2,1,3,12,1]
assert [s['id'] for s in sprites if s['clone']!=-1]==[9,10,11,12,13]
assert not any(s['auto_frame'] or s['auto_move'] or s['drag_enabled'] or s['mouse_in'] or s['mouse_out'] for s in sprites)
commands=[]
def walk(v,path):
 if isinstance(v,dict):
  if 'opcode' in v:commands.append(dict(path=path,**v))
  for k,x in v.items():walk(x,path+'/'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):walk(x,path+'/'+str(i))
walk(d,'scene');counts=collections.Counter(c['opcode'] for c in commands)
assert not any(counts[n] for n in (3,20,39,49))
custom=[c for c in commands if c['opcode']==23];assert sorted(c['args'][:2] for c in custom)==[[16,0],[16,1],[16,2],[16,3],[25,0]]
assert [c['args'] for c in commands if c['opcode']==41]==[[1],[1]]
refs={}
for name,anchors in {'sprites.cpp':['void configureRendezvous(','bool advanceRendezvous('],'astronomica.cpp':['bool AstronomicaEngine::onRendezvous(','_runner.setRendezvousHandler(','bool AstronomicaEngine::verifyP514Puzzle()'],'script.cpp':['case 514: return 30;','_rendezvousHandler->onRendezvous('],'resource.h':['uint32 frameSince','uint32 moveSince','int32 orbitSideX']}.items():
 f=cleanroom/'engine/astronomica'/name;content=f.read_bytes();lines=content.decode().splitlines();refs[name]=dict(sha256=hashlib.sha256(content).hexdigest(),anchors={a:next(i+1 for i,l in enumerate(lines) if a in l) for a in anchors})
audio=[]
for f in sorted(p.parent.glob('*.WAV')):
 with wave.open(str(f),'rb') as w:meta=dict(channels=w.getnchannels(),sample_rate=w.getframerate(),sample_width=w.getsampwidth(),frames=w.getnframes(),seconds=w.getnframes()/w.getframerate())
 audio.append(dict(name=f.name,size=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),**meta))
h=2166136261
for b in raw:h=((h^b)*16777619)&0xffffffff
prior=cleanroom/'probe_p514_motion.py'
report=dict(status='PASS',evidence_id='p514-save-original-static-20261022',scope='Static original HYP/WAV inventory and post-13-September native source review only; no original runtime, native engine or callback probe executed',source=dict(path=str(p),size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),fnv1a32=f'{h:08x}'),mode=d['mode'],layers=d['layers'],background=d['background'],control=d['control'],conditions=d['conditions'],initial_values=[c[3] for c in d['conditions']],sprites=sprites,programs=d['scripts'],sounds=d['sounds'],intro_sound_id=d['intro_sound_id'],audio=audio,movies=d['movies'],mouse_rects=d['mouse_rects'],command_count=len(commands),opcode_counts={str(k):v for k,v in sorted(counts.items())},commands=commands,custom=custom,source_references=refs,original_callback_probe=dict(path=str(prior),sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),consulted_as_text_only=True,original_addresses=['3:3755 region','4:366e..385b collision'],prior_claims_not_rerun=['Two 1000-step ellipse trajectories','17161 region cases','224 collision cases']),contract_observations=['UI speed local5 has sixteen settings0..15; four custom16 modes are not four UI settings','No recurring poll; program1 is queued only by speed controls and also runs at startup','Eight original locals retain signed initial-1 and initial54 despite raw width52; do not interpret widths as value maxima','Twenty own sprite records preserve cloned coordinates/flags and hidden sprite20 collision side effect','Rendezvous has no separate motion struct: native persistent motion resides in sprites and eight locals','Settled script queue can coexist with active target/ship/fuel animations','Successful custom16 cancels other pending programs, sets local6 and leaves own delayed continuation; pending success excluded from initial contract'],unknowns=['No dedicated native boundary audit, save format, save roundtrip or fresh-process proof performed here','Precise complete reachable dynamic phase invariants need native observation and original control routes','Native audio end, clock wrap and malformed payload atomicity remain untested in this static inventory','No original application runtime claim; Win16NE provider unsupported and not retried'])
args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ('source','initial_values','command_count','opcode_counts')},indent=2))

