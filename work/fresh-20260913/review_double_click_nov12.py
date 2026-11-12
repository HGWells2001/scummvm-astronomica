"""Bind original CS_DBLCLKS evidence to the exact real engine and bounded regressions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,time
from double_click_source_nov12 import baseline,production
from p512_memory_refusal_source_nov12f import inject as clock
from double_pair_batches_source_nov12 import inject as pair_batches
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(w/'click-backlog-seal-nov12-status.json');base=Path(old['snapshot'])/'engine/astronomica';stage=w/'double-click-candidate-nov12-stage';src=stage/'source/engines/astronomica';pin=read(stage/'proof.json')['candidate_exe_sha256']
for role,transform in [('candidate',production),('baseline',baseline)]:
 s=w/('double-click-'+role+'-nov12-stage');cpp,h=transform((base/'astronomica.cpp').read_text(),(base/'astronomica.h').read_text());assert cpp==(s/'source/engines/astronomica/astronomica.cpp').read_text() and h==(s/'source/engines/astronomica/astronomica.h').read_text()
 audit=read(w/('double-click-'+role+'-source-review-nov12.json'));assert audit['fresh_translation_units']==audit['archive_members_checked']==7 and audit['verified_reused_framework_objects']==403 and not audit['engine_class_layout_unchanged'] and audit['transient_mouse_pair_fields_added'] and audit['save_layouts_unchanged']
 assert read(s/'proof.json')['base_exe_sha256']==old['exe_sha256']
cpp,script=clock((src/'astronomica.cpp').read_text(),(src/'script.cpp').read_text());assert cpp==(w/'double-click-p512-clock-nov12-stage/source/engines/astronomica/astronomica.cpp').read_text() and script==(w/'double-click-p512-clock-nov12-stage/source/engines/astronomica/script.cpp').read_text()
mixed=w/'double-pair-batches-native-nov12'
while not(mixed/'proof.json').exists():
 if(mixed/'status.json').exists():assert read(mixed/'status.json')['status']!='FAILED'
 time.sleep(1)
names=['double-click-candidate-source-review-nov12.json','double-click-baseline-source-review-nov12.json','double-click-native-nov12/proof.json','double-click-physical-saves-native-nov12/proof.json','double-click-genuine-nov12/proof.json','double-click-p512-clock-native-nov12/proof.json','double-pair-batches-native-nov12/proof.json','double-pair-batches-source-review-nov12.json']
items={name:read(w/name)for name in names};assert all(j['status'].endswith('PASS')for j in items.values())
assert items[names[0]]['candidate_exe_sha256']==items[names[2]]['candidate_exe_sha256']==items[names[3]]['candidate_exe_sha256']==items[names[4]]['consumer_exe_sha256']==items[names[5]]['shipping_candidate_exe_sha256']==pin==sha(stage/'bin/scummvm.exe')
native=items[names[2]];assert len(native['cases'])==4 and native['baseline_double_actions_reproduced']==native['candidate_pairs_match_first_only']==native['candidate_third_click_is_new']==6 and native['accepted_backlog_and_host_controls_preserved'] and native['all_processes_exited_naturally']
assert len(items[names[3]]['cases'])==4 and items[names[4]]['fresh_processes']==4
assert items[names[6]]['shipping_candidate_exe_sha256']==pin and len(items[names[6]]['profiles'])==2
assert items[names[7]]['candidate_exe_sha256']==items[names[6]]['diagnostic_exe_sha256'] and items[names[7]]['archive_members_checked']==7
cpp,script=pair_batches((src/'astronomica.cpp').read_text(),(src/'script.cpp').read_text());assert cpp==(w/'double-pair-batches-nov12-stage/source/engines/astronomica/astronomica.cpp').read_text() and script==(src/'script.cpp').read_text()
original=read(w/'original-double-click-nov12/proof.json');assert original['status']=='ORIGINAL_DOUBLE_CLICK_CLASS_AND_DISPATCH_PASS' and original['class_style']==8
result=dict(status='DOUBLE_CLICK_ORIGINAL_CLASS_AND_NATIVE_REVIEW_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,previous_exe_sha256=old['exe_sha256'],engine_class_layout_changed=True,transient_mouse_pair_fields_added=3,all7engine_units_rebuilt=True,core_and_save_schemas_unchanged=True,original_evidence_sha256=sha(w/'original-double-click-nov12/proof.json'),evidence_sha256={name:sha(w/name)for name in names},exact_optional_clock_observer_recovered=True,limits=['Original main window class8=CS_DBLCLKS and handler ignores message515;static file/import evidence,not original Windows runtime','Normal gameplay pairs rapid nearby downs using the backend configured interval,500ms fallback and portable virtual tolerance ABS(dx/dy)<3;arbitrary historical host rectangle settings are not reconstructed','Three private derived UI fields are not serialized;class layout changes,all7engine objects rebuilt against403verified foundation objects','Six original P517 pairs compare100globals/two locals and gauge positions;third press is new,delayed/different-position clicks preserved,including Windows video','Accepted12P536batch comparisons and real keyboard/menu/quit remain PASS;four old ASVM2/26/27roundtrips,four genuine ASVM29continuations and12P512clock futures PASS','Exact full general still required before installation;intro/menu physical mouse history and physical hardware double-click trace not exhaustively tested','Old failed general remains untouched;no new whole-game percentage'])
(w/'double-click-review-nov12.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
