"""Preserve the verified, intentionally not-yet-enabled comet implementation."""
from pathlib import Path
import json,hashlib
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
for name in ('comet-state','comet-motion'):
    assert (root/'evidence'/(name+'.json')).read_bytes()==(work/(name+'-repeat.json')).read_bytes(),name
log=(work/'runtime.log').read_text()
assert 'Astronomica script verification: PASS' in log and 'FAIL' not in log
assert 'comet original motion comparison: PASS' in log
note='''

## Comet movement checkpoint, 1 October 2026

P502/P503/P504 movement implemented in sprites.cpp; all30 original
trajectory hashes match the native build. Original setup research covers
1920 cases, and both original probes reproduce their saved evidence exactly.
Full native suite PASS after the movement addition. Scene dispatch and
two-layer integration remain disabled and untested as interactive routes.
See COMET-RESEARCH.md for exact behavior, limitations and integration steps.
This does not increase the29 verified route scenes or establish a whole-game
completion percentage. No new package, prototype or launcher was created.
'''
for name in ('README.md','INTERPRETER.md','NEXT-STEPS.md'):
    p=root/name
    if b'## Comet movement checkpoint, 1 October 2026' not in p.read_bytes():
        with p.open('ab') as f:f.write(note.encode('ascii'))
result=dict(status='PASS',scope='Native motion only; comet scenes remain disabled',
    original_setup_cases=1920,native_trajectories=30,original_probes_reproducible=True,
    original_state_sha256=hashlib.sha256((root/'evidence/comet-state.json').read_bytes()).hexdigest(),
    original_motion_sha256=hashlib.sha256((root/'evidence/comet-motion.json').read_bytes()).hexdigest())
(root/'evidence/comet-validation.json').write_text(json.dumps(result,indent=2))
print('Comet research checkpoint saved; native full suite PASS')
