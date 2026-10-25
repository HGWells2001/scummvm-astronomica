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
probe_save_present=(root/'evidence/probe-saves-validation.json').is_file()
rendezvous_save_present=(root/'evidence/rendezvous-saves-validation.json').is_file()
planet_save_present=(root/'evidence/planet-saves-validation.json').is_file()
p521_save_present=(root/'evidence/p521-saves-validation.json').is_file()
p509_save_present=(root/'evidence/p509-saves-validation.json').is_file()
p511_save_present=(root/'evidence/p511-saves-validation.json').is_file()
p516_save_present=(root/'evidence/p516-saves-validation.json').is_file()
expected_save_scenes={505,506,508,513,515,517,519,524,526,528,529,530,531,532,533,534,535,536,537}
if probe_save_present:expected_save_scenes.add(522)
if rendezvous_save_present:expected_save_scenes.add(514)
if planet_save_present:expected_save_scenes.add(518)
if p521_save_present:expected_save_scenes.add(521)
if p509_save_present:expected_save_scenes.add(509)
if p511_save_present:expected_save_scenes.add(511)
if p516_save_present:expected_save_scenes.add(516)
assert save_coverage['whole_game_completion_percent'] is None and save_coverage['supported_puzzle_route_scenes']==len(expected_save_scenes)
assert {row['scene'] for row in save_coverage['puzzle_saves']}==expected_save_scenes
for row in save_coverage['puzzle_saves']:
 assert digest(root/row['validation_file'])==row['validation_sha256']
 assert digest(root/row.get('runtime_file',f"evidence/p{row['scene']}-saves-runtime.log"))==row['runtime_sha256']
 assert digest(root/row.get('startup_file',f"evidence/p{row['scene']}-saves-startup.log"))==row['startup_sha256']
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
variant_original=json.loads((root/'evidence/variant-save-original.json').read_text())
assert variant_original['status']=='PASS' and [s['scene'] for s in variant_original['scenes']]==[506,531,532,533,534,535]
for scene in variant_original['scenes']:
 assert digest(Path(f"D:/astro/PLACES/P{scene['scene']}/MEGAFILE.HYP"))==scene['source_sha256']
v=json.loads((root/'evidence/variant-saves-validation.json').read_text())
proof=json.loads((root/'evidence/variant-save-proof.json').read_text())
assert v['status']=='PASS' and v['exe_sha256']==m['exe_sha256'] and v['full_suite'] and v['format_version']==10
assert v['payload_bytes_by_scene']=={'506':3992,'531':3992,'532':3776,'533':3776,'534':4424,'535':3776}
assert v['scenes_per_stage']==6 and v['stages']==4 and v['full_frame_height']==480 and v['initial_repeats']>0
assert proof['metadata_listed'] and proof['slot']==9 and proof['fresh_process_fingerprint']==v['fresh_process_fingerprint']
assert v['boundaries']==proof['boundaries'] and v['solve_routes']==proof['routes'] and v['transitions']==4*v['solve_routes']+1
assert v['truncations']==v['byte_corruptions']==23736 and v['invalid_checksummed_states']==192
assert all(v[k] for k in ('partial_solutions','process_statics','random_continuation','first_completion_count','repeated_completion_count','exit_reentry'))
assert json.loads((root/'evidence/p530-previous-slot-proof.json').read_text())['unchanged']
for name,marker in [('variant-saves-runtime.log','variant saves: PASS ('),('variant-saves-startup.log','variant startup save: PASS'),('p530-previous-slot.log','P530 startup save: PASS'),('save-entry-history.log','save entry history: PASS (4 original P509 entries, 12 inert-value round trips, 8 metadata rejections')]:
 s=(root/'evidence'/name).read_text();assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
history=json.loads((root/'evidence/save-entry-history-proof.json').read_text())
assert history['status']=='PASS' and history['exe_sha256']==m['exe_sha256'] and history['destinations']==[524,526,528,530]
assert history['original_entries']==4 and history['inert_extreme_round_trips']==12 and history['metadata_rejections']==8
assert 'save entry history rejected: P509 -> P524' in (root/'evidence/save-entry-history-before.log').read_text()
launcher=json.loads((root/'evidence/local-launcher-validation.json').read_text())
assert launcher['status']=='PASS' and launcher['exe_sha256']==m['exe_sha256'] and launcher['normal_P1_startup']
assert launcher['template_sha256']==digest(root/'astronomica-play.ini')
print('Custom17 v10, original entry-history correction and normal launcher evidence integrity PASS')
p513=json.loads((root/'evidence/p513-save-original.json').read_text())
assert p513['status']=='PASS' and len(p513['sprite_frames'])==32 and len(p513['conditions'])==6 and len(p513['startup'])==4
assert p513['image_history_comparisons']==1089 and len(p513['images'])==33
assert len({p['file'] for p in p513['images']})==17
assert digest(Path('D:/astro/PLACES/P513/MEGAFILE.HYP'))==p513['source_sha256']
for picture in p513['images']:
 assert (picture['width'],picture['height'],picture['x'],picture['y'])==(313,320,177,22)
 assert digest(Path('D:/astro/PLACES/P513')/picture['file'])==picture['sha256']
