"""Validate the saved checkpoint against canonical sources and the local build."""
from pathlib import Path
import hashlib,json
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
m=json.loads((root/'evidence/development-validation.json').read_text())
for name,expected in m['engine_sha256'].items():
 assert digest(root/'engine/astronomica'/name)==expected,name
 assert digest(work/'scummvm/engines/astronomica'/name)==expected,('mirror',name)
assert digest(work/'build/Releasex64/scummvm.exe')==m['exe_sha256']
assert digest(root/'evidence/runtime.log')==m['runtime_log_sha256']
log=(root/'evidence/runtime.log').read_text()
assert 'FAIL' not in log and 'Astronomica script verification: PASS' in log
assert 'legacy save verification: PASS' in log
assert 'help original exponents: PASS (13 runs' in log
help_log=(root/'evidence/help-native-runtime.log').read_text()
assert 'help inline images: PASS (31 original images' in help_log
assert 'help original exponents: PASS (13 runs' in help_log
assert 'help article rendering: PASS (781 articles)' in help_log
assert 'help keyboard navigation: PASS (781 articles' in help_log
assert 'FAIL' not in help_log and 'Log closed successfully' in help_log
help_validation=json.loads((root/'evidence/help-native-validation.json').read_text())
assert help_validation['inline_images']==31 and help_validation['original_exponent_runs']==13
assert help_validation['keyboard_articles']==781
p508=json.loads((root/'evidence/p508-saves-validation.json').read_text())
assert p508['status']=='PASS' and p508['boundaries']==63 and p508['continuation_steps']==291
for name,marker in [('p508-saves-runtime.log','P508 saves: PASS (63 boundaries'),('p508-saves-startup.log','P508 startup save: PASS')]:
 s=(root/'evidence'/name).read_text()
 assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((root/'evidence/p508-save-proof.json').read_text())
assert proof['fresh_process_fingerprint']==p508['fresh_process_fingerprint'] and proof['metadata_listed']
original=json.loads((root/'evidence/p508-save-original.json').read_text())
assert original['status']=='PASS' and len(original['pictures'])==18
assert digest(Path('D:/astro/PLACES/P508/MEGAFILE.HYP'))==original['source_sha256']
for picture in original['pictures']:
 assert digest(Path('D:/astro/PLACES/P508')/picture['file'])==picture['sha256']
p505=json.loads((root/'evidence/p505-saves-validation.json').read_text())
assert json.loads((root/'evidence/p508-previous-slot-proof.json').read_text())['unchanged']
assert 'P508 startup save: PASS' in (root/'evidence/p508-previous-slot.log').read_text()
assert p505['status']=='PASS' and p505['boundaries']==38 and p505['successor_comparisons']==38 and p505['hover_resumptions']==38
for name,marker in [('p505-saves-runtime.log','P505 saves: PASS (38 boundaries'),('p505-saves-startup.log','P505 startup save: PASS')]:
 s=(root/'evidence'/name).read_text()
 assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((root/'evidence/p505-save-proof.json').read_text())
assert proof['fresh_process_fingerprint']==p505['fresh_process_fingerprint'] and proof['metadata_listed']
original=json.loads((root/'evidence/p505-save-original.json').read_text())
assert original['status']=='PASS' and len(original['pictures'])==8
assert digest(Path('D:/astro/PLACES/P505/MEGAFILE.HYP'))==original['source_sha256']
for picture in original['pictures']:
 assert digest(Path('D:/astro/PLACES/P505')/picture['file'])==picture['sha256']
p519=json.loads((root/'evidence/p519-save-original.json').read_text())
assert p519['status']=='PASS' and len(p519['images'])==10 and len(p519['image_commands'])==15
assert p519['pixel_sequence_comparisons']==1000
assert digest(Path('D:/astro/PLACES/P519/MEGAFILE.HYP'))==p519['source_sha256']
for picture in p519['images']:
 assert digest(Path('D:/astro/PLACES/P519')/picture['file'])==picture['sha256']
