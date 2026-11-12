"""Join the causal stopped-clock replay proof and exact current shipping checks."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from mapped_navigation_source_nov12b import production as navigation
from p512_segment_replay_source_nov12 import inject as replay
from p512_memory_refusal_source_nov12f import inject as regression
from p512_replay_edges_source_nov12 import inject as edges
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(w/'space-pause-seal-nov12-status.json');base=Path(old['snapshot'])/'engine/astronomica';middle=w/'mapped-navigation-candidate-nov12b-stage';stage=w/'p512-segment-replay-nov12-stage';src=stage/'source/engines/astronomica';pin=read(stage/'proof.json')['candidate_exe_sha256']
cpp,header=navigation((base/'astronomica.cpp').read_text(),(base/'astronomica.h').read_text())
assert cpp==(middle/'source/engines/astronomica/astronomica.cpp').read_text() and header==(middle/'source/engines/astronomica/astronomica.h').read_text()
cpp,script=replay(cpp,(base/'script.cpp').read_text());assert cpp==(src/'astronomica.cpp').read_text() and script==(src/'script.cpp').read_text() and (src/'astronomica.h').read_text()==header
for subdir,inject in [('p512-memory-refusal-nov12g-stage',regression),('p512-replay-edges-nov12-stage',edges)]:
 observed_cpp,observed_script=inject(cpp,script);assert(w/subdir/'source/engines/astronomica/astronomica.cpp').read_text()==observed_cpp and(w/subdir/'source/engines/astronomica/script.cpp').read_text()==observed_script
names=['p512-segment-replay-source-review-nov12.json','p512-memory-refusal-native-nov12g/proof.json','p512-replay-edges-native-nov12/proof.json','p512-replay-navigation-native-nov12/proof.json','p512-replay-physical-saves-native-nov12/proof.json','p512-replay-genuine-nov12/proof.json']
items={name:read(w/name)for name in names}
assert all(v['status'].endswith('PASS')for v in items.values())
assert items[names[0]]['candidate_exe_sha256']==items[names[3]]['candidate_exe_sha256']==items[names[4]]['candidate_exe_sha256']==items[names[5]]['consumer_exe_sha256']==sha(stage/'bin/scummvm.exe')==pin
assert items[names[2]]['shipping_candidate_exe_sha256']==pin
assert items[names[1]]['diagnostic_exe_sha256']==read(w/'p512-memory-refusal-nov12g-stage/proof.json')['candidate_exe_sha256']
baseline=read(w/'p512-memory-refusal-native-nov12f/proof.json');assert baseline['status']=='P512_ISOLATED_MEMORY_REFUSAL_REPRODUCED' and baseline['native_exited_naturally']
text=(w/'p512-memory-refusal-native-nov12f/native.log').read_text();assert 'retained48525 end48533 current485'in text and 'seeks1/1 need0 unordered1'in text
assert len(items[names[3]]['cases'])==3 and len(items[names[4]]['cases'])==4 and items[names[5]]['fresh_processes']==4
assert items[names[0]]['engine_class_layout_unchanged'] and items[names[0]]['verified_reused_framework_objects']==403
j=dict(status='P512_SEGMENT_REPLAY_AND_CONTROLLER_SOURCE_REVIEW_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,previous_exe_sha256=old['exe_sha256'],intermediate_unpublished_exe_sha256=read(middle/'proof.json')['candidate_exe_sha256'],changed_engine_files=['astronomica.cpp'],class_layout_unchanged=True,core_and_native_save_schemas_unchanged=True,all7engine_units_fresh=True,evidence_sha256={name:sha(w/name)for name in names},baseline_refusal_proof_sha256=sha(w/'p512-memory-refusal-native-nov12f/proof.json'),optional_regression_source_recovered_exactly=True,optional_edges_source_recovered_exactly=True,limits=['The actual failed baseline saved a stopped clock before its range limit;controlled accepted packet clock=end-8reproduces missing seek deterministically','Existing source guard used stopped clock and endOfVideo;the latter ignores video range end while stopped. Next video frame records segment exhaustion independently','New no-field decoder helper used for both fresh and prepared P512 movies;only stopped exhausted ranges rewind,midrange and active cases preserved across6ranges/18cells','Baseline failure and corrected12edge-clock futures use exact same optional observer;original resources/commands/delays unchanged','760original navigation references/306scenes including Windows;four ASVM2/26/27post-intro roundtrips;four genuine old-main ASVM29 fresh continuations','Old failed general remains untouched in debugger;this review does not make that run pass. New exact candidate full general must independently pass before promotion','No original media,binaries,raw disassembly or native fixtures for public distribution;no whole-game completion claim'])
(w/'p512-segment-replay-review-nov12.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