cross=json.loads((root/'evidence/p513-cross-setting.json').read_text())
motion=json.loads((root/'evidence/p513-motion.json').read_text())
assert cross['code_sha256']==motion['code_sha256']
assert [(r['initial_setting'],r['setting_after20_ticks'],r['last_x'],r['ticks'],r['digits']) for r in cross['cross_setting_cases']]==[(7,8,444,89,[0,5,0]),(9,8,443,266,[0,5,0])]
v=json.loads((root/'evidence/p513-saves-validation.json').read_text())
proof=json.loads((root/'evidence/p513-save-proof.json').read_text())
assert v['status']=='PASS' and v['exe_sha256']==m['exe_sha256'] and v['full_suite']
assert (v['format_version'],v['payload_bytes'],v['scene'],v['full_frame_height'])==(11,5928,513,480)
assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==10
assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint'] and proof['boundaries']==v['boundaries'] and v['boundaries']>100
assert (proof['routes'],proof['scenarios'],proof['photon_results'],proof['answer_continuations'],proof['live_setting_changes'])==(5,14,9,126,2)
assert (v['solve_and_exit_routes'],v['scenarios'],v['photon_results'],v['answer_continuations'],v['live_setting_changes'])==(5,14,9,126,2)
assert (v['truncations'],v['byte_corruptions'],v['invalid_checksummed_states'])==(5928,5928,37)
assert all(v[k] for k in ('retained_stopped_photon','retained_digits','random_continuation','silent_first_success','repeated_success_count'))
for name,marker in [('p513-saves-runtime.log','P513 saves: PASS ('),('p513-saves-startup.log','P513 startup save: PASS'),('variant-previous-slot.log','variant startup save: PASS')]:
 s=(root/'evidence'/name).read_text();assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
assert json.loads((root/'evidence/variant-previous-slot-proof.json').read_text())['unchanged']
print('P513 original cube/motion observations and v11 native save evidence integrity PASS')
p517=json.loads((root/'evidence/p517-save-original.json').read_text())
assert p517['status']=='PASS' and len(p517['sprite_frames'])==11 and len(p517['conditions'])==2
assert p517['image_history_comparisons']==196 and len(p517['images'])==14 and len({p['file'] for p in p517['images']})==4
assert [r['setting'] for r in p517['settings']]==list(range(1,15))
assert [r['level'] for r in p517['settings']]==[4,3,2,1,2,3,4,3,2,1,2,3,4,3]
assert digest(Path('D:/astro/PLACES/P517/MEGAFILE.HYP'))==p517['source_sha256']
for name,expected in p517['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES/P517')/name)==expected,name
for picture in p517['images']:
 assert (picture['width'],picture['height'],picture['x'],picture['y'])==(640,320,0,0)
 assert digest(Path('D:/astro/PLACES/P517')/picture['file'])==picture['sha256']
print('P517 preparatory original resource observations integrity PASS; no native-save claim')
builder_save=json.loads((root/'evidence/builder-save-original.json').read_text())
assert builder_save['status']=='PASS' and [r['scene'] for r in builder_save['scenes']]==[515,536]
for scene in builder_save['scenes']:
 assert scene['status']=='PASS' and len(scene['conditions'])==13 and len(scene['sprite_frames'])==60
 assert scene['image_history_comparisons']==4 and scene['ignored_frame_requests']==[dict(sprite=15,requested_frame=1,loaded_frames=1)]
 assert scene['early_launch_prefix']['condition']['args']==[1,2,4,0,1,0] and scene['early_launch_prefix']['mask_assignment']['args']==[1,0,7]
 assert digest(Path(f"D:/astro/PLACES/P{scene['scene']}/MEGAFILE.HYP"))==scene['source_sha256']
 for picture in scene['images']:
  assert (picture['width'],picture['height'],picture['x'],picture['y'])==(250,330,0,0)
  assert digest(Path(f"D:/astro/PLACES/P{scene['scene']}")/picture['file'])==picture['sha256']
print('P515/P536 preparatory resource inventory integrity PASS; no native-save claim')

v=json.loads((root/'evidence/p517-saves-validation.json').read_text())
proof=json.loads((root/'evidence/p517-save-proof.json').read_text())
assert v['status']=='PASS' and v['exe_sha256']==m['exe_sha256'] and v['full_suite']
assert (v['format_version'],v['payload_bytes'],v['scene'],v['full_frame_height'])==(12,3660,517,480)
assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==11
assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint'] and proof['boundaries']==v['boundaries'] and v['boundaries']>2000
assert (proof['routes'],proof['settings'],proof['animation_cases'])==(3,14,2240)
assert (v['solve_and_exit_routes'],v['settings'],v['animation_cases'])==(3,14,2240)
assert v['truncations']==v['byte_corruptions']==proof['truncations']==proof['corruptions']==3660
assert v['invalid_checksummed_states']==proof['invalid_states'] and proof['invalid_states']>30
assert all(v[k] for k in ('active_animation','inactive_phases','next_frame_timing','first_completion_count','repeated_completion_count','minimum_clamp','unsolved_exit','music_restart'))
assert proof['music_restart'] and proof['original_wav_sha256']==p517['original_wav_sha256']
for name,marker in [('p517-saves-runtime.log','P517 saves: PASS ('),('p517-saves-startup.log','P517 startup save: PASS'),('p513-previous-slot.log','P513 startup save: PASS')]:
 s=(root/'evidence'/name).read_text();assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