legacy=json.loads((root/'evidence/legacy-validation.json').read_text())
p524=json.loads((root/'evidence/p524-save-original.json').read_text())
assert p524['status']=='PASS' and len(p524['pictures'])==9 and p524['animated_frame_count']==8
assert p524['sprite_frame_counts']==[2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,2,8]
assert p524['sprite31_original_geometry']['xy']==[94,58]
assert digest(Path('D:/astro/PLACES/P524/MEGAFILE.HYP'))==p524['source_sha256']
for picture in p524['pictures']:
 assert digest(Path('D:/astro/PLACES/P524')/picture['file'])==picture['sha256']
p519save=json.loads((root/'evidence/p519-saves-validation.json').read_text())
assert p519save['status']=='PASS' and p519save['boundaries']==104 and p519save['gameplay_successor_comparisons']==74 and p519save['resource_compositions']==30
for name,marker in [('p519-saves-runtime.log','P519 saves: PASS (104 boundaries'),('p519-saves-startup.log','P519 startup save: PASS'),('p505-previous-slot.log','P505 startup save: PASS')]:
 s=(root/'evidence'/name).read_text()
 assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((root/'evidence/p519-save-proof.json').read_text())
assert proof['fresh_process_fingerprint']==p519save['fresh_process_fingerprint'] and proof['metadata_listed']
assert json.loads((root/'evidence/p505-previous-slot-proof.json').read_text())['unchanged']
assert legacy['status']=='PASS' and legacy['full_suite'] and legacy['original_menu_flow']
assert legacy['native_resave'] and legacy['fixture_unchanged']
legacy_log=(root/'evidence/legacy-runtime.log').read_text()
for marker in ('legacy original payloads: PASS','legacy parser checks: PASS','legacy state checks: PASS','legacy save verification: PASS'):
 assert marker in legacy_log,marker
assert 'FAIL' not in legacy_log and 'Log closed successfully' in legacy_log
assert json.loads((root/'evidence/legacy-file-proof.json').read_text())['unchanged_after_import']
research=json.loads((root/'evidence'/m.get('research_manifest','research-sept28.json')).read_text())
for name,expected in research['sha256'].items():assert digest(root/name)==expected,name
for name,expected in research['original_inputs_sha256'].items():assert digest(Path('D:/astro')/name)==expected,name
inventory=json.loads((root/'evidence/puzzle-save-requirements.json').read_text())
assert sorted(row['place'] for row in inventory['rows'])==sorted(m['complete_route_scenes'])
for row in inventory['rows']:
 original=Path('D:/astro')/f"PLACES/P{row['place']}/MEGAFILE.HYP"
 assert digest(original)==row['source_sha256'],str(original)
 assert original.stat().st_size==row['parsed_bytes']+row['trailing_bytes'],str(original)
print('Checkpoint integrity: PASS',m['date'],len(m['complete_route_scenes']),'puzzle route scenes; interactive:',m['interactive_nonpuzzle_scenes'])

p524save=json.loads((root/'evidence/p524-saves-validation.json').read_text())
assert p524save['status']=='PASS' and p524save['boundaries']==72 and p524save['animation_cases']==48
for name,marker in [('p524-saves-runtime.log','P524 saves: PASS (72 boundaries'),('p524-saves-startup.log','P524 startup save: PASS'),('p519-previous-slot.log','P519 startup save: PASS')]:
 s=(root/'evidence'/name).read_text()
 assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((root/'evidence/p524-save-proof.json').read_text())
