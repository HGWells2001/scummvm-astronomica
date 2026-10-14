"""Original resource inventory for future mid-puzzle save work, not save support."""
import argparse,hashlib,json,re
from pathlib import Path
from astro_reader import parse,FormatError
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
places=[501,502,503,504,505,506,508,509,510,511,512,513,514,515,516,517,518,519,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537]
rows=[]
for place in places:
 path=a.root/f'PLACES/P{place}/MEGAFILE.HYP';raw=path.read_bytes();tail=b''
 try:scene=parse(raw)
 except FormatError as error:
  match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(error))
  if not match:raise
  boundary=int(match[2],16);tail=raw[boundary:];assert len(tail)==int(match[1])
  scene=parse(raw[:boundary])
 scripts=[]
 def add(source,script):
  if script:scripts.append((source,script))
 for i,script in enumerate(scene['scripts']):add(f'program{i}',script)
 for i,sprite in enumerate(scene['sprites']):
  for event in ('click','drag','mouse_in','mouse_out'):add(f'sprite{i}.{event}',sprite.get(event,[]))
 for i,rect in enumerate(scene['mouse_rects']):
  for event in ('click','mouse_in','mouse_out'):add(f'rect{i}.{event}',rect.get(event,[]))
 commands=[c for _,script in scripts for c in script]
 customs=sorted({c['args'][0] for c in commands if c['opcode']==23})
 locals=[dict(index=c[1],width=c[2],initial=c[3]) for c in scene['conditions'] if c[0]==1]
 rows.append(dict(place=place,source_sha256=hashlib.sha256(raw).hexdigest(),mode=scene['mode'],local_conditions=locals,
  parsed_bytes=scene['consumed'],trailing_bytes=len(tail),trailing_sha256=hashlib.sha256(tail).hexdigest(),
  sprites=len(scene['sprites']),sprite_frames=[len(s['frames']) if 'frames' in s else None for s in scene['sprites']],
  sprite_clones=[s['clone'] for s in scene['sprites']],
  automatic_frames=[i for i,s in enumerate(scene['sprites']) if s.get('auto_frame')],
  automatic_moves=[i for i,s in enumerate(scene['sprites']) if s.get('auto_move')],
  drag_controls=[i for i,s in enumerate(scene['sprites']) if s.get('drag_enabled')],
  movies=scene['movies'],customs=customs,positive_delays=sum(c['delay']>0 for c in commands),
  local_snapshot_custom28=[source for source,script in scripts if any(c['opcode']==23 and c['args'][0]==28 for c in script)],
  sprite_mutation_opcodes=sorted({c['opcode'] for c in commands if c['opcode'] in (7,15,16,17,18,19,24,30,47,48)}),
  script_count=len(scripts),command_count=len(commands)))
assert len(rows)==35
out=dict(date='2026-10-13',scope='Static original resource inventory for 35 verified puzzle-route scenes; no mid-puzzle save implementation or completion percentage',
 trailing_note='Only the known scene prefix is inventoried. Trailing data is preserved and hashed, not interpreted; see probe_remaining_scenes.py for original loader boundary evidence.',
 original_global_only_payload='102 values omit local conditions, mutable sprites, pending scripts, movie progress, per-puzzle native state and random state.',
 rows=rows,conclusions=['No scene can be declared restorable from this static inventory alone.',
 'Even without automatic motion or movies, frame/visibility/local state changes can encode puzzle progress.',
 'Any native extension needs an explicit snapshot/restore contract and continuation tests, not just a scene reload.',
 'Custom28 is the existing narrow local/global transfer used by P524 around mentor help; it is not a general save API.'])
a.out.write_text(json.dumps(out,indent=2));print('Original puzzle save inventory:',len(rows),'resources')
for r in rows:
 if not r['movies'] and not r['automatic_moves']:print(r['place'],'locals',len(r['local_conditions']),'sprites',r['sprites'],'customs',r['customs'])