assert json.loads((root/'evidence/p513-previous-slot-proof.json').read_text())['unchanged']
print('P517 v12 active and stopped aurora phase save evidence integrity PASS')
audit=json.loads((root/'evidence/builder-boundaries.json').read_text())
assert audit['status']=='PASS' and audit['exe_sha256']==m['exe_sha256'] and audit['boundaries']==len(audit['rows']) and audit['boundaries']>100
assert audit['original_inventory_sha256']==digest(root/'evidence/builder-save-original.json')
assert {r['locals'][1] for r in audit['rows'] if r['locals'][1]}=={1,2,3,4,5}
assert all(len(r['sprites'])==60 and len(r['locals'])==13 for r in audit['rows'])
for n,expected in audit['source_sha256'].items():assert digest(Path(f'D:/astro/PLACES/P{n}/MEGAFILE.HYP'))==expected
s=(root/'evidence/builder-boundaries.log').read_text()
assert 'P515/P536 interaction verification: PASS' in s and 'FAIL' not in s and 'Log closed successfully' in s
print('Builder native boundary observations integrity PASS')

v=json.loads((root/'evidence/builder-saves-validation.json').read_text())
proof=json.loads((root/'evidence/builder-save-proof.json').read_text())
assert v['status']=='PASS' and v['exe_sha256']==m['exe_sha256'] and v['full_suite']
assert (v['format_version'],v['payload_bytes'],v['scenes'],v['full_frame_height'])==(13,8960,[515,536],480)
assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==12
assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint'] and proof['boundaries']==v['boundaries'] and v['boundaries']>300
assert proof['routes']==v['routes']==6 and proof['matrix_cases']==v['matrix_cases'] and proof['matrix_cases']>=280
assert proof['fresh_scene_timer_comparisons']==v['fresh_scene_timer_comparisons'] and proof['fresh_scene_timer_comparisons']>=6
assert proof['audio_driver']=='native' and not proof['diagnostic']
assert proof['truncations']==proof['corruptions']==8960 and proof['invalid_states']>40
assert proof['variant_fixture_unchanged'] and proof['dormant_boundaries'] and proof['no_picture_boundaries']
assert all(v[k] for k in ('dormant_sequence_retained','comet_phase_retained','first_completion_count','repeated_completion_count','early_launch','p515_success_noop','music_restart'))
for name,marker in [('builder-saves-runtime.log','builder saves: PASS ('),('builder-saves-startup.log','builder startup save: PASS'),('p517-previous-slot.log','P517 startup save: PASS')]:
 s=(root/'evidence'/name).read_text();assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
assert json.loads((root/'evidence/p517-previous-slot-proof.json').read_text())['unchanged']
for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
rocket=json.loads((root/'evidence/p537-motion-validation.json').read_text())
original=json.loads((root/'evidence/p537-motion-original.json').read_text())
assert rocket['status']=='PASS' and rocket['exe_sha256']==m['exe_sha256'] and rocket['full_suite']
assert rocket['combined_fnv32']==original['combined_fnv32']=='292dc3fd' and rocket['fixtures']==96 and rocket['steps']==original['steps']==14592
assert rocket['inactive_digit_timers']==21 and rocket['original_evidence_sha256']==digest(root/'evidence/p537-motion-original.json')
readout=json.loads((root/'evidence/p537-readout-proof.json').read_text())
assert rocket['readout_proof_sha256']==digest(root/'evidence/p537-readout-proof.json')
assert readout['status']=='PASS' and not readout['diagnostic'] and readout['exe_sha256']==m['exe_sha256']
assert readout['checked_pixels']==rocket['rendered_pixels'] and readout['checked_pixels']>1000 and readout['old_shift_mismatch_pixels']>0
assert {c['setting'] for c in readout['captures']}=={1,7,11,13}
for item in readout['captures']:assert digest(root/'evidence'/('p537-readout-'+str(item['setting'])+'.png'))==item['png_sha256']

assert rocket['native_runtime_sha256']==digest(root/'evidence/runtime.log')
assert 'P537 original callback comparison: PASS (96 fixtures, 14592 steps, 292dc3fd)' in (root/'evidence/runtime.log').read_text()
print('P537 original final readout and inactive timer correction integrity PASS')
print('Builder v13 construction and dormant-sequence save evidence integrity PASS')

v=json.loads((root/'evidence/rocket-saves-validation.json').read_text());proof=json.loads((root/'evidence/rocket-save-proof.json').read_text())
assert v['status']=='PASS' and v['exe_sha256']==m['exe_sha256'] and v['full_suite']
assert (v['format_version'],v['payload_bytes'],v['scene'])==(14,7680,537)
assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==13 and not proof['diagnostic'] and proof['audio_driver']=='native'
assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint'] and proof['boundaries']==v['boundaries'] and v['boundaries']>500
assert proof['history_boundaries']>300 and proof['dormant_boundaries']>300 and proof['busy_rejections']>0
assert proof['truncations']==proof['corruptions']==7680 and proof['invalid_states']>40 and proof['variant_fixture_unchanged']
for name,marker in [('rocket-saves-runtime.log','rocket saves: PASS ('),('rocket-saves-startup.log','rocket startup save: PASS'),('builder-previous-slot.log','builder startup save: PASS')]:
 s=(root/'evidence'/name).read_text();assert marker in s and 'FAIL' not in s and 'Log closed successfully' in s
assert json.loads((root/'evidence/builder-previous-slot-proof.json').read_text())['unchanged']
audit=json.loads((root/'evidence/rocket-boundaries.json').read_text());assert audit['status']=='PASS' and audit['exe_sha256']==m['exe_sha256'] and audit['boundaries']==402
assert all(len(row['sprites'])==48 for row in audit['rows']) and {row['selector'] for row in audit['rows']}==set(range(16))
assert audit['source_sha256']==digest(Path('D:/astro/PLACES/P537/MEGAFILE.HYP'))
print('P537 v14 settled rocket saves and independent boundary evidence integrity PASS')

