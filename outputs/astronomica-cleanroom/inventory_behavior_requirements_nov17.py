"""Version candidate behavioral requirements and attach exact historical native observations.

The report leaves reachability,action completion,current-engine behavior and
native-callback catalogue completeness open. Original bytes are independently
rechecked before any historical trace is attached to an original command.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json,subprocess,sys,traceback
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();w=a.workspace.resolve();out=a.out.resolve();out.mkdir(exist_ok=False,parents=True)
here=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 inventory=w/'original-branches-nov6/inventory.json';trace=w/'command-trace-text-map-nov13/proof.json';general=w/'command-trace-general-nov12c/proof.json';log=w/'command-trace-general-nov12c/general-native.log'
 subprocess.run([sys.executable,str(here/'verify_original_branches_nov6.py'),str(a.root),str(inventory),'--proof',str(out/'original-byte-proof.json')],check=True)
 inv=read(inventory);mapping=read(trace);native=read(general)
 assert mapping['status']=='COMMAND_TRACE_TEXT_HASH_ENTRANCE_RESULT_MAP_PASS' and native['status']=='COMMAND_TRACE_GENERAL_NATIVE_PASS'
 assert mapping['syntax_inventory_sha256']==sha(inventory) and mapping['general_proof_sha256']==sha(general)
 assert mapping['native_log_sha256']==native['log_sha256']==sha(log)
 assert mapping['diagnostic_exe_sha256']==native['candidate_exe_sha256'] and mapping['ambiguous_source_alias_signatures']==0
 commands={c['id']:c for c in inv['commands']};observations={}
 for row in mapping['mapping']:
  assert not row['action_completed_inferred'] and not row['human_route_inferred']
  assert len(row['source_command_ids'])==1;id=row['source_command_ids'][0];assert id in commands and id not in observations;c=commands[id]
  assert (c['scene'],c['file_offset'],c['opcode'],c['delay_ms'])==(row['scene'],row['file_offset'],row['opcode'],row['delay_ms'])
  text=[arg for arg in c['args']if isinstance(arg,dict)];numeric=[arg for arg in c['args']if not isinstance(arg,dict)]
  assert numeric==row['args'] and len(text)<=1
  if text:
   assert row['text_hex']!='-';raw=bytes.fromhex(row['text_hex']);assert len(raw)==text[0]['text_length'] and hashlib.sha256(raw).hexdigest()==text[0]['text_sha256']
  else:assert row['text_hex']=='-'
  results=row['condition_results_observed'];assert all(v in(0,1)for v in results)
  assert set(results)=={r['result']for r in row['condition_result_lines']}
  assert all(v>0 for v in row['entrance_log_lines']) and all(r['line']>0 for r in row['condition_result_lines'])
  observations[id]=dict(entrance_lines=row['entrance_log_lines'],predicate_result_lines=row['condition_result_lines'],predicate_results=results)
 assert len(observations)==mapping['unique_source_command_ids']==7424
 requirements=[]
 def add(kind,key,c=None,desired=None,**extra):
  prior=observations.get(c['id'],{})if c else{}
  predicate_lines=[r['line']for r in prior.get('predicate_result_lines',[])if r['result']==desired]if desired is not None else[]
  item=dict(id=kind+':'+key,kind=kind,original_command_id=c['id']if c else None,scene=c['scene']if c else extra.get('source_scene'),file_offset=c['file_offset']if c else None,reachability='UNCLASSIFIED',current_behavior_verified=False,action_completion_verified=False,historical_native_entrance_observed=bool(prior),historical_predicate_outcome_observed=bool(predicate_lines),historical_evidence=dict(entrance_lines=prior.get('entrance_lines',[]),predicate_outcome_lines=predicate_lines),**extra)
  if desired is not None:item['desired_predicate_result']=desired
  requirements.append(item)
 for c in inv['commands']:
  if c['opcode']==31:
   for desired in(0,1):add('predicate_outcome',c['id']+':'+str(desired),c,desired)
  if c['opcode']==45:add('alternative_continuation',c['id'],c,condition_link='NOT_INFERRED_FROM_NESTING')
  if c['delay_ms']>0:add('timed_dispatch',c['id'],c,delay_ms=c['delay_ms'],timing_verified=False)
  if c['opcode']==23:add('custom_dispatch_effects',c['id'],c,selector=c['args'][0],native_effects_verified=False)
 for index,route in enumerate(inv['route_references']):
  c=commands.get(route.get('command'));add('literal_route_outcome',str(index),c,source_scene=route['source'],route_kind=route['kind'],destination_outcome_verified=False)
 assert len({r['id']for r in requirements})==len(requirements)
 counts=collections.Counter(r['kind']for r in requirements);assert counts['predicate_outcome']==2784 and counts['alternative_continuation']==915 and counts['timed_dispatch']==1593 and counts['literal_route_outcome']==1124
 predicate_rows=[r for r in requirements if r['kind']=='predicate_outcome'];historical=sum(r['historical_predicate_outcome_observed']for r in predicate_rows)
 assert historical==mapping['conditions_with_results']+mapping['conditions_with_both_results']==1688
 by_scene=collections.defaultdict(collections.Counter)
 for r in requirements:by_scene[r['scene']if r['scene']is not None else r['source_scene']][r['kind']]+=1
 detail=dict(schema_version=1,status='CANDIDATE_BEHAVIOR_REQUIREMENTS_WITH_HISTORICAL_OBSERVATIONS',requirements=requirements,unbounded_catalogue_gaps=['Native callbacks and callback-generated queues outside literal HYP dispatches','Required failure/success/timed route outcomes and their reachability','Human complete audiovisual traversal'],historical_diagnostic_exe_sha256=mapping['diagnostic_exe_sha256'])
 local=out/'requirements-local.json';local.write_text(json.dumps(detail,indent=2)+'\n')
 receipt=dict(status='VERSIONED_BEHAVIOR_CANDIDATE_REQUIREMENTS_PASS',schema_version=1,at=datetime.now(timezone.utc).isoformat(),syntax_inventory_sha256=sha(inventory),fresh_original_byte_proof_sha256=sha(out/'original-byte-proof.json'),historical_trace_map_sha256=sha(trace),historical_general_proof_sha256=sha(general),historical_native_log_sha256=sha(log),historical_diagnostic_exe_sha256=mapping['diagnostic_exe_sha256'],historical_recorded_shipping_exe_sha256=mapping['shipping_exe_sha256'],original_files=421,readable_scene_prefixes=420,original_commands=10316,original_script_lists=936,matched_historical_command_entrances=len(observations),candidate_requirements_by_kind=dict(counts),candidate_requirements=len(requirements),predicate_outcome_cells=2784,historical_controlled_native_predicate_cells_observed=historical,predicate_cells_without_this_historical_observation=2784-historical,per_scene_counts={str(k):dict(v)for k,v in sorted(by_scene.items())},local_detail_sha256=sha(local),author_sha256=sha(Path(__file__)),engine_modified=False,acceptance_A03_complete=False,whole_game_completion_percent=None,limits=['Candidate syntax-derived requirements; reachability and required behavioral outcomes are not yet classified','Historical observations retain their original diagnostic executable identity and do not certify the current engine','Entrances and predicate results do not establish successful action completion,route outcomes or original Windows behavior','Alternative markers remain unlinked; no nested-if or inferred route model is introduced','Native callback/generated-queue catalogue remains open; per-command detail stays local','No completion percentage is inferred from these counts'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],dict(counts),'historical predicate cells',historical)
except Exception:
 (out/'failure.json').write_text(json.dumps(dict(status='FAILED',error=traceback.format_exc()),indent=2)+'\n');raise