assert proof['fresh_process_fingerprint']==p524save['fresh_process_fingerprint'] and proof['metadata_listed']
assert json.loads((root/'evidence/p519-previous-slot-proof.json').read_text())['unchanged']
assert p524['moon_sequence']['mask']==255 and p524['moon_sequence']['scenario']==9
print('P524 save evidence integrity PASS')
p526=json.loads((root/'evidence/p526-save-original.json').read_text())
assert p526['status']=='PASS' and len(p526['pictures'])==6 and len(p526['animations'])==3
assert digest(Path('D:/astro/PLACES/P526/MEGAFILE.HYP'))==p526['source_sha256']
for picture in p526['pictures']:
 assert digest(Path('D:/astro/PLACES/P526')/picture['file'])==picture['sha256']
print('P526 original save requirements integrity PASS')
save_coverage=json.loads((root/'evidence/native-save-coverage.json').read_text())
assert save_coverage['status']=='PASS' and save_coverage['exe_sha256']==m['exe_sha256'] and save_coverage['engine_sha256']==m['engine_sha256']
assert save_coverage['whole_game_completion_percent'] is None and save_coverage['supported_puzzle_route_scenes']==7
assert {row['scene'] for row in save_coverage['puzzle_saves']}=={505,508,519,524,526,528,530}
for row in save_coverage['puzzle_saves']:
 assert digest(root/row['validation_file'])==row['validation_sha256']
 assert digest(root/f"evidence/p{row['scene']}-saves-runtime.log")==row['runtime_sha256']
 assert digest(root/f"evidence/p{row['scene']}-saves-startup.log")==row['startup_sha256']
print('Measured native save coverage integrity PASS')
p526save=json.loads((root/'evidence/p526-saves-validation.json').read_text())
assert p526save['status']=='PASS' and p526save['boundaries']==686 and p526save['animation_cases']==216 and p526save['synthetic_answer_cases']==432
for name,marker in [('p526-saves-runtime.log','P526 saves: PASS (686 boundaries'),('p526-saves-startup.log','P526 startup save: PASS'),('p524-previous-slot.log','P524 startup save: PASS')]:
 s=(root/'evidence'/name).read_text()
 assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((root/'evidence/p526-save-proof.json').read_text())
assert proof['fresh_process_fingerprint']==p526save['fresh_process_fingerprint'] and proof['metadata_listed']
assert json.loads((root/'evidence/p524-previous-slot-proof.json').read_text())['unchanged']
audit=json.loads((root/'evidence/p526-native-save-boundaries.json').read_text())
assert audit['boundaries']==33 and audit['exe_sha256']==m['exe_sha256'] and audit['source_sha256']==p526['source_sha256']
print('P526 v7 save evidence integrity PASS')
p528=json.loads((root/'evidence/p528-save-original.json').read_text())
assert p528['status']=='PASS' and len(p528['phases'])==12 and len(p528['images'])==23
assert p528['pixel_history_comparisons']==1728 and len(p528['last_pair_only_failures'])==32
assert len(set(p528['tall_moon_last_row_sha256'].values()))==4
assert len(p528['natural_cycle_snapshots'])==48
assert p528['natural_cycle_snapshots'][0]['background_sha256']!=p528['natural_cycle_snapshots'][12]['background_sha256']
assert p528['legacy_debug_strip_overlap']['pixel_addresses']==855 and p528['legacy_debug_strip_overlap']['nonblack_pixels']==204
assert digest(Path('D:/astro/PLACES/P528/MEGAFILE.HYP'))==p528['source_sha256']
for picture in p528['images']:
 assert digest(Path('D:/astro/PLACES/P528')/picture['file'])==picture['sha256']