# Universe proof must identify this exact real engine and independently decoded movie.
v=json.loads((root/'evidence/universe-saves-validation.json').read_text());proof=json.loads((root/'evidence/universe-save-proof.json').read_text())
assert v['status']=='PASS' and v['exe_sha256']==proof['exe_sha256']==m['exe_sha256'] and v['full_suite']
assert (v['format_version'],v['payload_bytes'],v['scene'])==(15,3684,529)
assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==14 and not proof['diagnostic'] and proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
assert proof['ordinary_boundaries']>0 and proof['natural_voice_ends']>0 and proof['zero_frame_first_absent'] and proof['zero_frame_prior_residual'] and proof['extended_atomic_state'] and proof['music_restart']
assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint'] and proof['boundaries']==v['boundaries'] and v['boundaries']>100
assert proof['history_boundaries']>50 and proof['dormant_boundaries']>100 and proof['busy_rejections']>0
assert proof['truncations']==proof['corruptions']==3684 and proof['invalid_states']>=25 and proof['variant_fixture_unchanged']
for name,marker in [('universe-saves-runtime.log','universe saves: PASS ('),('universe-saves-startup.log','universe startup save: PASS'),('rocket-previous-slot.log','rocket startup save: PASS')]:
 text=(root/'evidence'/name).read_text();assert marker in text and 'FAIL' not in text and 'Log closed successfully' in text
text=(root/'evidence/universe-saves-runtime.log').read_text()
for marker in ('universe natural voice end: PASS','universe Music restart: PASS','universe extra guards: PASS','universe zero-frame history: PASS'):assert marker in text
previous=json.loads((root/'evidence/rocket-previous-slot-proof.json').read_text())
assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==m['exe_sha256']
assert previous['producing_exe_sha256']=='e1c05225769cb9411a1b849abe7530cb36ee24114a3cf65bac446c587b903d3c'
assert previous['slot_sha256']=='899116a341ff8c0480591bf1688ac9d5f671eda00fd5c1b193648aea1913b947' and previous['origin_commit']=='20aa22b8459e443f05a2b9e5fd078a6843933351'
audit_path=root/'evidence/universe-boundaries-proof.json';audit=json.loads(audit_path.read_text())
assert audit['status']=='PASS' and audit['exe_sha256']==m['exe_sha256'] and audit['boundaries']>=137 and audit['movie_samples']==proof['movie_samples']==253 and audit['actual_audio_driver']=='wasapi'
assert proof['movie_audit_proof_sha256']==digest(audit_path)
assert proof['movie_audit_log_sha256']==audit['log_sha256']==digest(root/'evidence/universe-boundaries.log')
assert audit['source_sha256']==digest(Path('D:/astro/PLACES/P529/MEGAFILE.HYP')) and audit['movie_sha256']==digest(Path('D:/astro/PLACES/P529/FUNIV.MOV'))
for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
print('P529 v15 settled universe, original MOV and zero-frame history evidence integrity PASS')

research=json.loads((root/'evidence/p522-save-original.json').read_text())
assert research['status']=='PASS' and research['source']['sha256']==digest(Path('D:/astro/PLACES/P522/MEGAFILE.HYP'))
assert research['source']['size']==483379 and research['initial_values']==[2,0] and research['command_count']==69 and len(research['sprites'])==18
assert research['recurring_program']['opcode']==41 and research['recurring_program']['args']==[0] and research['recurring_program']['delay']==200
for source in research['source_references']:assert digest(Path(source['path']))==source['sha256']
assert research['prior_original_callback_probe']['consulted_as_text_only']
print('P522 static original-resource inventory integrity PASS; no native save support claim')

audit=json.loads((root/'evidence/p522-probe-boundaries.json').read_text());build=json.loads((root/'evidence/p522-probe-audit-build-proof.json').read_text())
assert audit['status']==build['status']=='PASS' and build['diagnostic_only'] and audit['build_proof']==build
historical=json.loads((work/'verified-checkpoints/universe-dbe43465359f/checkpoint.json').read_text())
assert historical['exe_sha256']=='dbe43465359fff29a4a1931b850f463251120a71c21039e44106e64a1b6ffe7b'
assert build['regression_exe_sha256']==historical['exe_sha256'] and build['canonical_sha256']==historical['engine_sha256']
assert audit['log_sha256']==digest(root/'evidence/p522-probe-boundaries.log')
assert audit['observations']==len(audit['records'])==126 and set(map(int,audit['route_counts']))==set(range(4))
assert all(len(row['sprites'])==18 and all(len(words)==27 for words in row['sprites'].values()) for row in audit['records'])
assert audit['polling_observations']==len(audit['polls'])==5830 and audit['poll_executions']==sum(p['due'] for p in audit['polls'])==832
assert audit['after_startup_pending_counts']==[1]*4 and audit['observed_due_ages']==[210]
assert audit['hidden_probe_ordinary_motion']==105
text=(root/'evidence/p522-probe-boundaries.log').read_text()
assert 'Using SDL Audio Driver "dummy"' in text and 'Using SDL Video Driver "dummy"' in text and 'FAIL' not in text and 'Log closed successfully' in text
print('P522 historical native observation evidence integrity PASS; that audit tests no save format')


