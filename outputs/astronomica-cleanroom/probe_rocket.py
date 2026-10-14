"""Reproduce P537 callback dispatch and success flag from the original EXE."""
import argparse, hashlib, json, struct
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
exe = (args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols = json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
custom = next(s for s in symbols if s['name'] == '_do_custom')
base = custom['file_offset']-custom['offset']
dispatch = {struct.unpack_from('<I',exe,base+0x72a0+4*i)[0]:struct.unpack_from('<H',exe,base+0x731c+2*i)[0] for i in range(31)}
assert dispatch[14] == 0x2e22
success_scenes = [struct.unpack_from('<i',exe,base+0x6c94+4*i)[0] for i in range(34)]
assert 537 not in success_scenes
callbacks = []
for name, start, end in [('_fxm_move_rocket_slow',0x1631,0x195b),('_fxm_move_rocket',0x195b,0x1cd8),('_fxm_move_rocket_fast',0x1cd8,0x2036)]:
    s = next(s for s in symbols if s['name'] == name)
    assert s['segment'] == 3 and s['offset'] == start
    code = exe[s['file_offset']:s['file_offset']+end-start]
    if name == '_fxm_move_rocket':
        # cmp DWORD es:[bx+0x9a],0; only orbit reports puzzle success.
        assert bytes.fromhex('66 26 83 bf 9a 00 00') in code
    callbacks.append(dict(name=name,segment=3,start=start,end=end,sha256=hashlib.sha256(code).hexdigest()))
args.out.write_text(json.dumps(dict(command=14,dispatch='4:2e22',callbacks=callbacks,
    success_global=(0x9a-10)//4,common_success_537_is_noop=True,
    settings=dict(slow=[1,10],orbit=[11,12],fast=[13,15]),
    motion_period_ms=10,frame_animation_ids=[9,29]),indent=2))
print('Original P537 rocket dispatch: PASS')
