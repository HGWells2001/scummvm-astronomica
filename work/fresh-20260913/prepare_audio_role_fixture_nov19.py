"""Rebuild controlled native audio-role fixtures from the published catalogue and original WAVs."""
from pathlib import Path
import argparse,hashlib,json,re,struct
parser=argparse.ArgumentParser();parser.add_argument('--game',type=Path,default=Path('D:/astro'));args=parser.parse_args();w=Path(__file__).resolve().parent;catalogue=json.loads((w/'audio-role-catalogue-nov19.json').read_text());root=args.game.resolve();rows=[]
for clip in catalogue['clips']:
 for relative in clip['paths']:
  path=(root/relative).resolve();assert path.is_relative_to(root)and hashlib.sha256(path.read_bytes()).hexdigest()==clip['sha256'],relative
  m=re.fullmatch(r'PLACES/P(\d+)/S(\d+)\.WAV',relative)
  place,sound=(int(m[1]),int(m[2]))if m else(27,900+int(Path(relative).stem[1:]))
  rows.append((place,sound,int(clip['role']=='effect')))
assert len(rows)==catalogue['files']==632
blob=struct.pack('<I',len(rows))+b''.join(struct.pack('<iii',*row)for row in rows);out=w/'audio-role-fixture-nov19.bin';out.write_bytes(blob);print('632 audio-role fixture rows prepared; original files unchanged')
