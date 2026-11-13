"""Review the real synchronous-voice stack guard,exact source and bounded native gates."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from blocking_voice_source_nov13 import baseline,production
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(w/'double-click-seal-nov12-status.json');base=Path(old['snapshot'])/'engine/astronomica';stage=w/'blocking-voice-candidate-nov13-stage';src=stage/'source/engines/astronomica';pin=read(stage/'proof.json')['candidate_exe_sha256']
for role,transform in [('candidate',production),('baseline',baseline)]:
 folder=w/('blocking-voice-'+role+'-nov13-stage');cpp,h=transform((base/'astronomica.cpp').read_text(),(base/'astronomica.h').read_text());assert cpp==(folder/'source/engines/astronomica/astronomica.cpp').read_text() and h==(folder/'source/engines/astronomica/astronomica.h').read_text()
 audit=read(w/('blocking-voice-'+role+'-source-review-nov13.json'));assert audit['fresh_translation_units']==audit['archive_members_checked']==7 and audit['verified_reused_framework_objects']==403 and audit['save_layouts_unchanged']
 assert audit['engine_class_layout_unchanged']==(role=='baseline') and read(folder/'proof.json')['base_exe_sha256']==old['exe_sha256']
names=['blocking-voice-candidate-source-review-nov13.json','blocking-voice-baseline-source-review-nov13.json','blocking-voice-native-nov13b/proof.json','blocking-voice-physical-saves-native-nov13/proof.json','blocking-voice-genuine-nov13/proof.json','blocking-voice-p512-clock-native-nov13/proof.json']
items={n:read(w/n)for n in names};assert all(j['status'].endswith('PASS')for j in items.values())
assert items[names[0]]['candidate_exe_sha256']==items[names[2]]['candidate_exe_sha256']==items[names[3]]['candidate_exe_sha256']==items[names[4]]['consumer_exe_sha256']==items[names[5]]['shipping_candidate_exe_sha256']==pin==sha(stage/'bin/scummvm.exe')
assert len(items[names[2]]['cases'])==4 and items[names[2]]['save_load_and_streams_guarded'] and items[names[2]]['paused_time_excluded_from_script_deadline'] and items[names[2]]['all_processes_exited_naturally']
assert len(items[names[3]]['cases'])==4 and items[names[4]]['fresh_processes']==4
cpp=(src/'astronomica.cpp').read_text();header=(src/'astronomica.h').read_text()
assert cpp.count('if(_blockingSoundDepth)')==4 and header.count('uint _blockingSoundDepth=0;')==1
assert 'voiceStack(_blockingSoundDepth)'in cpp and 'uint32(_pausedMillis-pausedBefore)'in cpp
result=dict(status='BLOCKING_VOICE_SOURCE_AND_NATIVE_REVIEW_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,previous_exe_sha256=old['exe_sha256'],engine_class_layout_changed=True,transient_voice_stack_depth_added=True,core_and_save_schemas_unchanged=True,evidence_sha256={n:sha(w/n)for n in names},limits=['F5and unmodified Space handled in real common synchronous voice callback;actual original SOUNDS/S12voice,baseline/dummy/Windows','Actual mixer audio freezes in menu/pause;script deadline excludes held Engine pause time;runner state preserved','One private transient depth counter guards both public save/load queries and both stream methods;RAII handles nesting;all7engine units fresh/403foundation','Candidate accepted P536backlog/hostcontrols,4old physicalASVM2/26/27roundtrips,4genuine oldASVM29continuations,12P512clock futures PASS','Controlled common callback test,not every original caller or human audio quality check;new exact full general required before installation','Initial test driver targeted a nonexistent old-date stage and started no native process;correctedB uses actual13Novstages;old waiting drivers untouched','No whole-game completion or new fixed acceptance percentage'])
(w/'blocking-voice-review-nov13.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
