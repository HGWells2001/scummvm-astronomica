"""Derive the finite settled P528 state graph from original control prefixes.

The graph abstracts clocks, counters, sprites and audio. It is a resource
analysis reference for future native save tests, not a playable runtime.
"""
from pathlib import Path
from collections import deque
import argparse,hashlib,json,struct
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--answers',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
folder=a.root/'PLACES/P528';raw=(folder/'MEGAFILE.HYP').read_bytes();s=parse(raw)
answers=json.loads(a.answers.read_text());assert answers['status']=='PASS' and answers['resource_sha256']==hashlib.sha256(raw).hexdigest()
answer_map={(r['phase'],r['quadrant'],*r['before']):r for r in answers['cases']}
assert len(answer_map)==192
for button,local,delta,wrap_at,wrap_to in ((4,0,1,12,0),(5,1,-1,-1,3)):
 commands=s['sprites'][button]['click']
 assert [c['opcode'] for c in commands[:6]]==[28,9,46,31,32,42]
 assert commands[2]['args']==[1,local,delta]
 assert commands[3]['args']==[1,local,wrap_at,0,0,0]
 assert commands[4]['args']==[1,local,wrap_to]
 assert sum(c['opcode']==46 for c in commands)==1
 # Apart from the tested rotation/wrap, these controls do not modify locals.
 assert sum(c['opcode']==32 for c in commands)==1
 assert all(c['opcode']!=23 or c['args']==[18,0,0,0,0,0] for c in commands)
pairs={};image_hashes={}
commands=s['sprites'][4]['click']
for i,c in enumerate(commands):
 if c['opcode']!=24:continue
 condition=commands[i-1];assert condition['opcode']==31 and condition['args'][:2]==[1,0]
 phase=condition['args'][2];earth,moon=commands[i+2],commands[i+4]
 assert earth['opcode']==moon['opcode']==20 and earth['args'][1:]==[87,356] and moon['args'][1:]==[401,369]
 name=moon['args'][0].upper();data=(folder/name).read_bytes();width,height=struct.unpack_from('<ii',data,18)
 assert width==143 and height in (80,81)
 pairs[phase]=dict(earth=earth['args'][0].upper(),moon=name,tall=height==81)
 image_hashes[name]=hashlib.sha256(data).hexdigest()
assert len(pairs)==12
# No image commit in the quadrant or answer controls.
assert all(c['opcode']!=20 for button in (5,6) for c in s['sprites'][button]['click'])
initial=(11,0,0,0,False,'');queue=deque([initial]);paths={initial:[]};edges=[]
while queue:
 state=queue.popleft();phase,quadrant,first,second,committed,tall=state
 for action in ('phase','quadrant','answer'):
  target=list(state);terminal=False;sound=None
  if action=='phase':
   target[0]=(phase+1)%12;target[4]=True
   if pairs[target[0]]['tall']:target[5]=pairs[target[0]]['moon']
  elif action=='quadrant':target[1]=(quadrant-1)%4
  else:
   response=answer_map[phase,quadrant,first,second]
   target[2:4]=response['after'];terminal=bool(response['result']);sound=response['sound']
  target=tuple(target)
  edges.append(dict(source=list(state),action=action,target=list(target),departure_to=526 if terminal else None,sound=sound))
  if not terminal and target not in paths:paths[target]=paths[state]+[action];queue.append(target)
assert len(paths)==160 and len(edges)==480 and sum(e['departure_to'] is not None for e in edges)==6
assert all(not (state[2] and state[3]) for state in paths)
absent=[s for s in paths if not s[4]];assert len(absent)==4 and all(s[0]==11 and s[2:4]==(0,0) and not s[5] for s in absent)
tall_by_phase={phase:sorted({s[5] for s in paths if s[0]==phase and s[4]}) for phase in range(12)}
assert tall_by_phase=={0:['','MO_S1'],1:['MO_S11'],2:['MO_S10'],**{p:['MO_S10'] for p in range(3,10)},10:['MO_S2'],11:['MO_S1']}
geometry={(s[0],s[1],s[4],s[5]) for s in paths};assert len(geometry)==56
report=dict(date='2026-10-18',status='PASS',scope='Finite resource-derived settled-state abstraction, not native save/load coverage',
 source_sha256=hashlib.sha256(raw).hexdigest(),answer_reference_sha256=hashlib.sha256(a.answers.read_bytes()).hexdigest(),original_moon_sha256=image_hashes,
 state_fields=['phase','quadrant','first_flag','second_flag','pictures_committed','last_tall_moon'],initial=list(initial),
 state_count=len(paths),edge_count=len(edges),completion_edges=6,geometry_history_count=len(geometry),absent_picture_states=len(absent),
 tall_history_by_phase=tall_by_phase,states=[dict(values=list(state),shortest_actions=path) for state,path in sorted(paths.items())],edges=edges,
 omissions=['Clocks, elapsed audio, globals, completion counter, RNG, hover and sprite snapshot fields are not graph variables','No bitmap pixels or native scene restoration are checked here; see the separate original-image history proof','Entry from other scenes and loading are not transitions in this graph'])
a.out.write_text(json.dumps(report,indent=2))
print('P528 settled abstraction PASS: 160 reachable states, 480 control edges, 6 departures, 56 geometry/history combinations')