# v16 is verified only when the finalized P522 save evidence is present.
if probe_save_present:
 v=json.loads((root/'evidence/probe-saves-validation.json').read_text())
 proof=json.loads((root/'evidence/probe-save-proof.json').read_text())
 assert v['status']==proof['status']=='PASS' and v['exe_sha256']==proof['exe_sha256']==m['exe_sha256'] and v['full_suite']
 assert (v['format_version'],v['payload_bytes'],v['scene'])==(16,4472,522)
 assert proof['metadata_listed'] and proof['slot']==15 and not proof['diagnostic']
 assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
 assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint']
 assert proof['truncations']==proof['corruptions']==4472 and proof['invalid_states']>0 and proof['variant_fixture_unchanged']
 for key in ('boundaries','history_boundaries','dormant_boundaries','ordinary_boundaries'):
  assert proof[key]>0,key
  if key in v:assert proof[key]==v[key],key
 # The final driver must measure every promised continuation and guard.
 for key in ('poll_timing_cases','failed_return_boundaries','calendar_edges','flight_rejections','natural_voice_ends'):
  assert proof[key]>0,key
  if key in v:assert proof[key]==v[key],key
 assert proof['music_restart']
 for name,marker in [('probe-saves-runtime.log','probe saves: PASS'),('probe-saves-startup.log','probe startup save: PASS'),('universe-previous-slot.log','universe startup save: PASS')]:
  text=(root/'evidence'/name).read_text()
  assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.'),name
  assert 'Using SDL Audio Driver "wasapi"' in text,name
 previous=json.loads((root/'evidence/universe-previous-slot-proof.json').read_text())
 assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==m['exe_sha256']
 assert previous['audio_driver']=='wasapi'
 assert previous['producing_exe_sha256']=='dbe43465359fff29a4a1931b850f463251120a71c21039e44106e64a1b6ffe7b'
 assert previous['slot_sha256']=='654d47e01c9412b1dda09a27707bdb4778c493d62b00ff336ea233f46e6dc1e4'
 assert previous['origin_commit']=='dd687a686d5edb9d1931360b94ee568081ec0ad0'
 for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
 print('P522 v16 ordinary nonflight saves and frozen v15 continuation evidence integrity PASS')


# The fresh P514 inventory may be added before its separate save implementation.
p514_inventory=root/'evidence/p514-save-original.json'
if p514_inventory.is_file():
 research=json.loads(p514_inventory.read_text())
 assert research['status']=='PASS' and research['source']['size']==586435
 assert research['source']['sha256']==digest(Path('D:/astro/PLACES/P514/MEGAFILE.HYP'))
 assert research['command_count']==139 and len(research['sprites'])==20 and len(research['conditions'])==8
 assert research['initial_values']==[0,-1,0,54,1,0,0,0]
 assert [c[2] for c in research['conditions']]==[20,19,2,52,1,16,16,1]
 assert research['mode']==0 and research['layers']==1 and not research['movies'] and not research['mouse_rects']
 for name,reference in research['source_references'].items():assert digest(root/'engine/astronomica'/name)==reference['sha256'],name
 assert research['original_callback_probe']['consulted_as_text_only']
 assert digest(root/'probe_p514_motion.py')==research['original_callback_probe']['sha256']
 print('P514 fresh static original-resource inventory integrity PASS; separate from save validation')
if rendezvous_save_present:
 assert p514_inventory.is_file(), 'Final P514 save evidence requires its original inventory'
 v=json.loads((root/'evidence/rendezvous-saves-validation.json').read_text())
 proof=json.loads((root/'evidence/rendezvous-save-proof.json').read_text())
 assert v['status']==proof['status']=='PASS' and v['exe_sha256']==proof['exe_sha256']==m['exe_sha256'] and v['full_suite']
 assert (v['format_version'],v['payload_bytes'],v['scene'])==(17,4632,514)
 assert proof['metadata_listed'] and proof['slot']==16 and not proof['diagnostic']
 assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
 assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint']
 assert proof['truncations']==proof['corruptions']==4632 and proof['invalid_states']>0 and proof['variant_fixture_unchanged']
 for key in ('boundaries','busy_rejections','history_boundaries','dormant_boundaries','ordinary_boundaries','prelaunch_boundaries','launched_boundaries','failed_docking_boundaries','successor_checks','future_outcome_checks','timer_cases','natural_voice_ends'):
  assert proof[key]>0,key
  if key in v:assert v[key]==proof[key],key
 assert proof['speed_settings']>=16 and proof['music_restart'] and proof['extended_atomic_state']
 if 'speed_settings' in v:assert proof['speed_settings']==v['speed_settings']
 for name,marker in [('rendezvous-saves-runtime.log','rendezvous saves: PASS'),('rendezvous-saves-startup.log','rendezvous startup save: PASS'),('probe-previous-slot.log','probe startup save: PASS')]:
  text=(root/'evidence'/name).read_text()
  assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.'),name
  assert 'Using SDL Audio Driver "wasapi"' in text,name
 previous=json.loads((root/'evidence/probe-previous-slot-proof.json').read_text())
 assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==m['exe_sha256'] and previous['audio_driver']=='wasapi'
 assert previous['producing_exe_sha256']=='634c241e0d4242ad95e5915d4c77af491fe8c20b62100533e6bb82d444152bb0'
 assert previous['slot_sha256']=='8a88d6f4d7c9a5313a7fa30755be670d01fb64be5824c88f01b02f6c1d6042ee'
 assert previous['origin_commit']=='295842e695bb9e41a5c3641918af203c0062731a'
 for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
 print('P514 v17 rendezvous saves and frozen v16 continuation evidence integrity PASS')

