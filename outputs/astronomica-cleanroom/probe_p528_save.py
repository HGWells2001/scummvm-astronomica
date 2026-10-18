"""Fresh original-resource save inventory for the P528 eclipse puzzle."""
from pathlib import Path
import argparse,hashlib,io,itertools,json,struct
from PIL import Image
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
folder=a.root/'PLACES/P528';raw=(folder/'MEGAFILE.HYP').read_bytes();s=parse(raw)
assert s['mode']==0 and s['layers']==1 and len(s['sprites'])==9 and not s['scripts'] and not s['mouse_rects'] and not s['movies']
assert [c[2] for c in s['conditions']]==[13,4,4,1,1]
assert [len(x['frames']) for x in s['sprites']]==[2,2,2,2,2,2,2,12,1]
assert all(not x['auto_frame'] and not x['auto_move'] and not x['drag_enabled'] for x in s['sprites'])
phases=[];images={};script=s['sprites'][4]['click']
for i,c in enumerate(script):
 if c['opcode']!=24:continue
 condition=script[i-1];assert condition['opcode']==31 and condition['args'][:2]==[1,0]
 phase=condition['args'][2];assert 0<=phase<12 and c['args'][0]==8 and c['args'][3]==11-phase
 assert script[i+1]['opcode']==23 and script[i+1]['args']==[18,0,0,0,0,0]
 pair=[]
 for at,xy in [(i+2,(87,356)),(i+4,(401,369))]:
  image=script[at];assert image['opcode']==20 and tuple(image['args'][1:])==xy and script[at+1]['opcode']==49
  name=image['args'][0].upper();data=(folder/name).read_bytes();assert data[:2]==b'BM'
  width,height=struct.unpack_from('<ii',data,18);assert width>0 and height>0
  images[name]=dict(file=name,width=width,height=height,sha256=hashlib.sha256(data).hexdigest())
  pair.append(dict(file=name,x=xy[0],y=xy[1],command_offset=image['offset']))
 phases.append(dict(phase=phase,sprite7_position=c['args'][1:3],sprite7_frame=c['args'][3],pictures=pair))
assert {x['phase'] for x in phases}==set(range(12)) and len(phases)==12
assert next(x for x in phases if x['phase']==2)['pictures'][0]['file']=='GE_S1'
assert len(images)==23
assert len({(images[row['pictures'][0]['file']]['width'],images[row['pictures'][0]['file']]['height']) for row in phases})==1
assert {(images[row['pictures'][1]['file']]['width'],images[row['pictures'][1]['file']]['height']) for row in phases}=={(143,80),(143,81)}
for row in phases:
 first,second=[dict(p,**{k:v for k,v in images[p['file']].items() if k!='file'}) for p in row['pictures']]
 assert first['x']+first['width']<=second['x'] or second['x']+second['width']<=first['x'] or first['y']+first['height']<=second['y'] or second['y']+second['height']<=first['y']
assert sum(c['opcode']==20 for sprite in s['sprites'] for event in ('click','drag','mouse_in','mouse_out') for c in sprite.get(event,[]))==24
decoded={name:Image.open(folder/name).convert('RGB') for name in images}
base=Image.new('RGB',(640,480));comparisons=0;last_pair_failures=[]
for key in ('background','control'):
 ref=s[key];assert ref and 'offset' in ref
 bitmap=Image.open(io.BytesIO(raw[ref['offset']:ref['offset']+ref['size']])).convert('RGB')
 base.paste(bitmap,(0,480-bitmap.height if key=='control' else 0))
def commit(canvas,row):
 for picture in row['pictures']:canvas.paste(decoded[picture['file']],(picture['x'],picture['y']))
for first in phases:
 for last in phases:
  continuous=base.copy();commit(continuous,first);commit(continuous,last)
  restored=base.copy();commit(restored,last)
  if continuous.tobytes()!=restored.tobytes():last_pair_failures.append([first['phase'],last['phase']])
