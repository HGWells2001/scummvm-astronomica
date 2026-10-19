"""Record measured native save coverage separately from whole-game progress."""
from pathlib import Path
import hashlib,json
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inventory=json.loads((root/'evidence/puzzle-save-requirements.json').read_text())
rows=[]
for place,version,size,slot in [(508,3,2464,2),(505,4,2472,3),(519,5,2584,4),(524,6,2612,5),(526,7,4956,6),(528,8,3444,7),(530,9,5604,8)]:
 validation=root/f'evidence/p{place}-saves-validation.json';v=json.loads(validation.read_text())
 proof=json.loads((root/f'evidence/p{place}-save-proof.json').read_text())
 assert v['status']=='PASS' and proof['metadata_listed'] and proof['slot']==slot
 assert v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
 log=root/f'evidence/p{place}-saves-runtime.log';startup=root/f'evidence/p{place}-saves-startup.log'
 assert f'P{place} save verification: PASS' in log.read_text() and 'FAIL' not in log.read_text()
 assert f'P{place} startup save: PASS' in startup.read_text() and 'FAIL' not in startup.read_text()
 rows.append(dict(scene=place,version=version,payload_bytes=size,test_slot=slot,scope='Settled native puzzle boundaries; no pending foreground work',
  validation_file=validation.relative_to(root).as_posix(),validation_sha256=digest(validation),runtime_sha256=digest(log),startup_sha256=digest(startup),fresh_process_fingerprint=proof['fresh_process_fingerprint']))
supported={row['scene'] for row in rows};all_scenes={row['place'] for row in inventory['rows']}
assert supported<=all_scenes
result=dict(date='2026-10-18',status='PASS',exe_sha256=digest(work/'build/Releasex64/scummvm.exe'),
 engine_sha256={p.name:digest(p) for p in sorted((root/'engine/astronomica').iterdir()) if p.is_file()},
 exploration=dict(read_versions=[1,2],write_version=2,scope='Settled mode1 exploration screens; v1 inactive countdown compatibility'),
 puzzle_saves=rows,supported_puzzle_route_scenes=len(supported),inventoried_puzzle_route_scenes=len(all_scenes),
 unsupported_puzzle_route_scenes=sorted(all_scenes-supported),whole_game_completion_percent=None,
 limitations=['These 35 route scenes include variants and are not a count of distinct puzzles','The supported save scenes are a feature-specific count, not whole-game completion','Ambient sample position is not retained','Complete manual audiovisual playthrough remains outstanding'])
(root/'evidence/native-save-coverage.json').write_text(json.dumps(result,indent=2))
print('Native save coverage: seven supported puzzle scenes; versions 1-9 readable; no global completion percentage')
