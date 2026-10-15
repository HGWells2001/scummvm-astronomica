"""Verify original P508 resources needed by settled native save reconstruction."""
from pathlib import Path
import argparse,hashlib,json,struct
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
p=a.root/'PLACES/P508/MEGAFILE.HYP';raw=p.read_bytes();s=parse(raw)
assert s['mode']==0 and len(s['sprites'])==23 and len(s['scripts'])==3 and not s['movies']
assert [c[:4] for c in s['conditions']]==[[1,0,18,1],[1,1,18,0],[1,2,1,1],[1,3,3,0],[1,4,8,0],[1,5,10,0]]
scripts=list(s['scripts'])
for i,sprite in enumerate(s['sprites']):
    assert not sprite['auto_frame'] and not sprite['auto_move'] and not sprite['drag_enabled']
    count=len(sprite['frames']) if sprite['clone']==-1 else len(s['sprites'][sprite['clone']-1]['frames'])
    assert count==(2 if i<4 else 1)
    scripts.extend(sprite.get(event,[]) for event in ('click','drag','mouse_in','mouse_out'))
assert not s['mouse_rects']
commands=[c for script in scripts for c in script]
mutations=sorted({c['opcode'] for c in commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)})
assert mutations==[16,17]
pictures=[]
for i,c in enumerate(s['scripts'][1]):
    if c['opcode']!=20:continue
    cond=s['scripts'][1][i-1]
    assert cond['opcode']==31 and cond['args'][:2]==[1,0] and cond['args'][4]==0
    name,x,y=c['args'];assert (x,y)==(67,354)
    image=a.root/'PLACES/P508'/name.upper();data=image.read_bytes()
    assert data[:2]==b'BM' and struct.unpack_from('<ii',data,18)==(508,108)
    pictures.append(dict(choice=cond['args'][2],file=name.upper(),x=x,y=y,width=508,height=108,sha256=hashlib.sha256(data).hexdigest()))
assert [p['choice'] for p in pictures]==list(range(1,19))
assert sum(c['opcode']==20 for c in commands)==18
assert not any(c['opcode'] in (21,50) for c in commands)
a.out.write_text(json.dumps(dict(date='2026-10-15',status='PASS',source_sha256=hashlib.sha256(raw).hexdigest(),
    local_conditions=s['conditions'],sprite_mutation_opcodes=mutations,button_frame_counts=[2]*4,
    other_sprite_frame_count=1,pictures=pictures,
    conclusion='At settled question boundaries, each new opaque picture fully replaces the same original rectangle; no pixel history is needed. Only visibility is mutated by serialized sprite commands. Input button pulses must have completed.',
    limitation='Static resource evidence does not replace continuation, corruption or fresh-process native save tests.'),indent=2))
print('Original P508 save resources PASS: 18 equal-footprint pictures, 6 locals, 23 sprites')
