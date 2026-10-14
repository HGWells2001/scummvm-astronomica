"""Check P508 scene-entry audio against original executable and resources."""
import argparse, hashlib, json, sys, wave
from pathlib import Path
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
b=(args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols=json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
s=next(s for s in symbols if s['name']=='_load_place');base=s['file_offset']-s['offset']
assert b[base+0x156b:base+0x1574]==bytes.fromhex('66c706bb0100000000')
assert b[base+0x1c45:base+0x1c4e]==bytes.fromhex('ff36cd01900ee8b91e')
scene=parse((args.root/'PLACES/P508/MEGAFILE.HYP').read_bytes())
assert scene['mode']==0 and scene['intro_sound']==1 and scene['intro_sound_id']==302 and scene['movie_count']==0
folder=args.root/'PLACES/P508'
assert (folder/'S1.WAV').read_bytes()==(folder/'S302.WAV').read_bytes()
files={}
for name in ('S0.WAV','S1.WAV','S302.WAV'):
 with wave.open(str(folder/name)) as w:
  files[name]=dict(sha256=hashlib.sha256((folder/name).read_bytes()).hexdigest(),frames=w.getnframes(),rate=w.getframerate(),channels=w.getnchannels(),seconds=w.getnframes()/w.getframerate())
args.out.write_text(json.dumps(dict(files=files,scene_intro=302,default_loop=0,evidence=dict(loop='9:156b writes 0 to DS:01bb for mode 0',intro='9:1c45 pushes direct intro ID; 9:1c4b calls _playSound',wait='9:2f22-2fa5 waits for intro playback when movie count is zero',help_exception='9:1c26 skips intro when previous scene is 408'),scope='Mode-0 interactive entry; other scene modes and save-restore counter behavior remain outside this implementation'),indent=2))
print('P508 entry audio original evidence: PASS')
