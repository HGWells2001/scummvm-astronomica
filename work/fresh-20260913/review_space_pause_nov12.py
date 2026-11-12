"""Bind standard Space pause and isolated self-test setup to native source and save evidence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from space_pause_source_nov12 import production,baseline
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(w/'intro-menu-seal-nov12-status.json');base=Path(old['snapshot'])/'engine/astronomica'
candidate=w/'space-pause-candidate-nov12-stage';original=w/'space-pause-baseline-nov12-stage'
b=read(candidate/'proof.json');bb=read(original/'proof.json')
a=read(w/'space-pause-candidate-source-review-nov12.json');ab=read(w/'space-pause-baseline-source-review-nov12.json')
n=read(w/'space-pause-native-nov12/proof.json');files=read(w/'space-pause-physical-saves-native-nov12/proof.json');af=read(w/'space-pause-physical-saves-source-review-nov12.json')
assert b['base_exe_sha256']==bb['base_exe_sha256']==old['exe_sha256']
assert b['candidate_exe_sha256']==a['candidate_exe_sha256']==n['candidate_exe_sha256']==files['candidate_exe_sha256']==sha(candidate/'bin/scummvm.exe')
assert bb['candidate_exe_sha256']==ab['candidate_exe_sha256']==n['baseline_diagnostic_exe_sha256']
for stage,transform in [(candidate,production),(original,baseline)]:
 cpp,h=transform((base/'astronomica.cpp').read_text(),(base/'astronomica.h').read_text())
 assert(stage/'source/engines/astronomica/astronomica.cpp').read_text()==cpp and(stage/'source/engines/astronomica/astronomica.h').read_text()==h
for audit in(a,ab,af):
 assert audit['fresh_translation_units']==audit['archive_members_checked']==7 and audit['verified_reused_framework_objects']==403 and audit['save_layouts_unchanged'] and audit['engine_class_layout_unchanged']
assert len(n['cases'])==3 and n['all_processes_exited_naturally']
for c in n['cases']:
 if c['role']=='candidate':assert c['saw_actual_engine_pause'] and c['save_blocked_during_intro'] and c['load_blocked_during_intro'] and c['paused_millis']>=100 and c['audio_millis_at_escape']-c['audio_millis_at_pause']<50
 else:assert not c['saw_actual_engine_pause'] and c['audio_millis_at_escape']>100
 assert c['cursor_during_intro']==-1 and c['cursor_visible'] and len(c['room_checks'])==2
assert len(files['cases'])==4 and files['all_processes_exited_naturally'] and all(c['introduction_completed_before_old_load']for c in files['cases'])
names=['space-pause-candidate-source-review-nov12.json','space-pause-baseline-source-review-nov12.json','space-pause-native-nov12/proof.json','space-pause-physical-saves-source-review-nov12.json','space-pause-physical-saves-native-nov12/proof.json']
j=dict(status='SPACE_PAUSE_SOURCE_CAUSAL_AUDIO_AND_FILE_REVIEW_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=b['candidate_exe_sha256'],previous_exe_sha256=old['exe_sha256'],baseline_diagnostic_exe_sha256=bb['candidate_exe_sha256'],class_layout_unchanged=True,all7engine_units_fresh=True,framework_and_save_schemas_unchanged=True,evidence_sha256={p:sha(w/p)for p in names},limits=['Same timed EventSource in accepted baseline and candidate;complete original P501 voice;actual Windows backend','P103 room and P27 actual click-locked pending program preserve full runner hash,screen RGB,cursor and game clock across actual pause','Ctrl/Alt/Meta Space remain unhandled by the engine pause action','Four old physical ASVM2/26/27 roundtrips after complete introduction;not all historical futures','No original Windows program run,original asset distribution,human listening test or whole-game completion claim'])
(w/'space-pause-review-nov12.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