assert next(row for row in p528['phases'] if row['phase']==2)['pictures'][0]['file']=='GE_S1'
print('P528 original save requirements integrity PASS')
answer=json.loads((root/'evidence/p528-answer-states.json').read_text())
assert answer['status']=='PASS' and answer['case_count']==192 and answer['instruction_count']==50 and answer['instructions_covered']==50
assert answer['settled_input_combinations']==144 and answer['completion_edges_from_settled_inputs']==4
assert answer['first_flag_pairs']==[[0,1],[6,3]] and answer['second_flag_pairs']==[[0,3],[6,1]]
assert answer['resource_sha256']==p528['source_sha256'] and digest(Path('D:/astro/SETUP/ASTRO.EXE'))==answer['executable_sha256']
assert answer['original_completion_condition_delay_ms']==400 and answer['original_completion_destination_delay_ms']==4500 and answer['original_completion_destination']==526
assert len(answer['cases'])==192 and {tuple([r['phase'],r['quadrant'],*r['before']]) for r in answer['cases']}=={(p,q,a,b) for p in range(12) for q in range(4) for a in range(2) for b in range(2)}
assert {p for row in answer['cases'] for p in row['trace']}=={row['address'] for row in answer['instructions']}
for row in answer['cases']:
 assert row['result']==int(row['after']==[1,1]) and row['sound'] in (8,9,10)
 assert all(after>=before for before,after in zip(row['before'],row['after']))
print('P528 original answer-state audit integrity PASS')
graph_path=root/'evidence/p528-settled-graph.json';graph=json.loads(graph_path.read_text())
assert graph['status']=='PASS' and graph['source_sha256']==p528['source_sha256']
assert graph['answer_reference_sha256']==digest(root/'evidence/p528-answer-states.json')
assert (graph['state_count'],graph['edge_count'],graph['completion_edges'],graph['geometry_history_count'],graph['absent_picture_states'])==(160,480,6,56,4)
states={tuple(row['values']) for row in graph['states']};assert len(states)==160 and len(graph['edges'])==480
assert graph['initial']==[11,0,0,0,False,'']
assert sum(e['departure_to']==526 for e in graph['edges'])==6
for row in graph['states']:
 p,q,first,second,committed,tall=row['values']
 assert p in range(12) and q in range(4) and first in (0,1) and second in (0,1) and not(first and second)
 if not committed:assert p==11 and not first and not second and not tall
for edge in graph['edges']:
 assert tuple(edge['source']) in states
 if edge['departure_to'] is None:assert tuple(edge['target']) in states
 else:assert edge['departure_to']==526 and edge['target'][2:4]==[1,1]
for name,expected in graph['original_moon_sha256'].items():assert digest(Path('D:/astro/PLACES/P528')/name)==expected,name
print('P528 settled-state abstraction integrity PASS')
presentation=json.loads((root/'evidence/presentation-validation.json').read_text())
assert presentation['status']=='PASS' and presentation['exe_sha256']==m['exe_sha256'] and presentation['frame_height']==480
assert presentation['scene_count']==12 and presentation['original_p528_pixels_checked']==855 and not presentation['debug_overlay_default']
assert presentation['optional_overlay'] and presentation['recovery_after_disable'] and presentation['full_suite']
s=(root/'evidence/presentation.log').read_text()
assert 'full-height presentation: PASS (12 scenes, 855 original P528 pixels' in s and 'FAIL' not in s and 'Log closed successfully' in s
assert json.loads((root/'evidence/p526-previous-slot-proof.json').read_text())['unchanged']
assert 'P526 startup save: PASS' in (root/'evidence/p526-previous-slot.log').read_text()
print('Full-frame presentation evidence integrity PASS')
audio=json.loads((root/'evidence/audio-channels-validation.json').read_text())
assert audio['status']=='PASS' and audio['exe_sha256']==m['exe_sha256'] and audio['full_suite']
assert audio['scenes']==[505,508,519,524,526,528] and audio['music_loops']==6 and audio['foreground_replacements']==6
assert audio['music_muted'] and audio['music_volume']==0 and audio['effects_volume']==256 and audio['effects_unmuted'] and audio['controls_restored']
s=(root/'evidence/audio-channels.log').read_text()
assert 'audio channel verification: PASS (6 muted music loops, 6 foreground replacements, controls restored)' in s and 'FAIL' not in s and 'Log closed successfully' in s
proof=json.loads((root/'evidence/audio-channels-proof.json').read_text())
assert proof['status']=='PASS' and proof['unchanged'] and len(proof['original_wav_sha256'])==12
for name,expected in proof['original_wav_sha256'].items():assert digest(Path(name))==expected,name
print('Audio category evidence integrity PASS')
p528save=json.loads((root/'evidence/p528-saves-validation.json').read_text())
assert p528save['status']=='PASS' and p528save['exe_sha256']==m['exe_sha256'] and p528save['full_suite']
assert (p528save['format_version'],p528save['payload_bytes'],p528save['reachable_states'],p528save['boundaries'],p528save['completion_edges'],p528save['unsolved_exits'],p528save['full_frame_height'])==(8,3444,160,640,6,160,480)
proof=json.loads((root/'evidence/p528-save-proof.json').read_text())
assert proof['metadata_listed'] and proof['slot']==7 and proof['resource_edges_compared']==640
assert proof['original_state_graph_sha256']==digest(graph_path) and proof['fresh_process_fingerprint']==p528save['fresh_process_fingerprint']
for name,marker in [('p528-saves-runtime.log','P528 saves: PASS (160 reachable states, 640 round trips'),('p528-saves-startup.log','P528 startup save: PASS')]:
 s=(root/'evidence'/name).read_text();assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
