"""Record original P515/P536 scripts and the executable's success dispatch."""
import argparse, hashlib, json, struct
from pathlib import Path
from astro_reader import parse

ap = argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--out',type=Path,required=True)
args = ap.parse_args()
exe = (args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols = json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
custom = next(x for x in symbols if x['name']=='_do_custom'); base=custom['file_offset']-custom['offset']
table = {struct.unpack_from('<I',exe,base+0x6c94+4*i)[0]:struct.unpack_from('<H',exe,base+0x6c94+4*34+2*i)[0] for i in range(34)}
assert 515 not in table and table[536] == 0x584c
setter = next(x for x in symbols if x['name']=='_SWSetCurrentFrameIndex')
setter_base = setter['file_offset']-setter['offset']
# 8:08aa compares the requested signed index with frame count; jge exits.
assert exe[setter_base+0x8aa:setter_base+0x8b3] == bytes.fromhex('66263b474b0f8daa00')
rows=[]
for place in (515,536):
    raw=(args.root/f'PLACES/P{place}/MEGAFILE.HYP').read_bytes(); scene=parse(raw)
    assert len(scene['sprites'])==60 and len(scene['scripts'])==7
    assert len(scene['sprites'][14]['frames'])==1
    for template in (4,5):
        assert any(c['opcode']==15 and c['args']==[15,1] for c in scene['scripts'][template])
    launch=scene['sprites'][7]['click']
    transition=next(i for i,c in enumerate(launch) if c['opcode']==5 and c['args']==[536])
    assert launch[transition+1]['opcode']==49 and launch[transition+1]['delay']==-1
    rows.append(dict(scene=place,resource_sha256=hashlib.sha256(raw).hexdigest(),templates=scene['scripts'],
        controls=[dict(id=i+1,xy=s['xy'],commands=s['click']) for i,s in enumerate(scene['sprites']) if s.get('click_enabled')]))
args.out.write_text(json.dumps(dict(status='Original resource and executable evidence; native routes verified separately',
    success_dispatch={515:'default no operation',536:'global31, first success only'},
    scene_transition='Opcode5 stores the destination; opcode49 displays the previously staged image before scene reload',
    scenes=rows),indent=2))
print('Original builder evidence: PASS (P515/P536, 60 sprites each, deferred image display, success dispatch)')

