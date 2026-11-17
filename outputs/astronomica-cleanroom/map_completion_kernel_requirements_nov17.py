"""Attach bounded historical native completion effects to versioned original requirements."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json,re,struct,traceback
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();w=a.workspace.resolve();out=a.out.resolve();out.mkdir(exist_ok=False,parents=True)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 syntax=w/'original-branches-nov6/inventory.json';requirements=w/'original-behavior-requirements-nov17';native_dir=w/'success-effects-native-nov10';oracle_dir=w/'original-success-effects-nov10';stage=w/'success-effects-nov10-stage'
 inv=read(syntax);catalog=read(requirements/'requirements-local.json');catalog_proof=read(requirements/'proof.json');native=read(native_dir/'proof.json');oracle=read(oracle_dir/'proof.json');build=read(stage/'proof.json')
 assert catalog_proof['status']=='VERSIONED_BEHAVIOR_CANDIDATE_REQUIREMENTS_PASS' and catalog_proof['local_detail_sha256']==sha(requirements/'requirements-local.json')
 assert catalog_proof['syntax_inventory_sha256']==oracle['inventory_sha256']==sha(syntax)
 assert native['status']=='ORIGINAL_COMPLETION_REAL_ENGINE_CALLBACK_EFFECTS_PASS' and native['oracle_proof_sha256']==sha(oracle_dir/'proof.json') and native['build_proof_sha256']==sha(stage/'proof.json')
 assert native['candidate_exe_sha256']==build['candidate_exe_sha256']==sha(stage/'bin/scummvm.exe')
 assert sha(stage/'source/engines/astronomica/astronomica.cpp')==build['candidate_engine_sha256']['astronomica.cpp']
 assert sha(a.root/'SETUP/ASTRO.EXE')==oracle['original_exe_sha256']=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
 fixture=oracle_dir/'fixture.bin';log=native_dir/'native.log';assert sha(fixture)==oracle['fixture_sha256']==native['fixture_sha256'] and sha(log)==native['native_log_sha256']
 commands={(c['scene'],c['file_offset']):c for c in inv['commands']if c['opcode']==23 and c['args']==[25,0,0,0,0,0]};assert len(commands)==30
 required={r['original_command_id']:r['id']for r in catalog['requirements']if r['kind']=='custom_dispatch_effects'};assert len(required)==158
 raw=fixture.read_bytes();assert raw[:8]==b'SCFX0001';cases=struct.unpack_from('<I',raw,8)[0];assert cases==300;at=12;expected={};detail=[];seen=set();by_scene=collections.Counter()
 for case in range(cases):
  scene,offset,counter,repeats=struct.unpack_from('<4I',raw,at);at+=16;assert repeats==2 and(scene,offset)in commands
  initial=raw[at:at+400];assert len(initial)==400;at+=400;c=commands[scene,offset];assert c['id']in required
  original=(a.root/f'PLACES/P{scene}/MEGAFILE.HYP').read_bytes();assert hashlib.sha256(original).hexdigest()==next(s['sha256']for s in inv['scenes']if s['scene']==scene)
  assert struct.unpack_from('<7i',original,offset)==(23,25,0,0,0,0,0)
  seen.add(c['id']);by_scene[scene]+=1
  for repeat in range(repeats):
   after,voices,voice_counter,voice_hash=struct.unpack_from('<4I',raw,at);at+=16;globals_after=raw[at:at+400];assert len(globals_after)==400 and voices<=1;at+=400
   expected[case,repeat]=dict(scene=scene,source=offset,counter=after,voices=voices,voice_counter=voice_counter,voice_hash=voice_hash)
   detail.append(dict(requirement_id=required[c['id']],original_command_id=c['id'],case=case,repeat=repeat,scene=scene,original_source_offset=offset,initial_counter=counter,initial_globals_sha256=hashlib.sha256(initial).hexdigest(),expected_final_globals_sha256=hashlib.sha256(globals_after).hexdigest(),expected_counter=after,expected_voices=voices,historical_kernel_effects_verified=False,current_behavior_verified=False,natural_reachability='UNCLASSIFIED',resource_delay_normalized_to_minus1=True))
 assert at==len(raw) and len(expected)==600 and len(seen)==25 and set(by_scene)==set(native['scenes'])==set(oracle['scenes'])
 current=None;begun=set();passed={};voices={key:[]for key in expected}
 for line_no,line in enumerate(log.read_text(errors='replace').splitlines(),1):
  m=re.search(r'Custom effects begin: case(\d+) repeat(\d+) scene(\d+) source(\d+) expectedvoices(\d+) voicecounter(\d+) voicehash([0-9a-f]+)',line)
  if m:
   current=int(m[1]),int(m[2]);assert current in expected and current not in begun;begun.add(current);e=expected[current]
   assert (int(m[3]),int(m[4]),int(m[5]),int(m[6]),int(m[7],16))==(e['scene'],e['source'],e['voices'],e['voice_counter'],e['voice_hash']);continue
  m=re.search(r'Custom effects voice: counter(\d+) hash([0-9a-f]+) sound(\d+)',line)
  if m:assert current is not None;voices[current].append((int(m[1]),int(m[2],16),int(m[3]),line_no));continue
  m=re.search(r'Custom effects result: PASS case(\d+) repeat(\d+) scene(\d+) counter(\d+) voices(\d+)',line)
  if m:
   key=int(m[1]),int(m[2]);assert key==current and key not in passed;e=expected[key]
   assert (int(m[3]),int(m[4]),int(m[5]))==(e['scene'],e['counter'],e['voices']);passed[key]=line_no
 assert begun==set(passed)==set(expected)
 for row in detail:
  key=row['case'],row['repeat'];e=expected[key];actual=voices[key]
  assert len(actual)==e['voices']
  if e['voices']:assert [v[:3]for v in actual]==[(e['voice_counter'],e['voice_hash'],912)]
  row.update(historical_kernel_effects_verified=True,native_pass_log_line=passed[key],native_voice_log_lines=[v[3]for v in actual])
 assert sum(map(len,voices.values()))==native['actual_blocking_voices']==oracle['voice_calls']==44
 local=out/'kernel-requirements-local.json';local.write_text(json.dumps(dict(schema_version=1,rows=detail,historical_diagnostic_exe_sha256=native['candidate_exe_sha256']),indent=2)+'\n')
 receipt=dict(status='HISTORICAL_COMPLETION_KERNEL_REQUIREMENT_MAP_PASS',schema_version=1,at=datetime.now(timezone.utc).isoformat(),behavior_catalogue_sha256=sha(requirements/'proof.json'),syntax_inventory_sha256=sha(syntax),historical_native_proof_sha256=sha(native_dir/'proof.json'),historical_oracle_proof_sha256=sha(oracle_dir/'proof.json'),historical_native_log_sha256=sha(log),historical_native_exe_sha256=native['candidate_exe_sha256'],historical_native_cpp_sha256=build['candidate_engine_sha256']['astronomica.cpp'],original_exe_sha256=oracle['original_exe_sha256'],fixture_sha256=sha(fixture),custom_dispatch_candidate_requirements=158,custom25_source_commands=30,representative_source_requirements_linked=len(seen),same_selector_other_source_instances_not_inferred=5,controlled_cases=300,historical_native_invocations_rechecked=600,blocking_voice_boundaries_rechecked=44,per_scene_controlled_cases={str(k):v for k,v in sorted(by_scene.items())},local_detail_sha256=sha(local),author_sha256=sha(Path(__file__)),engine_modified=False,acceptance_A03_complete=False,whole_game_completion_percent=None,limits=['Historical isolated custom25 semantics with controlled globals/counter and normalized delay; original OS voice boundary modeled','Actual native callback and100-global comparisons belong to the pinned older diagnostic executable','Original resource source offsets are mapped explicitly; five other same-selector command instances are not relabeled as observed','No natural gameplay reachability,timing,current-engine equivalence,complete native callback inventory or whole-game claim','Full per-case fixture/global detail remains local'])
 (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],'source requirements',len(seen),'historical invocations',len(expected),'voice boundaries',sum(map(len,voices.values())))
except Exception:
 (out/'failure.json').write_text(json.dumps(dict(status='FAILED',error=traceback.format_exc()),indent=2)+'\n');raise
