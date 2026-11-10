"""Pin the still-unvisited P536 condition and surrounding original data.

This is source inventory, not a reachability proof or a gameplay implementation.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';sys.path.insert(0,str(o))
from astro_reader import parse
raw=Path('D:/astro/PLACES/P536/MEGAFILE.HYP').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)=='2427a16a916e53affdf0c7a7590f858f96492784d11eb1a7b3632b804e35d554'
s=parse(raw);script=s['sprites'][7]['click'];target=script[16]
assert target['offset']==350661 and target['opcode']==31 and target['args']==[1,2,4,0,0,0]
prefix=[dict(index=i,**c)for i,c in enumerate(script[:17])if c['opcode']in(31,41,45)]
assert [(x['index'],x['args'])for x in prefix if x['opcode']==31]==[(2,[1,2,4,0,1,0]),(5,[1,2,4,0,2,0]),(8,[1,1,3,0,2,0]),(16,[1,2,4,0,0,0])]
initial={str(c[1]):dict(width=c[2],value=c[3],low=c[4],high=c[5])for c in s['conditions']if c[0]==1}
assert initial['1']['value']==2 and initial['2']['value']==0 and initial['3']['value']==0 and initial['4']['value']==6
program_calls=[dict(index=i,program=c['args'][0],delay=c['delay'])for i,c in enumerate(script[:16])if c['opcode']==41];assert [x['program']for x in program_calls]==[2,0,6]
phase_writers=[];height_writers=[]
for sprite,sp in enumerate(s['sprites'],1):
 for index,c in enumerate(sp.get('click',[])):
  if c['opcode']==32 and c['args'][:2]==[1,2]:phase_writers.append(dict(sprite=sprite,index=index,value=c['args'][2],offset=c['offset']))
  if c['opcode']==32 and c['args'][:2]==[1,4]:height_writers.append(dict(sprite=sprite,index=index,value=c['args'][2],offset=c['offset']))
proof=dict(status='ORIGINAL_P536_UNVISITED_GATE_SOURCE_INVENTORY_PASS',verified_at=datetime.now(timezone.utc).isoformat(),source_hyp_sha256=sha(raw),reader_sha256=sha((o/'astro_reader.py').read_bytes()),author_sha256=sha(Path(__file__).read_bytes()),target=target,initial_locals=initial,prefix_tests_and_calls=prefix,queued_programs_before_target=program_calls,serialized_phase_writers=phase_writers,serialized_height_writers=height_writers,native_observed=False,unreachable_proven=False,defect_proven=False,limits=['Data extracted directly from original P536 resource using the cleanroom reader','No inference of whole-game completeness or natural reachability','Earlier condition outcomes alone are insufficient: delayed command/program41 scheduling and last-condition state require separate analysis','Initial local4 is6, not0; do not assume all default retained height fields start empty','Investigate original cap-validation local6 and program scheduling before constructing a natural UI path'])
(w/'p536-unvisited-gate-source-nov10.json').write_text(json.dumps(proof,indent=2)+'\n');print('Original P536 unresolved gate pinned; no reachability classification changed')
