"""Original introductory scripts, RGB movie descriptions and quit instruction."""
import argparse,json,struct,hashlib
from pathlib import Path
from astro_reader import parse
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
def sha(b):return hashlib.sha256(b).hexdigest()
exe=(args.root/'SETUP/ASTRO.EXE').read_bytes();assert sha(exe)=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
ne=struct.unpack_from('<I',exe,0x3c)[0];table=ne+struct.unpack_from('<H',exe,ne+0x22)[0];shift=struct.unpack_from('<H',exe,ne+0x32)[0]
def base(seg):return struct.unpack_from('<H',exe,table+8*(seg-1))[0]<<shift
assert exe[base(15)+0x3b2:base(15)+0x3b8]==bytes.fromhex('c706d3010100')
assert exe[base(20)+0x3c0:base(20)+0x3ce]==b'%s/PLACES/P2/\0'
rows=[]
for n in (0,1,2,3,4,432,433):
 data=(args.root/f'PLACES/P{n}/MEGAFILE.HYP').read_bytes();scene=parse(data)
 rows.append(dict(place=n,sha256=sha(data),entry=scene['scripts'],mouse_rects=scene['mouse_rects']))
movies=[]
for name in ('FLATOPEN.MOV','FLATOPN2.MOV'):
 data=(args.root/'PLACES/P2'/name).read_bytes();entries=[]
 def atoms(a,z):
  while a+8<=z:
   size,kind=struct.unpack_from('>I4s',data,a);assert size>=8 and a+size<=z
   if kind in (b'moov',b'trak',b'mdia',b'minf',b'stbl'):atoms(a+8,a+size)
   if kind==b'stsd':
    x=a+16
    for _ in range(struct.unpack_from('>I',data,a+12)[0]):
     length,codec=struct.unpack_from('>I4s',data,x)
     if codec==b'cvid':
      width,height=struct.unpack_from('>HH',data,x+32);depth,palette=struct.unpack_from('>HH',data,x+82)
      assert (width,height,depth,palette)==(400,200,24,65535)
      entries.append(dict(codec='cvid',width=width,height=height,depth=depth,palette_id=palette))
     x+=length
   a+=size
 atoms(0,len(data));assert len(entries)==1
 movies.append(dict(path='PLACES/P2/'+name,sha256=sha(data),video=entries))
args.out.write_text(json.dumps(dict(status='Original evidence, not runtime validation',quit_instruction='15:03b2 stores word1 in DS:01d3 then joins the command dispatcher',quit_code_sha256=sha(exe[base(15)+0x3b2:base(15)+0x3bb]),p4_directory='PLACES/P2',scenes=rows,movies=movies),indent=2))
print('Original intro/logo scripts, quit instruction and RGB24 descriptors: PASS')
