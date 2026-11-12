"""Bind original full-voice comparison,cursor transition and new derived busy guard to exact source."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,time
from intro_menu_source_nov12c import production,baseline
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=read(w/'startup-defaults-seal-nov12-status.json');base=Path(old['snapshot'])/'engine/astronomica';candidate=w/'intro-menu-candidate-nov12c-stage';original=w/'intro-menu-baseline-nov12c-stage'
b=read(candidate/'proof.json');bb=read(original/'proof.json');a=read(w/'intro-menu-candidate-source-review-nov12c.json');ab=read(w/'intro-menu-baseline-source-review-nov12c.json');n=read(w/'intro-menu-native-nov12c/proof.json');files=read(w/'intro-menu-physical-saves-native-nov12c/proof.json');af=read(w/'intro-menu-physical-saves-source-review-nov12c.json')
assert b['base_exe_sha256']==bb['base_exe_sha256']==old['exe_sha256'];assert b['candidate_exe_sha256']==a['candidate_exe_sha256']==n['candidate_exe_sha256']==files['candidate_exe_sha256']==sha(candidate/'bin/scummvm.exe');assert bb['candidate_exe_sha256']==ab['candidate_exe_sha256']==n['baseline_diagnostic_exe_sha256']
for stage,transform in [(candidate,production),(original,baseline)]:
 cpp,h=transform((base/'astronomica.cpp').read_text(),(base/'astronomica.h').read_text());assert(stage/'source/engines/astronomica/astronomica.cpp').read_text()==cpp and(stage/'source/engines/astronomica/astronomica.h').read_text()==h
for audit in(a,ab,af):assert audit['fresh_translation_units']==audit['archive_members_checked']==7 and audit['verified_reused_framework_objects']==403 and audit['save_layouts_unchanged']
assert a['private_derived_cache_fields_added'] and not a['engine_class_layout_unchanged'] and ab['engine_class_layout_unchanged'] and af['engine_class_layout_unchanged']
assert len(n['cases'])==3 and n['all_processes_exited_naturally']
for c in n['cases']:
 if c['role']=='candidate':assert c['saw_actual_engine_pause'] and c['save_blocked_during_intro'] and c['load_blocked_during_intro'] and c['paused_millis']>=100 and c['audio_millis_at_escape']-c['audio_millis_at_pause']<50 and c['cursor_during_intro']==-1 and c['cursor_visible']
 else:assert not c['saw_actual_engine_pause'] and c['cursor_during_intro']==0 and c['audio_millis_at_escape']>100
assert len(files['cases'])==4 and files['all_processes_exited_naturally'] and all(c['introduction_completed_before_old_load']for c in files['cases'])
global_file=w/'intro-global-menu-native-nov12/proof.json'
while not global_file.exists():
 status=w/'intro-global-menu-native-nov12/status.json'
 if status.exists():assert read(status)['status']!='FAILED'
 time.sleep(1)
global_menu=read(global_file);assert global_menu['status'].endswith('PASS') and global_menu['candidate_exe_sha256']==b['candidate_exe_sha256'] and global_menu['cases'][0]['load_blocked_during_intro']is False and global_menu['cases'][1]['load_blocked_during_intro']is True
names=['intro-global-menu-native-nov12/proof.json','intro-menu-candidate-source-review-nov12c.json','intro-menu-baseline-source-review-nov12c.json','intro-menu-native-nov12c/proof.json','intro-menu-physical-saves-source-review-nov12c.json','intro-menu-physical-saves-native-nov12c/proof.json']
j=dict(status='INTRO_MENU_SOURCE_CAUSAL_AUDIO_CURSOR_AND_FILE_REVIEW_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=b['candidate_exe_sha256'],previous_exe_sha256=old['exe_sha256'],baseline_diagnostic_exe_sha256=bb['candidate_exe_sha256'],private_derived_introduction_busy_flag_added=True,save_and_load_public_and_stream_entrypoints_guarded=True,cursor_updated_before_original_spoken_intro_loop=True,all7engine_units_fresh=True,framework_and_save_schemas_unchanged=True,evidence_sha256={p:sha(w/p)for p in names},limits=['Same timed EventSourceobserver in accepted baseline/candidate;original P501S302runs completely in every case','Real F5menu/Enginepause/mixer elapsed time/busy save-load gates and previous exit-cursor fallback checked,including actual Windows backend','Four old accepted-engine physical ASVM2/26/27roundtrips run after complete original voice and busy-guard release;not all historical full futures','Derived UIflag is not serialized;class layout changes and all7engine units are rebuilt together','No original Windows program run,no original asset/save fixture/binary distribution,no human playthrough/global completion claim'])
(w/'intro-menu-review-nov12.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
