"""Check the original local synchronous audio exceptions."""
import argparse,hashlib,json,wave
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
b=(args.root/'SETUP/ASTRO.EXE').read_bytes();assert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols=json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text());s=next(s for s in symbols if s['name']=='_playSound');base=s['file_offset']-s['offset']
expected=bytes.fromhex('66813e8c0cf9010000750a83fe027c0583fe0a7e1766813e8c0c00020000750583fe0e7407833e900700740a168d86fefe506a02eb08168d86fefe506a039affff0000')
assert b[base+0x3bb5:base+0x3bf8]==expected
files=[]
for place,ids in ((505,range(2,11)),(512,[14])):
 for sound in ids:
  p=args.root/f'PLACES/P{place}/S{sound}.WAV'
  with wave.open(str(p)) as w:
   files.append(dict(place=place,file_id=sound,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),frames=w.getnframes(),rate=w.getframerate(),seconds=w.getnframes()/w.getframerate()))
args.out.write_text(json.dumps(dict(address='9:3bb5-3bf8',bytes=expected.hex(),behavior='P505 local 2..10 and P512 local 14 use sndPlaySound flags 2; ordinary local sounds use flags 3. File IDs have already been decremented by command reader.',files=files),indent=2))
print('Original blocking audio exceptions: PASS')
