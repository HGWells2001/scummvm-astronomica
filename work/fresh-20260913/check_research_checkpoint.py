"""Check research fixture consistency without treating it as playable support."""
from pathlib import Path
import json
root=Path('outputs/astronomica-cleanroom/evidence');work=Path('work/fresh-20260913')
assert (root/'comet-state.json').read_bytes()==(work/'comet-state-repeat.json').read_bytes()
setup=json.loads((root/'p516-setup.json').read_text());assert setup['cases']==128
collisions=json.loads((root/'p516-collision.json').read_text());assert collisions['cases']==64
hits=[row for row in collisions['rows'] if row['solved']]
assert len(hits)==2 and {row['input'][0] for row in hits}=={17,18}
assert all(row['sounds']==[9] and row['explosions']==[[23,52,52,10]] for row in hits)
motion=json.loads((root/'p516-motion.json').read_text())
assert motion['duration']==20000 and motion['fnv1a32']=='0x7780b563'
assert len(motion['visibility_events'])==34
for row in motion['visibility_events']:
 v=row['visible'];assert len(v)==8
 for i in range(4):assert v[i]+v[7-i]==1
print('Original research consistency: PASS; P516 remains unimplemented')
