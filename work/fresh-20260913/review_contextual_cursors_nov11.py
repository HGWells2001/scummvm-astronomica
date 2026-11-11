"""Bind original contextual zone evidence to the exact built engine and natural-exit tests."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
from contextual_cursor_source_nov11b import production
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(w/'navigation-cursors-seal-nov11-status.json');stage=w/'contextual-cursors-nov11b-stage';b=read(stage/'proof.json');a=read(w/'contextual-cursors-source-review-nov11b.json');n=read(w/'contextual-cursors-native-nov11b/proof.json');loop=read(w/'contextual-cursor-loop-native-nov11b/proof.json');facts=read(w/'original-down-cursor-nov11/proof.json')
assert b['base_exe_sha256']==old['exe_sha256'] and a['candidate_exe_sha256']==n['candidate_exe_sha256']==loop['candidate_exe_sha256']==b['candidate_exe_sha256']==sha(stage/'bin/scummvm.exe')
base=Path(old['snapshot'])/'engine/astronomica';cpp,h=production((base/'astronomica.cpp').read_text(),(base/'astronomica.h').read_text());assert cpp==(stage/'source/engines/astronomica/astronomica.cpp').read_text() and h==(stage/'source/engines/astronomica/astronomica.h').read_text()
assert a['fresh_translation_units']==a['archive_members_checked']==7 and a['verified_reused_framework_objects']==403 and a['derived_cursor_array_expanded'] and not a['engine_class_layout_unchanged'] and a['save_layouts_unchanged']
assert len(n['cases'])==6 and n['native_gui_profiles']==4 and n['all_processes_exited_naturally'] and len(loop['cases'])==3 and loop['all_processes_exited_naturally']
rows=[]
for c in loop['cases']:
 log=w/'contextual-cursor-loop-native-nov11b'/c['profile']/'native.log';text=log.read_text(errors='replace')
 passed=len(re.findall(r'Navigation cursor player frame: PASS',text));waits=len(re.findall(r'Contextual cursor deferred frame: WAIT',text));assert passed==len(c['frames']) and waits>=1 and 'FAIL'not in text
 rows.append(dict(profile=c['profile'],checked_phases=passed,deferred_wait_frames=waits,observed_loop_iterations=passed+waits,log_sha256=sha(log)))
assert sum(c['old_fixture']is not None for c in loop['cases'])==2 and all(c['new_physical_save_version']==2 for c in loop['cases'])
evidence=['original-down-cursor-nov11/proof.json','original-navigation-cursors-nov11/proof.json','contextual-cursors-source-review-nov11b.json','contextual-cursors-native-nov11b/proof.json','contextual-cursor-loop-native-nov11b/proof.json']
j=dict(status='ORIGINAL_CONTEXTUAL_CURSOR_SOURCE_GUI_EVENT_FILE_REVIEW_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=b['candidate_exe_sha256'],previous_exe_sha256=old['exe_sha256'],original_scene_ids=facts['scene_ids'],original_rect=facts['rect'],original_cursor_group=4,original_context_global='cb8',ordinary_NAV_axis_added=False,original_deferred_script_timing_unchanged=True,all7engine_units_fresh=True,framework_and_save_schemas_unchanged=True,loop_observations=rows,evidence_sha256={p:sha(w/p)for p in evidence},limits=['Original NEbytes,pixels,disassembly and previews local only','16/17/17checked phases plus separately counted deferred WAITframes;legacy diagnostic terminal frame label is not a total frame count','SDLdummy controlled native input and CursorMan calls;not manual hardware pointer or human whole-game validation','Two frozen earlier accepted-engine ASVM26/27file loads;not original Windows saves or all-history full futures','Fixed acceptance7/10;whole-game completion unmeasured'])
(w/'contextual-cursors-review-nov11.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'],rows)
