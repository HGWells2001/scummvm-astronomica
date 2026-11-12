"""Review original backlog facts and exact real-loop/compatibility gates before installation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from click_backlog_source_nov12b import baseline,production
from p512_memory_refusal_source_nov12f import inject as clock_observer
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(w/'p512-segment-replay-seal-nov12-status.json');base=Path(old['snapshot'])/'engine/astronomica';stage=w/'click-backlog-candidate-nov12b-stage';src=stage/'source/engines/astronomica';build=read(stage/'proof.json');pin=build['candidate_exe_sha256']
for role,transform in [('candidate',production),('baseline',baseline)]:
 s=w/('click-backlog-'+role+'-nov12b-stage');cpp,h=transform((base/'astronomica.cpp').read_text(),(base/'astronomica.h').read_text());assert cpp==(s/'source/engines/astronomica/astronomica.cpp').read_text() and h==(s/'source/engines/astronomica/astronomica.h').read_text();assert read(s/'proof.json')['base_exe_sha256']==old['exe_sha256']
 audit=read(w/('click-backlog-'+role+'-source-review-nov12b.json'));assert audit['fresh_translation_units']==audit['archive_members_checked']==7 and audit['verified_reused_framework_objects']==403 and audit['engine_class_layout_unchanged'] and audit['save_layouts_unchanged'] and audit['private_methods_only']
cpp,script=clock_observer((src/'astronomica.cpp').read_text(),(src/'script.cpp').read_text());assert cpp==(w/'click-backlog-p512-clock-nov12-stage/source/engines/astronomica/astronomica.cpp').read_text() and script==(w/'click-backlog-p512-clock-nov12-stage/source/engines/astronomica/script.cpp').read_text()
names=['click-backlog-candidate-source-review-nov12b.json','click-backlog-baseline-source-review-nov12b.json','click-backlog-native-nov12b/proof.json','click-backlog-physical-saves-native-nov12/proof.json','click-backlog-genuine-nov12/proof.json','click-backlog-p512-clock-native-nov12/proof.json']
items={name:read(w/name)for name in names};assert all(v['status'].endswith('PASS')for v in items.values())
assert items[names[0]]['candidate_exe_sha256']==items[names[2]]['candidate_exe_sha256']==items[names[3]]['candidate_exe_sha256']==items[names[4]]['consumer_exe_sha256']==items[names[5]]['shipping_candidate_exe_sha256']==sha(stage/'bin/scummvm.exe')==pin
native=items[names[2]];assert len(native['cases'])==3 and native['all_processes_exited_naturally']
for row in native['cases']:
 assert row['cases']==12 and row['keyboard_menu_and_quit_preserved']
 assert row['differences_from_first_click']==(12 if row['role']=='baseline'else 0)
assert len(items[names[3]]['cases'])==4 and items[names[4]]['fresh_processes']==4
original=read(w/'original-mouse-backlog-nov12/proof.json');assert original['status']=='ORIGINAL_MOUSE_BACKLOG_REMOVAL_INVENTORY_PASS'
result=dict(status='CLICK_BACKLOG_ORIGINAL_QUEUE_AND_NATIVE_REVIEW_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,previous_exe_sha256=old['exe_sha256'],baseline_diagnostic_exe_sha256=native['baseline_diagnostic_exe_sha256'],class_layout_unchanged=True,private_nonvirtual_method_added=True,core_and_save_schemas_unchanged=True,original_queue_evidence_sha256=sha(w/'original-mouse-backlog-nov12/proof.json'),evidence_sha256={name:sha(w/name)for name in names},exact_optional_clock_observer_recovered=True,limits=['Original do_mouse drains queued window messages before handling the current click;ScummVM adapts the mouse backlog while retaining host keys/menu/quit','Actual extracted production poll loop baseline/candidate,12original P536bursts/100globals/13locals per profile,including Windows;candidate matches single-click reference in every case','No fields,class layout,core or save-schema changes;all7engine units fresh/403foundation verified','Four old ASVM2/26/27roundtrips,four genuine ASVM29fresh continuations and all12P512end-minus8futures PASS','Separate full general on exact candidate still required before promotion','Old failed general remains untouched;no original Windows runtime/global P536reachability/whole-game completion claim'])
(w/'click-backlog-review-nov12.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
