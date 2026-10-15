"""Verify original P505 image footprints and static/hover save requirements."""
from pathlib import Path
import argparse,hashlib,json,struct
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
raw=(a.root/'PLACES/P505/MEGAFILE.HYP').read_bytes();s=parse(raw)
assert s['mode']==0 and len(s['sprites'])==18 and len(s['scripts'])==3 and len(s['mouse_rects'])==10 and not s['movies']
assert s['conditions']==[[1,0,8,1,1,8],[1,1,8,0,0,255],[1,2,4,0,0,4],[1,3,1,1,1,1]]
scripts=list(s['scripts']);hover=[]
for i,sprite in enumerate(s['sprites']):
    assert not sprite['auto_frame'] and not sprite['auto_move'] and not sprite['drag_enabled']
    count=len(sprite['frames']) if sprite['clone']==-1 else len(s['sprites'][sprite['clone']-1]['frames'])
    assert count==(2 if i<8 and i%2==0 else 1)
    scripts.extend(sprite.get(event,[]) for event in ('click','drag','mouse_in','mouse_out'))
    if sprite.get('mouse_in') or sprite.get('mouse_out'):hover.append(i)
assert hover==[0,2,4,6]
for rect in s['mouse_rects']:
    scripts.extend(rect.get(event,[]) for event in ('click','mouse_in','mouse_out'))
commands=[c for script in scripts for c in script]
mutations=sorted({c['opcode'] for c in commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)})
assert mutations==[16,17]
pictures=[]
for i,c in enumerate(s['scripts'][1]):
    if c['opcode']!=20:continue
    cond=s['scripts'][1][i-1]
    assert cond['opcode']==31 and cond['args'][:2]==[1,0] and cond['args'][4]==0
    name,x,y=c['args'];assert (x,y)==(254,362)
    data=(a.root/'PLACES/P505'/name.upper()).read_bytes()
    assert data[:2]==b'BM' and struct.unpack_from('<ii',data,18)==(135,86)
    pictures.append(dict(choice=cond['args'][2],file=name.upper(),x=x,y=y,width=135,height=86,sha256=hashlib.sha256(data).hexdigest()))
assert [p['choice'] for p in pictures]==list(range(1,9))
assert sum(c['opcode']==20 for c in commands)==8
assert not any(c['opcode'] in (21,50) for c in commands)
a.out.write_text(json.dumps(dict(date='2026-10-15',status='PASS',source_sha256=hashlib.sha256(raw).hexdigest(),local_conditions=s['conditions'],sprite_mutation_opcodes=mutations,hover_sprite_indices=hover,hover_rectangles=10,pictures=pictures,conclusion='Eight equal-footprint opaque pictures reconstruct settled questions. Preserve hover-enter state to avoid duplicate speech and stale highlights.',limitation='Resource evidence requires native continuation and fresh-process validation.'),indent=2))
print('Original P505 save resources PASS: 8 equal-footprint pictures, 4 locals, 18 sprites, 14 hover targets')
