"""Reproduce P520 movie selection from the original script, EXE and MOV."""
import argparse,hashlib,json,struct
from pathlib import Path
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
exe=(args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
assert exe[0x21200+0x3de:].split(b'\0',1)[0]==b'%s/PLACES/P408/'
scene=parse((args.root/'PLACES/P520/MEGAFILE.HYP').read_bytes())
assert scene['movies']==['mentors.mov']
commands=[(c['opcode'],c['args'],c['delay']) for c in scene['scripts'][0]]
assert commands==[(37,[0,55407,1274],0),(3,[0,240,130,0],0),(5,[537],44000)]
assert scene['mouse_rects'][0]['click'][0]['args']==[537]
movie=(args.root/'PLACES/P408/MENTORS.MOV').read_bytes()
def atoms(start,end):
 while start+8<=end:
  size,kind=struct.unpack_from('>I4s',movie,start)
  assert size>=8 and start+size<=end
  if kind==b'mvhd':
   assert movie[start+8]==0
   yield struct.unpack_from('>II',movie,start+20)
  if kind==b'moov':yield from atoms(start+8,start+size)
  start+=size
headers=list(atoms(0,len(movie)));assert headers==[(30,67222)]
args.out.write_text(json.dumps(dict(movie='PLACES/P408/MENTORS.MOV',sha256=hashlib.sha256(movie).hexdigest(),timescale=30,duration_ticks=67222,start_tick=55407,length_ticks=1274,start_seconds=55407/30,length_seconds=1274/30,position=[240,130],destination=537,transition_ms=44000,commands=scene['scripts'][0],evidence=['9:2651-266f redirects P520 to P408','15:023d-02c6 invokes _SetMovieActiveSegment','17:05d3-0600 sets selection start and duration','17:0209 _PlayMovie positions and starts playback']),indent=2))
print('Original P520 video metadata: PASS')