assert len(last_pair_failures)==32
tall={name:hashlib.sha256(image.crop((0,80,143,81)).tobytes()).hexdigest() for name,image in decoded.items() if name.startswith('MO_') and image.height==81}
assert len(tall)==4 and len(set(tall.values()))==4
for sequence in itertools.product(phases,repeat=3):
 continuous=base.copy();last_tall=None
 for row in sequence:
  commit(continuous,row)
  moon=row['pictures'][1]['file']
  if decoded[moon].height==81:last_tall=moon
 restored=base.copy()
 if last_tall:restored.paste(decoded[last_tall],(401,369))
 commit(restored,sequence[-1])
 assert continuous.tobytes()==restored.tobytes();comparisons+=1
assert comparisons==1728
continuous=base.copy();last_tall=None;cycle=[]
for step in range(1,49):
 phase=(11+step)%12;row=next(row for row in phases if row['phase']==phase);commit(continuous,row)
 moon=row['pictures'][1]['file']
 if decoded[moon].height==81:last_tall=moon
 restored=base.copy()
 if last_tall:restored.paste(decoded[last_tall],(401,369))
 commit(restored,row);assert continuous.tobytes()==restored.tobytes()
 cycle.append(dict(step=step,phase=phase,last_tall_moon=last_tall,background_sha256=hashlib.sha256(continuous.tobytes()).hexdigest()))
assert cycle[0]['phase']==cycle[12]['phase']==0 and cycle[0]['last_tall_moon'] is None and cycle[12]['last_tall_moon']=='MO_S1'
assert cycle[0]['background_sha256']!=cycle[12]['background_sha256']
report=dict(date='2026-10-18',status='PASS',scope='Original serialized resources only; P528 native saves not implemented',source_sha256=hashlib.sha256(raw).hexdigest(),conditions=s['conditions'],sprite_frame_counts=[len(x['frames']) for x in s['sprites']],phases=sorted(phases,key=lambda x:x['phase']),images=sorted(images.values(),key=lambda x:x['file']),
 findings=['No startup programs, mouse rectangles, movies or automatic motion','Twelve phase branches commit two nonoverlapping image rectangles','Phase2 explicitly reuses GE_S1 alongside MO_S10; retain the original mapping','Initial phase11 can exist before any image commits; returning to phase11 later has two committed images','Original custom18 changes moon render coordinates while preserving its stored center and frame'],
 requirements=['Preserve absent-versus-committed pictures independently from local phase','Preserve both mutable render positions and sprite7 selected frame','Retain the two solved eclipse flags and repeated alignment behavior','Verify all48 phase/quadrant positions, both solve orders, duplicate success count, wrong/repeated alignment and unsolved exit','Reject pending actions/foreground audio and preflight both bitmaps before live state mutation'])
report['pixel_history_comparisons']=comparisons
report['last_pair_only_failures']=last_pair_failures
report['tall_moon_last_row_sha256']=tall
report['background_history_contract']='Keep last committed pair and last 81px moon image, or absence; restore tall moon first then the current pair'
report['pixel_comparison_scope']='Original bitmap RGB pixels on original embedded background/control; image history only, not complete native scene restoration'
report['initial_background_sha256']=hashlib.sha256(base.tobytes()).hexdigest()
report['natural_cycle_snapshots']=cycle
assert decoded['GE_S1'].size==(171,105)
strip=decoded['GE_S1'].crop((0,100,171,105)).tobytes()
colors=[tuple(strip[i:i+3]) for i in range(0,len(strip),3)]
assert len(colors)==855 and sum(c!=(0,0,0) for c in colors)==204 and len(set(colors))==22
report['legacy_debug_strip_overlap']=dict(image='GE_S1',screen_rect=[87,456,258,461],pixel_addresses=len(colors),nonblack_pixels=204,distinct_colors=22,original_rgb_sha256=hashlib.sha256(strip).hexdigest())
a.out.write_text(json.dumps(report,indent=2));print('P528 original save inventory PASS: 32 last-pair counterexamples; 1728 histories and 48 natural cycle steps; phase0 has two background histories')