p518_inventory=root/'evidence/p518-save-original.json'
if p518_inventory.exists():
 research=json.loads(p518_inventory.read_text())
 assert research['status']=='STATIC_ORIGINAL_INVENTORY_ONLY' and research['command_count']==111
 assert research['source']['size']==489731 and research['source']['sha256']==digest(Path('D:/astro/PLACES/P518/MEGAFILE.HYP'))
 assert research['source']['sha256']=='235de8b0fbb86b6cc1a8337779d6c6f7804e8455bce0dc607ea00092f3f6ffbd'
 assert research['mode']==0 and research['layers']==1 and len(research['sprites'])==32
 assert research['conditions']==[[1,0,20,0,0,20],[1,1,9,0,0,511],[1,2,9,1,1,9],[1,3,20,0,0,20]]
 assert research['opcode_counts']['39']==3 and '20' not in research['opcode_counts'] and not research['movies'] and not research['mouse_rects']
 for name,reference in research['source_references'].items():assert digest(root/'engine/astronomica'/name)==reference['sha256'],name
 assert research['prior_original_probe']['consulted_as_text_only'] and digest(root/'probe_p518_planets.py')==research['prior_original_probe']['sha256']
 print('P518 fresh static original resource identity/source references PASS; separate from native save proof')
if planet_save_present:
 assert p518_inventory.is_file()
 v=json.loads((root/'evidence/planet-saves-validation.json').read_text())
 proof=json.loads((root/'evidence/planet-save-proof.json').read_text())
 assert v['status']==proof['status']=='PASS' and v['exe_sha256']==proof['exe_sha256']==m['exe_sha256'] and v['full_suite']
 assert (v['format_version'],v['payload_bytes'],v['scene'])==(18,6184,518)
 assert proof['metadata_listed'] and proof['slot']==17 and not proof['diagnostic']
 assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
 assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint']
 assert proof['truncations']==proof['corruptions']==6184 and proof['invalid_states']>0 and proof['variant_fixture_unchanged']
 for key in ('boundaries','busy_rejections','history_boundaries','dormant_boundaries','ordinary_boundaries','natural_voice_ends'):
  assert proof[key]>0,key
  if key in v:assert v[key]==proof[key],key
 assert proof['music_restart'] and proof['extended_atomic_state']
 for name,marker in [('planet-saves-runtime.log','planet saves: PASS'),('planet-saves-startup.log','planet startup save: PASS'),('rendezvous-previous-slot.log','rendezvous startup save: PASS')]:
  text=(root/'evidence'/name).read_text()
  assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.'),name
  assert 'Using SDL Audio Driver "wasapi"' in text,name
 previous=json.loads((root/'evidence/rendezvous-previous-slot-proof.json').read_text())
 assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==m['exe_sha256'] and previous['audio_driver']=='wasapi'
 assert previous['producing_exe_sha256']=='33980e92277d656d45f3383af5868db2567915de53642d3f5ec08dea87ae3faa'
 assert previous['slot_sha256']=='53fba4c58fe6caf096c349fa65efba43a588feb79386895fe434f09afcf04fa0'
 assert previous['origin_commit']=='ab9094909911ca5d1f73e6ad2b0e507b67f7a10f'
 for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
 for key in ('follow_boundaries','released_boundaries','failed_arrivals','correct_arrivals','successor_checks','future_outcome_checks','exhausted_mask_checks','timer_cases'):
  assert proof[key]>0,key
  if key in v:assert proof[key]==v[key],key
 assert proof['speed_settings']>=16 and proof['count8_zero_checks']==1
 print('P518 v18 planet saves and frozen v17 continuation evidence integrity PASS')

p521_inventory=root/'evidence/p521-save-original.json'
if p521_inventory.exists():
 research=json.loads(p521_inventory.read_text())
 assert research['status']=='STATIC_ORIGINAL_PROFILE_ONLY' and research['command_count']==175
 assert research['source']['size']==717441 and research['source']['sha256']==digest(Path('D:/astro/PLACES/P521/MEGAFILE.HYP'))
 assert research['source']['sha256']=='fd9e9e50e785604aec367a90213c5454c179fa5f93e81da50bed1cf095017f47'
 assert research['mode']==0 and research['layers']==1 and research['sprite_count']==27 and research['condition_count']==0 and research['startup_program_count']==1
 assert not research['movies'] and not research['conditions']
 for name,reference in research['source_anchors'].items():
  assert digest(root/'engine/astronomica'/name)==reference['sha256'],name
  assert all(reference['references'].values()),name
 for asset in research['assets']:assert digest(Path('D:/astro/PLACES/P521')/asset['name'])==asset['sha256'],asset['name']
 print('P521 fresh original resource/asset identities and source references PASS; separate from native save proof')