print('P528 v8 native save evidence integrity PASS')
p530=json.loads((root/'evidence/p530-save-original.json').read_text())
assert p530['status']=='PASS' and p530['command_count']==581 and p530['image_commits']==25 and p530['image_history_comparisons']==625
assert len(p530['conditions'])==14 and p530['startup_programs']==11 and len(p530['sprite_frames'])==29
assert digest(Path('D:/astro/PLACES/P530/MEGAFILE.HYP'))==p530['source_sha256']
assert len(p530['images'])==25 and {(p['width'],p['height'],p['x'],p['y']) for p in p530['images']}=={(172,172,460,10)}
for p in p530['images']:assert digest(Path('D:/astro/PLACES/P530')/p['file'])==p['sha256']
print('P530 original save inventory integrity PASS')
p530save=json.loads((root/'evidence/p530-saves-validation.json').read_text())
assert p530save['status']=='PASS' and p530save['exe_sha256']==m['exe_sha256'] and p530save['full_suite']
assert (p530save['format_version'],p530save['payload_bytes'],p530save['scenarios_per_round'],p530save['rounds'],p530save['pictures'],p530save['full_frame_height'])==(9,5604,5,3,25,480)
assert p530save['partial_components'] and p530save['prior_round_picture'] and p530save['random_continuation'] and p530save['counter_unchanged']
assert p530save['placement_permutations']==6
assert 8<=p530save['solve_routes']<=32 and p530save['boundaries']==57*p530save['solve_routes']+2
proof=json.loads((root/'evidence/p530-save-proof.json').read_text())
assert proof['metadata_listed'] and proof['slot']==8 and proof['fresh_process_fingerprint']==p530save['fresh_process_fingerprint']
assert proof['round_trips']==p530save['boundaries'] and proof['solve_routes']==p530save['solve_routes']
for name,marker in [('p530-saves-runtime.log','P530 saves: PASS ('),('p530-saves-startup.log','P530 startup save: PASS'),('p528-previous-slot.log','P528 startup save: PASS')]:
 s=(root/'evidence'/name).read_text();assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
assert json.loads((root/'evidence/p528-previous-slot-proof.json').read_text())['unchanged']
orders=json.loads((root/'evidence/p530-orders-original.json').read_text())
assert orders['status']=='PASS' and orders['source_sha256']==p530['source_sha256'] and orders['case_count']==100 and len(orders['cases'])==100
assert orders['correct_detectors_by_last_sprite']=={'19':[2,4,5,1,4],'20':[2,4,5,1,4],'21':[2,4,5,1,4],'22':[2,1,5,4,4]}
print('P530 v9 native save and original-order evidence integrity PASS')
