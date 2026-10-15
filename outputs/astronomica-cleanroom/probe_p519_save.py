"""Bound P519 background history from original serialized image commands."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct
from PIL import Image
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
p=a.root/'PLACES/P519';raw=(p/'MEGAFILE.HYP').read_bytes();s=parse(raw)
assert s['mode']==0 and len(s['sprites'])==27 and len(s['mouse_rects'])==10 and not s['movies']
scripts=[(f'program{i}',x) for i,x in enumerate(s['scripts'])]
for kind,items in [('sprite',s['sprites']),('rect',s['mouse_rects'])]:
 for i,item in enumerate(items):
  for event in ('click','drag','mouse_in','mouse_out'):
   if item.get(event):scripts.append((f'{kind}{i}.{event}',item[event]))
assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled'] for x in s['sprites'])
images={};commands=[]
for source,script in scripts:
 for i,c in enumerate(script):
  if c['opcode']!=20:continue
  name,x,y=c['args'];data=(p/name.upper()).read_bytes();assert data[:2]==b'BM'
  width,height=struct.unpack_from('<ii',data,18)
  assert (x,y,width,height) in [(258,356,143,108),(282,358,99,99)]
  assert i+1<len(script) and script[i+1]['opcode']==49
  images[name]=dict(file=name.upper(),x=x,y=y,width=width,height=height,sha256=hashlib.sha256(data).hexdigest())
  commands.append(dict(source=source,offset=c['offset'],image=name))
assert len(images)==10 and len(commands)==15
assert s['scripts'][0][0]['args']==['black_b',258,356]
# Every small footprint lies strictly inside the large footprint. Therefore a
# new large image erases every earlier image; only the last subsequent small
# image can contribute pixels. Record this geometry, not inferred playability.
large=[n for n,r in images.items() if r['width']==143];small=[n for n,r in images.items() if r['width']==99]
assert len(large)==5 and len(small)==5
assert 258<=282 and 356<=358 and 282+99<=258+143 and 358+99<=356+108
all_commands=[c for _,script in scripts for c in script]
mutations=sorted({c['opcode'] for c in all_commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)})
assert mutations==[15,16,17]
decoded={name:Image.open(p/row['file']).convert('RGB') for name,row in images.items()}
comparisons=0;pixels=set()
for sequence in itertools.product(images,repeat=3):
 full=decoded['black_b'].copy();last_large='black_b';last_small=None
 for name in sequence:
  row=images[name];full.paste(decoded[name],(row['x']-258,row['y']-356))
  if name in large:last_large=name;last_small=None
  else:last_small=name
 restored=decoded[last_large].copy()
 if last_small:restored.paste(decoded[last_small],(24,2))
 assert full.tobytes()==restored.tobytes(),sequence
 pixels.add(hashlib.sha256(full.tobytes()).hexdigest());comparisons+=1
assert comparisons==1000
a.out.write_text(json.dumps(dict(date='2026-10-15',status='PASS',source_sha256=hashlib.sha256(raw).hexdigest(),local_conditions=s['conditions'],sprite_count=27,rectangle_count=10,sprite_mutation_opcodes=mutations,images=list(images.values()),image_commands=commands,large_images=large,small_images=small,pixel_sequence_comparisons=comparisons,distinct_composition_sha256=sorted(pixels),background_contract='Keep latest large image and latest small image since that large image, or none. Large image replaces all prior image pixels; small image replaces all prior small-image pixels.',remaining_requirements=['Track both image identities at opcode49 commit, not opcode20 staging','Store frame selections including frame2, visibility and hover entered flags','Reject queued work, blocking speech, button pulses and flash before admitting save','Validate atomic load and continuation at detector selection, target selection, errors and solved-pair boundaries'],limitation='Resource proof and proposed contract only; P519 saves remain unsupported.'),indent=2))
print('Original P519 save geometry PASS: two nested footprints, 1000 original-pixel composition comparisons')
