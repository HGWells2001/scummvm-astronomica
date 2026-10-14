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
assert 'FAIL' not in help_log and 'Log closed successfully' in help_log
help_validation=json.loads((root/'evidence/help-native-validation.json').read_text())
assert help_validation['inline_images']==31 and help_validation['original_exponent_runs']==13
legacy=json.loads((root/'evidence/legacy-validation.json').read_text())
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
