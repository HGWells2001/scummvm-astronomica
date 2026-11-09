"""Replay original predicates at values observed during actual native builder paths."""
from pathlib import Path
import collections,hashlib,json
template=Path(__file__).with_name('probe_original_scene_scalars_nov7.py')
w=Path('work/fresh-20260913').resolve();pin=json.loads((w/'original-scene-scalars-nov7/proof.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(template)==pin['author_sha256']
prefix=template.read_text().split('inventory=json.loads(a.inventory.read_text());',1)[0]
exec(compile(prefix,str(template),'exec'),globals())
folder=w/'condition-trace-nov9-stage/builder-run'
native=json.loads((folder/'proof.json').read_text());observations=folder/'observations-local.json'
assert native['status']=='REAL_BUILDER_CONDITION_TRACE_OBSERVATION_PASS'
assert digest(observations)==native['local_observations_sha256']
seen=collections.defaultdict(collections.Counter)
for row in json.loads(observations.read_text()):
    m=Machine();m.stack(6,4,ptr(0))
    for off in range(0x1832,0x187a):m.write(0x5000,off,1,exe[base(15)+off])
    m.write(0x2000,0x7a8,4,0x4000c000);m.write(0x2000,0xc88,4,0x4000d000)
    offset=(0xc00a if row['scope']==0 else 0xd3f8)+row['id']*4
    m.write(0x4000,offset,4,row['value'])
    args=[row['scope'],row['id'],row['low'],row['high'],row['comparison'],0]
    for n,value in enumerate(args):m.write(0x4000,(ptr(0)&65535)+4+n*4,4,value)
    m.run(execute,0xc70,0x1636,'predicate')
    actual=bool(m.read(0x2000,0x6a7,2));assert actual==row['result']
    seen[row['original_id']][actual]+=1
inventory=json.loads(a.inventory.read_text());keys={}
for scene in inventory['scenes']:
    for ordinal,script in enumerate(scene['scripts']):
        for i,index_ in enumerate(script['command_indices']):keys[scene['scene'],ordinal,i]=inventory['commands'][index_]['id']
baseline=json.loads((w/'scalar-branch-coverage-nov7/condition-outcomes-local.json').read_text())
resolved=[];combined=collections.Counter()
for row in baseline:
    key=keys[row['scene'],row['script'],row['command']];native_counts=seen[key]
    t=row['true_visits']+native_counts[True];f=row['false_visits']+native_counts[False]
    category='both'if t and f else'true_only'if t else'false_only'if f else'unvisited';combined[category]+=1
    if row['category']=='unvisited'and native_counts:
        resolved.append(dict(scene=row['scene'],script=row['script'],command=row['command'],native_true=native_counts[True],native_false=native_counts[False]))
a.out.mkdir(exist_ok=False,parents=True)
(a.out/'newly-observed-local.json').write_text(json.dumps(resolved,indent=2)+'\n')
proof=dict(status='LIVE_BUILDER_ORIGINAL_PREDICATE_COMPARISON_PASS',observations=native['observations'],
           original_exe_sha256=sha(exe),template_sha256=digest(template),author_sha256=digest(Path(__file__)),
           observation_proof_sha256=digest(folder/'proof.json'),observations_sha256=digest(observations),
           observed_distinct_conditions=sum(bool(v)for v in seen.values()),
           previously_unvisited_now_observed=len(resolved),combined_matrix_and_live_categories=dict(combined),
           executed_original_predicate_steps=sum(counts.values()),local_new_detail_sha256=digest(a.out/'newly-observed-local.json'),
           limits=['Actual native engine observed values compared with bounded original predicate instructions; not original Windows execution',
                   'Combined counts join reduced scalar cases with five real builder routes; they do not certify all gameplay',
                   'Temporary diagnostic candidate not installed; offsets/details and resources remain local'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Live builder/original predicate PASS:',proof['observations'],'evaluations,',len(resolved),'previous gaps observed,',dict(combined))