if p521_save_present:
 assert p521_inventory.is_file()
 v=json.loads((root/'evidence/p521-saves-validation.json').read_text())
 proof=json.loads((root/'evidence/p521-save-proof.json').read_text())
 assert v['status']==proof['status']=='PASS' and v['exe_sha256']==proof['exe_sha256']==m['exe_sha256'] and v['full_suite']
 assert (v['format_version'],v['payload_bytes'],v['scene'])==(19,5392,521)
 assert proof['metadata_listed'] and proof['slot']==18 and not proof['diagnostic']
 assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
 assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint']
 assert proof['truncations']==proof['corruptions']==5392 and proof['invalid_states']>0 and proof['variant_fixture_unchanged']
 for key in ('boundaries','busy_rejections','history_boundaries','dormant_boundaries','ordinary_boundaries','natural_voice_ends'):
  assert proof[key]>0,key
  if key in v:assert v[key]==proof[key],key
 assert proof['music_restart'] and proof['extended_atomic_state']
 for name,marker in [('p521-saves-runtime.log','P521 saves: PASS'),('p521-saves-startup.log','P521 startup save: PASS'),('planet-previous-slot.log','planet startup save: PASS')]:
  text=(root/'evidence'/name).read_text()
  assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.'),name
  assert 'Using SDL Audio Driver "wasapi"' in text,name
 previous=json.loads((root/'evidence/planet-previous-slot-proof.json').read_text())
 assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==m['exe_sha256'] and previous['audio_driver']=='wasapi'
 assert previous['producing_exe_sha256']=='9994d088c56ed65f86de27c3681c4a5179a78a5e2c0190c52e11461c1913c601'
 assert previous['slot_sha256']=='4ac262c002979dd3bd5d2832a2c01c1ca6d728233f4287a3245ab9f5786e7e6a'
 assert previous['origin_commit']=='490a28a0e583a7978f310b27465048ce2e81e058'
 for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
 for key in ('retained_image_boundaries','fragment_history_boundaries','animation_boundaries','successor_checks','future_outcome_checks','timer_cases'):
  assert proof[key]>0,key
  if key in v:assert proof[key]==v[key],key
 assert proof['choice_controls']==5 and proof['future_outcome_checks']>=4
 print('P521 v19 saves and frozen v18 continuation evidence integrity PASS')

p509_inventory=root/'evidence/p509-save-original.json'
if p509_inventory.exists():
 research=json.loads(p509_inventory.read_text())
 assert research['status']=='STATIC_ORIGINAL_PROFILE_ONLY'
 assert (research['source']['size'],research['command_count'],research['sprite_count'],research['condition_count'],research['startup_program_count'])==(713948,312,19,17,6)
 assert research['source']['sha256']==digest(Path('D:/astro/PLACES/P509/MEGAFILE.HYP'))=='053c47d65ba963ed0b1f4fc78f088fa1678586ed6a02c6c1178772e22f572e44'
 assert research['reader_sha256']==digest(root/'astro_reader.py')
 for asset in research['assets']:assert digest(Path('D:/astro/PLACES/P509')/asset['name'])==asset['sha256'],asset['name']
 print('P509 original resource profile PASS; static evidence separate from native saves')
if p509_save_present:
 assert p509_inventory.is_file()
 v=json.loads((root/'evidence/p509-saves-validation.json').read_text())
 proof=json.loads((root/'evidence/p509-save-proof.json').read_text())
 assert v['status']==proof['status']=='PASS' and v['exe_sha256']==proof['exe_sha256']==m['exe_sha256'] and v['full_suite']
 assert (v['format_version'],v['payload_bytes'],v['scene'])==(20,4540,509)
 assert proof['metadata_listed'] and proof['slot']==19 and not proof['diagnostic']
 assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
 assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint']
 assert proof['truncations']==proof['corruptions']==4540 and proof['invalid_states']>0 and proof['variant_fixture_unchanged']
 for key in ('boundaries','busy_rejections','history_boundaries','dormant_boundaries','ordinary_boundaries','natural_voice_ends','retained_image_boundaries','target_history_boundaries','animation_boundaries','successor_checks','future_outcome_checks','timer_cases'):
  assert proof[key]>0,key
  assert v[key]==proof[key],key
 assert proof['choice_controls']==6 and proof['future_outcome_checks']>=4
 assert proof['music_state_preserved'] and proof['ambient_stays_stopped'] and proof['extended_atomic_state']
 for name,marker in [('p509-saves-runtime.log','P509 save verification: PASS'),('p509-saves-startup.log','P509 startup save: PASS'),('p521-previous-slot.log','P521 startup save: PASS')]:
  text=(root/'evidence'/name).read_text()
  assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.'),name
  assert 'Using SDL Audio Driver "wasapi"' in text,name
 previous=json.loads((root/'evidence/p521-previous-slot-proof.json').read_text())
 assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==m['exe_sha256'] and previous['audio_driver']=='wasapi'
 assert previous['producing_exe_sha256']=='c211fe7efe949995728705341bc741ed484cc5ba47f68f024ff8326789da6207'
 assert previous['slot_sha256']=='4554f711cabb0606b92fe3799db3306e25cc1eaafadca75bc3a0d545133ef5c7'
 assert previous['origin_commit']=='2e0d63a89a00447757affb086866906e5e3c6cf6'
 for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
 print('P509 v20 pending-narrator saves and genuine frozen v19 integrity PASS')

p511_inventory=root/'evidence/p511-save-original.json'
if p511_inventory.exists():
 research=json.loads(p511_inventory.read_text())
 assert research['status']=='STATIC_ORIGINAL_INVENTORY_ONLY'
 assert (research['source']['size'],research['command_count'],research['sprite_count'],research['condition_count'],research['startup_program_count'])==(635643,221,35,6,5)
 assert research['source']['sha256']==digest(Path('D:/astro/PLACES/P511/MEGAFILE.HYP'))=='c3e2e2c92289a076b686e8f6a408d9fc13fe9fdf4fad2934aaca57b4ffd7df3f'
 assert research['reader_sha256']==digest(root/'astro_reader.py')
 for asset in research['assets']:assert digest(Path('D:/astro/PLACES/P511')/asset['name'])==asset['sha256'],asset['name']
 print('P511 original resource profile PASS; static evidence separate from native saves')
