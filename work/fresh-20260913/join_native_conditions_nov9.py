"""Reproduce the scalar/live outcome join from hash-pinned local observations."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json
w=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--include-general',action='store_true');a=ap.parse_args()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin=read(w/'original-scene-scalars-nov7/proof.json');invpath=w/'original-branches-nov6/inventory.json';assert sha(invpath)==pin['inventory_sha256']
inventory=read(invpath);ids={c['id']:c for c in inventory['commands']};keys={}
for s in inventory['scenes']:
 for ordinal,script in enumerate(s['scripts']):
  for i,index in enumerate(script['command_indices']):keys[(s['scene'],ordinal,i)]=inventory['commands'][index]['id']
groups=[('builder','condition-trace-nov9-stage/builder-run'),('endings','condition-trace-nov9-stage/endings-run'),('transitions','condition-trace-nov9-stage/transitions-run'),('game-state','condition-trace-nov9-stage/game-state-run'),('p510-start','p510-start-condition-nov9-stage/native-run')]
groups.append(('builder-default','builder-default-condition-nov9-stage/native-run'))
if a.include_general:groups.append(('general','all-routes-condition-general-nov9/observations'))
seen=collections.defaultdict(collections.Counter);evidence={};cases=0;raw=0
for label,folder in groups:
 folder=w/folder;proof=w/f'live-{label}-original-predicates-nov9/proof.json';p=read(proof);native=read(folder/'proof.json');obs=folder/'observations-local.json'
 assert p['status']==('LIVE_BUILDER_ORIGINAL_PREDICATE_COMPARISON_PASS' if label=='builder' else 'LIVE_ORIGINAL_ASSET_PREDICATE_COMPARISON_PASS')
 assert sha(obs)==p['observations_sha256']==native['local_observations_sha256'] and sha(folder/'proof.json')==p['observation_proof_sha256']
 rows=read(obs);assert len(rows)==p['observations']==native['observations']
 for row in rows:
  c=ids[row['original_id']];assert c['opcode']==31 and c['scene']==row['scene'] and c['file_offset']==row['offset']
  assert c['args'][:5]==[row['scope'],row['id'],row['low'],row['high'],row['comparison']]
  seen[c['id']][row['result']]+=row.get('visits',1)
 cases+=len(rows);raw+=sum(x.get('visits',1) for x in rows)
 evidence[label]=dict(observations_sha256=sha(obs),instruction_comparison_sha256=sha(proof),cases=len(rows),accepted_native_evaluations=sum(x.get('visits',1)for x in rows))
baseline=w/'scalar-branch-coverage-nov7/condition-outcomes-local.json';rows=read(baseline)
assert len(rows)==1392;categories=collections.Counter();resolved=0;detail=[]
for row in rows:
 ident=keys[(row['scene'],row['script'],row['command'])];n=seen[ident]
 t=row['true_visits']+n[True];f=row['false_visits']+n[False]
 category='both'if t and f else'true_only'if t else'false_only'if f else'unvisited';categories[category]+=1
 if row['category']=='unvisited' and category!='unvisited':resolved+=1
 detail.append(dict(scene=row['scene'],script=row['script'],command=row['command'],original_id=ident,category=category,matrix_true=row['true_visits'],matrix_false=row['false_visits'],native_true=n[True],native_false=n[False]))
a.out.mkdir(exist_ok=False);(a.out/'condition-outcomes-local.json').write_text(json.dumps(detail,indent=2)+'\n')
j=dict(status='NATIVE_ROUTE_AND_ORIGINAL_PREDICATE_COVERAGE_JOIN_PASS',completed_at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),baseline_sha256=sha(baseline),inventory_sha256=sha(invpath),instruction_compared_cases=cases,accepted_native_evaluations=raw,original_condition_positions=len(rows),previous_unvisited=sum(x['category']=='unvisited'for x in rows),newly_observed=resolved,combined_categories=dict(categories),remaining_unvisited=[{k:x[k]for k in('scene','script','command')}for x in detail if x['category']=='unvisited'],groups=evidence,local_details_sha256=sha(a.out/'condition-outcomes-local.json'),whole_game_completion_percent=None,limits=['Reduced scalar matrix plus controlled real-engine observations; no complete required-gameplay scope','General native traces may include copied diagnostic states; only globally unique source signatures assigned','An unobserved outcome does not establish a defect or unreachable branch'])
(a.out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print('Verified outcome join:',dict(categories),'; unique observed-value cases',cases)
