"""Record measured native save coverage separately from whole-game progress."""
from pathlib import Path
import hashlib,json
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inventory=json.loads((root/'evidence/puzzle-save-requirements.json').read_text())
rows=[]
for place,version,size,slot in [(508,3,2464,2),(505,4,2472,3),(519,5,2584,4),(524,6,2612,5),(526,7,4956,6),(528,8,3444,7),(530,9,5604,8),(513,11,5928,10),(517,12,3660,11)]:
 validation=root/f'evidence/p{place}-saves-validation.json';v=json.loads(validation.read_text())
 proof=json.loads((root/f'evidence/p{place}-save-proof.json').read_text())
 assert v['status']=='PASS' and proof['metadata_listed'] and proof['slot']==slot
 assert v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
 log=root/f'evidence/p{place}-saves-runtime.log';startup=root/f'evidence/p{place}-saves-startup.log'
 assert f'P{place} save verification: PASS' in log.read_text() and 'FAIL' not in log.read_text()
 assert f'P{place} startup save: PASS' in startup.read_text() and 'FAIL' not in startup.read_text()
 rows.append(dict(scene=place,version=version,payload_bytes=size,test_slot=slot,scope='Settled native puzzle boundaries; no pending foreground work',
  validation_file=validation.relative_to(root).as_posix(),validation_sha256=digest(validation),runtime_sha256=digest(log),startup_sha256=digest(startup),fresh_process_fingerprint=proof['fresh_process_fingerprint']))
validation=root/'evidence/variant-saves-validation.json';v=json.loads(validation.read_text())
proof=json.loads((root/'evidence/variant-save-proof.json').read_text())
assert v['status']=='PASS' and proof['metadata_listed'] and proof['slot']==9 and v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
log=root/'evidence/variant-saves-runtime.log';startup=root/'evidence/variant-saves-startup.log'
assert 'variant save verification: PASS' in log.read_text() and 'FAIL' not in log.read_text()
assert 'variant startup save: PASS' in startup.read_text() and 'FAIL' not in startup.read_text()
for place,size in ((506,3992),(531,3992),(532,3776),(533,3776),(534,4424),(535,3776)):
 rows.append(dict(scene=place,version=10,payload_bytes=size,test_slot=9,family='custom17',scope='Settled partial solutions; all six scenes in memory; one representative family slot in a fresh process',
  validation_file=validation.relative_to(root).as_posix(),validation_sha256=digest(validation),runtime_file=log.relative_to(root).as_posix(),runtime_sha256=digest(log),
  startup_file=startup.relative_to(root).as_posix(),startup_sha256=digest(startup),fresh_process_fingerprint=proof['fresh_process_fingerprint']))
validation=root/'evidence/builder-saves-validation.json';v=json.loads(validation.read_text())
proof=json.loads((root/'evidence/builder-save-proof.json').read_text())
assert v['status']=='PASS' and proof['metadata_listed'] and proof['slot']==12 and v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
log=root/'evidence/builder-saves-runtime.log';startup=root/'evidence/builder-saves-startup.log'
assert 'builder save verification: PASS' in log.read_text() and 'FAIL' not in log.read_text()
assert 'builder startup save: PASS' in startup.read_text() and 'FAIL' not in startup.read_text()
for place in (515,536):
 rows.append(dict(scene=place,version=13,payload_bytes=8960,test_slot=12,family='builder',scope='Settled construction; both scenes in memory and partial P536 in a fresh process; dormant custom17 sequence retained',
  validation_file=validation.relative_to(root).as_posix(),validation_sha256=digest(validation),runtime_file=log.relative_to(root).as_posix(),runtime_sha256=digest(log),
  startup_file=startup.relative_to(root).as_posix(),startup_sha256=digest(startup),fresh_process_fingerprint=proof['fresh_process_fingerprint']))
validation=root/'evidence/rocket-saves-validation.json';v=json.loads(validation.read_text())
proof=json.loads((root/'evidence/rocket-save-proof.json').read_text())
assert v['status']=='PASS' and proof['metadata_listed'] and proof['slot']==13 and v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
log=root/'evidence/rocket-saves-runtime.log';startup=root/'evidence/rocket-saves-startup.log'
assert 'rocket save verification: PASS' in log.read_text() and 'FAIL' not in log.read_text()
assert 'rocket startup save: PASS' in startup.read_text() and 'FAIL' not in startup.read_text()
rows.append(dict(scene=537,version=14,payload_bytes=7680,test_slot=13,scope='Settled selector and failed-return boundaries; previous readout and motion epoch preserved; no mid-launch saving',
 validation_file=validation.relative_to(root).as_posix(),validation_sha256=digest(validation),runtime_file=log.relative_to(root).as_posix(),runtime_sha256=digest(log),
 startup_file=startup.relative_to(root).as_posix(),startup_sha256=digest(startup),fresh_process_fingerprint=proof['fresh_process_fingerprint']))