if p511_save_present:
 assert p511_inventory.is_file()
 v=json.loads((root/'evidence/p511-saves-validation.json').read_text())
 proof=json.loads((root/'evidence/p511-save-proof.json').read_text())
 assert v['status']==proof['status']=='PASS' and v['exe_sha256']==proof['exe_sha256']==m['exe_sha256'] and v['full_suite']
 assert (v['format_version'],v['payload_bytes'],v['scene'])==(21,6256,511)
 assert proof['metadata_listed'] and proof['slot']==20 and not proof['diagnostic']
 assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
 assert proof['fresh_process_fingerprint']==v['fresh_process_fingerprint']
 assert proof['truncations']==proof['corruptions']==6256 and proof['invalid_states']>0 and proof['variant_fixture_unchanged']
 for key in ('boundaries','busy_rejections','history_boundaries','dormant_boundaries','ordinary_boundaries','natural_voice_ends','retained_image_boundaries','frame_history_boundaries','animation_boundaries','successor_checks','future_outcome_checks','timer_cases'):
  assert proof[key]>0,key
  assert v[key]==proof[key],key
 assert proof['choice_controls']==8 and proof['future_outcome_checks']>=4
 assert (proof['dial_settings'],proof['cloud_settings'],proof['type_settings'])==(16,14,4)
 assert proof['ambient_deadline_cases']==3 and v['ambient_deadline_cases']==3
 assert proof['music_restart'] and proof['extended_atomic_state']
 for name,marker in [('p511-saves-runtime.log','P511 save verification: PASS'),('p511-saves-startup.log','P511 startup save: PASS'),('p509-previous-slot.log','P509 startup save: PASS')]:
  text=(root/'evidence'/name).read_text()
  assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.'),name
  assert 'Using SDL Audio Driver "wasapi"' in text,name
 previous=json.loads((root/'evidence/p509-previous-slot-proof.json').read_text())
 assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==m['exe_sha256'] and previous['audio_driver']=='wasapi'
 assert previous['producing_exe_sha256']=='b4d7e936aaaf39a379ee15765b7d49c16546d805bd57a1df5f36d823e097f59f'
 assert previous['slot_sha256']=='fcb257d8c9af158d982063c91d81f5bb8bc32de3a5f055afb4031c92e5aaf0fb'
 assert previous['origin_commit']=='5f05fd1d3c9e2c1715e202e58310eb7836e782ce'
 for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
 print('P511 v21 frame-history saves and genuine frozen v20 integrity PASS')

p516_inventory=root/'evidence/p516-save-original.json'
if p516_inventory.exists():
 research=json.loads(p516_inventory.read_text())
 assert research['status']=='STATIC_ORIGINAL_INVENTORY_ONLY'
 assert (research['source']['size'],research['command_count'],research['sprite_count'],research['condition_count'],research['startup_program_count'])==(563403,133,37,3,2)
 assert research['source']['sha256']==digest(Path('D:/astro/PLACES/P516/MEGAFILE.HYP'))=='fae86ac8d36038046a9d387f8fbc28d822d2cdcacc2cdb0ab4d941d55b58ced6'
 assert research['reader_sha256']==digest(root/'astro_reader.py')
 for asset in research['assets']:assert digest(Path('D:/astro/PLACES/P516')/asset['name'])==asset['sha256']
 print('P516 original resource profile PASS; static evidence separate from native saves')
if (root/'evidence/p516-saves-validation.json').exists():
 v=json.loads((root/'evidence/p516-saves-validation.json').read_text());proof=json.loads((root/'evidence/p516-save-proof.json').read_text())
 assert v['status']==proof['status']=='PASS' and v['full_suite'] and not proof['diagnostic']
 assert v['scope']=='restricted_stopped_p516' and v['format_version']==22 and v['payload_bytes']==6944
 assert v['exe_sha256']==proof['exe_sha256']==m['exe_sha256'] and proof['metadata_listed'] and proof['slot']==21
 assert v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
 assert proof['audio_driver']=='native' and proof['actual_audio_driver']=='wasapi'
 assert proof['truncations']==proof['corruptions']==6944
 for key in ('boundaries','history_boundaries','dormant_boundaries','ordinary_boundaries','busy_rejections','invalid_states','natural_voice_ends','retained_motion_boundaries','handoff_boundaries','animation_boundaries','successor_checks','timer_cases'):
  assert proof[key]>0 and v[key]==proof[key],key
 assert proof['choice_controls']==6 and proof['future_outcome_checks']>=2
 assert (proof['direction_settings'],proof['speed_settings'])==(4,16)
 assert proof['ambient_deadline_cases']==3 and proof['music_restart'] and proof['extended_atomic_state']
 for name,marker in [('p516-saves-runtime.log','P516 save verification: PASS'),('p516-saves-startup.log','P516 startup save: PASS'),('p511-previous-slot.log','P511 startup save: PASS')]:
  text=(root/'evidence'/name).read_text()
  assert marker in text and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.'),name
  assert 'Using SDL Audio Driver "wasapi"' in text,name
 previous=json.loads((root/'evidence/p511-previous-slot-proof.json').read_text())
 assert previous['status']=='PASS' and previous['unchanged'] and previous['exe_sha256']==m['exe_sha256'] and previous['audio_driver']=='wasapi'
 assert previous['producing_exe_sha256']=='1e27c45d9b7f5f3ab780837931cc7a6b07639fac3b95d6b58d6e2bfdcce2e306'
 assert previous['slot_sha256']=='91c0948e9407c17c1c848cf88f5b8561e098dd52bea2c50462579bca673a80bc'
 assert previous['origin_commit']=='fa543e9319be616d8d946233ecb7f8e67bcc1a28'
 for name,expected in proof['original_wav_sha256'].items():assert digest(Path('D:/astro/PLACES')/name)==expected
 print('Restricted P516v22 saves and genuine frozen v21 integrity PASS')
