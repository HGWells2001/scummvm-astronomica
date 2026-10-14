"""Independent original BMP patches composed before static sprites."""
import argparse,json
from pathlib import Path
from astro_reader import parse
from verify_move_reference import generate
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
rows=[]
for place,patches in [(505,[('APOLLO',254,362),('CAVE',254,362)]),(511,[('CLOUD3',325,0),('CLOUD2',325,0)]),(509,[('SKY1',0,0),('SKY2',0,0)])]:
 scene=parse((args.root/f'PLACES/P{place}/MEGAFILE.HYP').read_bytes())
 assert scene['layers']==1
 pos=tuple(scene['sprites'][0]['xy'])
 result=generate(args.root,args.out,place,1,(pos,pos),background_patches=patches)
 rows.append(dict(scene=place,patches=patches,frames=result))
(args.out/'references.json').write_text(json.dumps(rows,indent=2));print(rows)

