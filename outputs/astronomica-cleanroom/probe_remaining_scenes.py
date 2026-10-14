"""Inventory remaining puzzle resources without treating parsed data as support."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from astro_reader import parse,FormatError
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
rows=[]
def commands(obj):
 if isinstance(obj,dict):
  if 'opcode' in obj:yield obj
  else:
   for value in obj.values():yield from commands(value)
 elif isinstance(obj,list):
  for value in obj:yield from commands(value)
for place in (502,503,504,510,516,523):
 data=(args.root/f'PLACES/P{place}/MEGAFILE.HYP').read_bytes();trailing=0
 try:scene=parse(data)
 except FormatError as e:
  match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e));assert match,e
  trailing=int(match[1]);scene=parse(data[:int(match[2],16)])
 tail=data[scene['consumed']:];images=[]
 for offset in range(4,len(tail)-54):
  if tail[offset:offset+2]!=b'BM':continue
  size=struct.unpack_from('<I',tail,offset+2)[0]
  if size<54 or size>len(tail)-offset or struct.unpack_from('<I',tail,offset-4)[0]!=size:continue
  width,height,planes,bpp=struct.unpack_from('<iiHH',tail,offset+18)
  if planes!=1 or width<=0 or height==0 or bpp not in (1,4,8,16,24,32):continue
  images.append(dict(file_offset=scene['consumed']+offset,size=size,width=width,height=height,bpp=bpp))
 rows.append(dict(scene=place,sha256=hashlib.sha256(data).hexdigest(),layers=scene['layers'],sprites=len(scene['sprites']),entry_scripts=len(scene['scripts']),custom_commands=sorted({tuple(c['args']) for c in commands(scene) if c['opcode']==23}),second_layer_sprites=[i+1 for i,s in enumerate(scene['sprites']) if s['layer']==2],movies=scene['movies'],parsed_bytes=scene['consumed'],trailing_bytes=trailing,trailing_sha256=hashlib.sha256(tail).hexdigest(),trailing_embedded_bitmaps=images))
args.out.write_text(json.dumps(dict(status='Original resource inventory only; these scenes have no verified complete native route',rows=rows,trailing_note='Contains real bitmap data. Original _load_place 9:2c87 is the final _getsome call; after the condition loop at2c97 it adds layers and initializes sprites without parsing another structure. Preserve tails; their historical purpose is not established.'),indent=2))
print('Remaining original scenes:',[(r['scene'],r['layers'],r['trailing_bytes'],len(r['trailing_embedded_bitmaps'])) for r in rows])
