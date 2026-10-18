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
assert save_coverage['whole_game_completion_percent'] is None and save_coverage['supported_puzzle_route_scenes']==4
assert {row['scene'] for row in save_coverage['puzzle_saves']}=={505,508,519,524}
for row in save_coverage['puzzle_saves']:
 assert digest(root/row['validation_file'])==row['validation_sha256']
 assert digest(root/f"evidence/p{row['scene']}-saves-runtime.log")==row['runtime_sha256']
 assert digest(root/f"evidence/p{row['scene']}-saves-startup.log")==row['startup_sha256']
print('Measured native save coverage integrity PASS')
