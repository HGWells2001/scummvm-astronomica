"""Independent original-instruction digests for native P523 differential tests."""
import itertools,json,collections
import probe_p523_callbacks as callbacks
import probe_p523_spread as spread
from probe_p526_motion import args

def fold(h,values):
 for v in values:h=((h^(v&0xffffffff))*16777619)&0xffffffff
 return h
ops=['_SetMovieActiveSegment','_CallMeWhen','_show','_hide','_hide_em','_StartMovie','_StopMovie','_puzzle_successful']
h=2166136261;count=0
for event in range(1,20):
 for channels in itertools.product((0,19,20,29,30,39,40,59,60,74,75,99),repeat=3):
  for buttons in range(4):
   for solved in (0,1):
    r=callbacks.run(event,channels,buttons,solved);h=fold(h,[len(r['calls'])]);count+=1
    for c in r['calls']:
     op=ops.index(c['name']);values=[]
     if op==0:
      values=c.get('malformed_word_arguments',[c['start'],c['duration']])
     elif op==1:values=[c['slot'],c['event'],c['time']]
     elif op in (2,3):values=[c['sprite']]
     h=fold(h,[op]+values+[0]*(3-len(values)))
    h=fold(h,[0 if r['place']==523 else r['place']])
callback_hash=h;h=2166136261;seen={(33,33,33)};queue=collections.deque(seen);edges=0
while queue:
 state=queue.popleft()
 for button in range(1,7):
  target=spread.step(state,button);edges+=1;h=fold(h,[*state,button,*target])
  if target not in seen:seen.add(target);queue.append(target)
out=dict(status='Original instruction reference, not native results',callback_cases=count,
 compatibility_repair='event8 failure: original word arguments 3721/80 replace malformed 32-bit call',callback_hash=hex(callback_hash),spread_states=len(seen),spread_edges=edges,spread_hash=hex(h))
args.out.write_text(json.dumps(out,indent=2));print(out)
