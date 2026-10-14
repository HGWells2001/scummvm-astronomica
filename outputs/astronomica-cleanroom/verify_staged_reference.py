"""References for all 18 original P508 image choices."""
import argparse,json
from pathlib import Path
from astro_reader import parse
from verify_move_reference import generate
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
s=parse((args.root/'PLACES/P508/MEGAFILE.HYP').read_bytes());commands=s['scripts'][1]
patches=[(c['args'][0].upper(),c['args'][1],c['args'][2]) for c in commands if c['opcode']==20]
assert len(patches)==18 and commands[-1]['opcode']==49 and commands[-1]['delay']==0
pos=tuple(s['sprites'][0]['xy']);rows=generate(args.root,args.out,508,1,(pos,)*18,background_patches=patches)
(args.out/'choices.json').write_text(json.dumps([dict(choice=i+1,file=p[0],hashes=r['hashes']) for i,(p,r) in enumerate(zip(patches,rows))],indent=2))
print('Verified',len(rows),'P508 references')
