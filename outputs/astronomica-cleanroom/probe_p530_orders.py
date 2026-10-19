"""Derive P530 answer dispatch for each final component from original scripts."""
from pathlib import Path
import argparse,hashlib,json
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
raw=(a.root/'PLACES/P530/MEGAFILE.HYP').read_bytes();s=parse(raw)
programs={}
for index in range(2,7):
 commands=s['scripts'][index];rows={};choice=None;picture=None
 for c in commands:
  if c['opcode']==31 and c['args'][:2]==[1,10]:choice=c['args'][2];picture=None
  elif choice in range(1,6) and c['opcode']==20:picture=c['args'][0].upper()
  elif choice in range(1,6) and c['opcode']==9:
   assert choice not in rows and c['args'][0] in (9,10)
   assert picture
   rows[choice]=dict(detector=choice,sound=c['args'][0]-1,sound_offset=c['offset'],correct=c['args'][0]==10,picture=picture)
 assert set(rows)==set(range(1,6)) and sum(row['correct'] for row in rows.values())==1
 assert all('picture' in row for row in rows.values())
 programs[index]=rows
dispatch={}
for sprite in (19,20,21,22):
 commands=s['sprites'][sprite]['click'];mapping={}
 for i,c in enumerate(commands[:-1]):
  if c['opcode']==31 and c['args'][:2]==[1,9]:
   call=commands[i+1];assert call['opcode']==41 and call['args'][0] in programs
   mapping[c['args'][2]]=call['args'][0]
 assert set(mapping)==set(range(1,6));dispatch[sprite]=mapping
cases=[]
for sprite,mapping in dispatch.items():
 for scenario,program in mapping.items():
  for detector,row in programs[program].items():cases.append(dict(last_sprite=sprite,scenario=scenario,program=program,**row))
assert len(cases)==100
answers={str(sprite):[next(row['detector'] for row in cases if row['last_sprite']==sprite and row['scenario']==scenario and row['correct']) for scenario in range(1,6)] for sprite in dispatch}
assert answers=={'19':[2,4,5,1,4],'20':[2,4,5,1,4],'21':[2,4,5,1,4],'22':[2,1,5,4,4]}
report=dict(date='2026-10-19',status='PASS',scope='Static original script dispatch; not execution or complete input-history coverage',source_sha256=hashlib.sha256(raw).hexdigest(),cases=cases,case_count=100,correct_detectors_by_last_sprite=answers,
 finding='Placing component B (sprite22) last swaps the response programs for scenarios2/4/5 relative to placing the detector or component A last; scenarios2/4 have different correct detectors',
 requirements=['Test all six A/B/detector placement permutations','Retain partial selections and placed-component flags exactly','Do not normalize the original order-dependent answer mapping'])
a.out.write_text(json.dumps(report,indent=2));print('P530 original order dispatch PASS:100 responses; component-B-last changes correct detectors for scenarios2/4')
