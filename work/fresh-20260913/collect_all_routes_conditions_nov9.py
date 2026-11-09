"""Map completed native general-suite traces conservatively to original commands."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,re
w=Path(__file__).resolve().parent;folder=w/'all-routes-condition-general-nov9';out=folder/'observations';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
native=read(folder/'proof.json');assert native['status']=='ALL_ROUTES_CONDITION_GENERAL_NATIVE_PASS'
stage=w/'builder-default-condition-nov9-stage';build=read(stage/'proof.json');seal=read(w/'builder-mask-guard-seal-nov9-status.json')
assert sha(stage/'bin/scummvm.exe')==native['candidate_exe_sha256']==build['candidate_exe_sha256']
source=stage/'source/engines/astronomica'
assert sha(source/'script.cpp')==build['trace_script_sha256'] and sha(source/'astronomica.cpp')==build['candidate_astronomica_sha256']
for n,h in seal['engine_sha256'].items():
 if n not in ('astronomica.cpp','script.cpp'):assert sha(source/n)==h
log=folder/'general-native.log';assert sha(log)==native['log_sha256']
inventory=read(w/'original-branches-nov6/inventory.json');by_signature=collections.defaultdict(list)
for c in inventory['commands']:
 if c['opcode']==31:by_signature[(c['file_offset'],*c['args'][:5])].append(c)
pattern=r'Astronomica condition trace: offset=(\d+) scope=(-?\d+) id=(-?\d+) value=(-?\d+) low=(-?\d+) high=(-?\d+) cmp=(-?\d+) result=(\d+)'
unique={};unassigned=collections.Counter();total=0;matched=0
for line in log.read_text(errors='replace').splitlines():
 m=re.search(pattern,line)
 if not m:continue
 offset,scope,ident,value,low,high,comparison,result=map(int,m.groups());total+=1
 candidates=by_signature[(offset,scope,ident,low,high,comparison)]
 # General verifiers can hold copied runners without a new loadPlace log.
 # A last-seen scene would therefore be insufficient evidence of ownership.
 if len(candidates)!=1:
  unassigned['ambiguous' if candidates else 'unmapped']+=1;continue
 c=candidates[0];expected=value==low if comparison==0 else value<low if comparison==1 else value>low if comparison==2 else low<=value<=high
 assert bool(result)==expected
 row=dict(scene=c['scene'],offset=offset,original_id=c['id'],scope=scope,id=ident,value=value,low=low,high=high,comparison=comparison,result=bool(result))
 key=(c['id'],value,bool(result));unique.setdefault(key,dict(**row,visits=0))['visits']+=1;matched+=1
observations=list(unique.values());assert observations and total==matched+sum(unassigned.values())
paths={s['scene']:s for s in inventory['scenes']};assets={}
for place in set(x['scene'] for x in observations):
 s=paths[place];p=Path('D:/astro')/s['path'];assert sha(p)==s['sha256'];assets[str(place)]=s['sha256']
(out/'observations-local.json').write_text(json.dumps(observations,indent=2)+'\n')
p=dict(status='REAL_ORIGINAL_ASSET_CONDITION_TRACE_OBSERVATION_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=native['candidate_exe_sha256'],general_native_proof_sha256=sha(folder/'proof.json'),native_log_sha256=sha(log),observations=len(observations),raw_trace_evaluations=total,uniquely_assigned_evaluations=matched,excluded_assignment_counts=dict(unassigned),scenes=sorted(set(x['scene'] for x in observations)),original_asset_sha256=assets,local_observations_sha256=sha(out/'observations-local.json'),trace_only_candidate_installed=False,limits=['Only globally unique original offset-plus-operand signatures assigned; ambiguous and unknown signatures explicitly excluded','Equal source position/value/result observations deduplicated, retaining visit counts; instruction verifier checks unique cases','Existing full general native verifier; some copied owner states are controlled verifier states, not a human gameplay history','No original Windows execution or full-game coverage claim'])
(out/'proof.json').write_text(json.dumps(p,indent=2)+'\n');print('General native trace observations ready:',len(observations),'unique cases from',total,'evaluations;',dict(unassigned))