validation=root/'evidence/universe-saves-validation.json';v=json.loads(validation.read_text())
proof=json.loads((root/'evidence/universe-save-proof.json').read_text())
assert v['status']=='PASS' and proof['metadata_listed'] and proof['slot']==14 and v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
log=root/'evidence/universe-saves-runtime.log';startup=root/'evidence/universe-saves-startup.log'
assert 'universe save verification: PASS' in log.read_text() and 'FAIL' not in log.read_text()
assert 'universe startup save: PASS' in startup.read_text() and 'FAIL' not in startup.read_text()
rows.append(dict(scene=529,version=15,payload_bytes=3684,test_slot=14,scope='Settled universe boundaries; last presented original movie frame independent of selector and attempted segment',
 validation_file=validation.relative_to(root).as_posix(),validation_sha256=digest(validation),runtime_file=log.relative_to(root).as_posix(),runtime_sha256=digest(log),
 startup_file=startup.relative_to(root).as_posix(),startup_sha256=digest(startup),fresh_process_fingerprint=proof['fresh_process_fingerprint']))

# Only count P522 after the exact official native evidence exists.
probe_validation=root/'evidence/probe-saves-validation.json'
if probe_validation.exists():
 v=json.loads(probe_validation.read_text());proof=json.loads((root/'evidence/probe-save-proof.json').read_text())
 assert v['status']=='PASS' and v['full_suite'] and proof['metadata_listed'] and proof['slot']==15
 assert v['exe_sha256']==proof['exe_sha256']==digest(work/'build/Releasex64/scummvm.exe')
 assert v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
 log=root/'evidence/probe-saves-runtime.log';startup=root/'evidence/probe-saves-startup.log'
 assert 'probe save verification: PASS' in log.read_text() and 'FAIL' not in log.read_text()
 assert 'probe startup save: PASS' in startup.read_text() and 'FAIL' not in startup.read_text()
 rows.append(dict(scene=522,version=16,payload_bytes=v['payload_bytes'],test_slot=15,
  scope='Ordinary nonflight P522 boundaries; recurring poll, orbit and calendar epochs retained; flight excluded',
  validation_file=probe_validation.relative_to(root).as_posix(),validation_sha256=digest(probe_validation),
  runtime_file=log.relative_to(root).as_posix(),runtime_sha256=digest(log),startup_file=startup.relative_to(root).as_posix(),
  startup_sha256=digest(startup),fresh_process_fingerprint=proof['fresh_process_fingerprint']))

rendezvous_validation=root/'evidence/rendezvous-saves-validation.json'
if rendezvous_validation.exists():
 v=json.loads(rendezvous_validation.read_text());proof=json.loads((root/'evidence/rendezvous-save-proof.json').read_text())
 assert v['status']=='PASS' and v['full_suite'] and proof['metadata_listed'] and proof['slot']==16
 assert v['exe_sha256']==proof['exe_sha256']==digest(work/'build/Releasex64/scummvm.exe')
 assert v['fresh_process_fingerprint']==proof['fresh_process_fingerprint']
 log=root/'evidence/rendezvous-saves-runtime.log';startup=root/'evidence/rendezvous-saves-startup.log'
 assert 'rendezvous save verification: PASS' in log.read_text() and 'FAIL' not in log.read_text()
 assert 'rendezvous startup save: PASS' in startup.read_text() and 'FAIL' not in startup.read_text()
 rows.append(dict(scene=514,version=17,payload_bytes=v['payload_bytes'],test_slot=16,
  scope='Settled P514 boundaries, including active orbit/fuel motion and hidden failed-docking history; queued transitions excluded',
  validation_file=rendezvous_validation.relative_to(root).as_posix(),validation_sha256=digest(rendezvous_validation),
  runtime_file=log.relative_to(root).as_posix(),runtime_sha256=digest(log),startup_file=startup.relative_to(root).as_posix(),
  startup_sha256=digest(startup),fresh_process_fingerprint=proof['fresh_process_fingerprint']))

supported={row['scene'] for row in rows};all_scenes={row['place'] for row in inventory['rows']}
assert supported<=all_scenes
result=dict(date='2026-10-22' if probe_validation.exists() else '2026-10-21',status='PASS',exe_sha256=digest(work/'build/Releasex64/scummvm.exe'),
 engine_sha256={p.name:digest(p) for p in sorted((root/'engine/astronomica').iterdir()) if p.is_file()},
 exploration=dict(read_versions=[1,2],write_version=2,scope='Settled mode1 exploration screens; v1 inactive countdown compatibility'),
 puzzle_saves=rows,supported_puzzle_route_scenes=len(supported),inventoried_puzzle_route_scenes=len(all_scenes),
 unsupported_puzzle_route_scenes=sorted(all_scenes-supported),whole_game_completion_percent=None,
 limitations=['These 35 route scenes include variants and are not a count of distinct puzzles','The supported save scenes are a feature-specific count, not whole-game completion','Ambient sample position is not retained','Complete manual audiovisual playthrough remains outstanding'])
(root/'evidence/native-save-coverage.json').write_text(json.dumps(result,indent=2))
print(f'Native save coverage: {len(supported)} supported puzzle scenes; no global completion percentage')
