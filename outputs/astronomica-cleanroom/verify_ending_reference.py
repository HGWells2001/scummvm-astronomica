"""Extract the P511 ending's original command sequence for reproducible review."""
import argparse, json
from pathlib import Path
from astro_reader import parse
ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
s=parse((args.root/'PLACES/P511/MEGAFILE.HYP').read_bytes())['scripts'][0]
commands=[(c['opcode'],c['args'],c['delay']) for c in s]
assert commands == [(31,[1,5,7,0,0,0],0),(32,[1,5,8],0),(28,[-1],0),(16,[6],-1),(16,[7],-1),(7,[5,0,170],-1),(27,[12],0),(7,[20,190,220],0),(7,[20,220,215],300),(7,[20,250,210],300),(7,[20,280,205],300),(7,[20,310,205],300),(7,[20,340,210],300),(7,[20,370,210],300),(7,[20,400,215],300),(23,[25,0,0,0,0,0],5000),(5,[388],1000),(45,[],-1),(31,[1,4,1,0,0,0],0),(29,[-1],75),(42,[],-1)]
args.out.write_text(json.dumps(dict(scene=511,script=0,commands=s,solved_input={'local_5':7},destination=388),indent=2))
print('Verified original P511 ending: 21 commands, eight positions, destination P388')
