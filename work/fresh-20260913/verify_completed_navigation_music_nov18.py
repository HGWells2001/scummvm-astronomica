"""Recheck the completed native trace after a boolean conversion error in its result parser."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;out=w/'navigation-music-native-nov18b';stage=w/'navigation-music-observer-nov18b-stage'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
failed=out/'failed-parser.py';assert sha(failed)=='608954ffb06ba39230717d608b51c2260659d07fc1935d145daf359bb3845888'
failure=read(out/'status.json');assert failure['status']=='FAILED'
assert 'line 27, in <module>'in failure['error'] and "row[10]==bool((c['destination_loop'] or -1))"in failure['error']
# The pinned driver passed its preceding code==0 /1538 rows/complete-line guard
# before reaching this boolean assertion. Preserve that failure record unchanged.
assert "assert code==0 and len(rows)==1538 and 'Navigation Music complete: passed1538 total1538'in text"in failed.read_text()
build=read(stage/'proof.json');release=read(w/'p513-control-music-seal-nov17.json');cases=read(w/'navigation-music-cases-nov18.json')['cases']
assert build['status']=='NAVIGATION_MUSIC_OBSERVER_B_BUILD_PASS' and len(cases)==1538
assert sha(stage/'bin/scummvm.exe')==build['candidate_exe_sha256'] and sha(w/'build/Releasex64/scummvm.exe')==build['base_exe_sha256']==release['exe_sha256']
from navigation_music_source_nov18b import observe
source=w.parents[1]/'outputs/astronomica-cleanroom/engine/astronomica';cpp,header=observe((source/'astronomica.cpp').read_text(),(source/'astronomica.h').read_text())
assert cpp==(stage/'source/engines/astronomica/astronomica.cpp').read_text() and header==(stage/'source/engines/astronomica/astronomica.h').read_text()
log=out/'native.log';text=log.read_text(errors='replace')
rows=[tuple(map(int,x))for x in re.findall(r'Navigation Music row: case(\d+) route(\d+) P(\d+) dir(\d+) requested(\d+) permit(\d+) pad(\d+) actual(\d+) after(\d+) loop(-?\d+) active(\d) advancing(\d) owner(\d) resultPASS',text)]
assert len(rows)==1538 and 'Navigation Music complete: passed1538 total1538'in text and 'FAIL'not in text
assert text.rstrip().endswith('--- Log closed successfully.') and not list((out/'saves').iterdir())
for i,(row,c)in enumerate(zip(rows,cases)):
    assert row[:10]==(i,c['route_index'],c['source'],c['direction'],c['requested'],c['permit'],c['keypad'],c['destination'],c['permit_after'],c['destination_loop']or -1)
    assert row[10]==bool(c['destination_loop']) and row[12]==1
    if c['destination_loop']:assert row[11]==1
receipt=dict(status='ORIGINAL_NAVIGATION_ACTIVE_MUSIC_PASS',at=datetime.now(timezone.utc).isoformat(),observer_exe_sha256=build['candidate_exe_sha256'],canonical_exe_sha256=release['exe_sha256'],observer_build_proof_sha256=sha(stage/'proof.json'),cases_sha256=sha(w/'navigation-music-cases-nov18.json'),native_log_sha256=sha(log),literal_navigation_routes=760,source_rooms_with_routes=305,mode1_room_without_nav_routes=31,keyboard_variants=2,extra_permitted_gate_fixtures=9,native_cases=1538,canonical_engine_changed=False,normal_frame_pump_preserved=True,native_exited_naturally=True,mute=True,audio_driver='wasapi',completed_trace_revalidated_without_native_rerun=True,failed_parser_sha256=sha(failed),preserved_failure_status_sha256=sha(out/'status.json'),native_exit_zero_verified_via_preceding_pinned_driver_assertion=True,validator_sha256=sha(Path(__file__)),limits=['Controlled direct source loads and actual arrow/keypad handlers, not natural reachability from a new game','Selected global57 fixtures, not exhaustive global-state or sprite-click coverage','Native stream ownership and elapsed progress, not acoustic playback','Denied P429 gate boundaries checked before complete movie playback','The original result parser converted no-track sentinel-1 to boolean true; corrected independent validation preserves the completed log and failure record'])
(out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
