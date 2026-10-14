"""Fresh Astronomica binary reader. Derived from original ASTRO.EXE, 2026-09-13.
Does not execute scripts. Unknown structures fail with an exact byte offset.
"""
from pathlib import Path
import struct,json,argparse,hashlib,collections

class FormatError(ValueError):pass
class Reader:
 def __init__(self,data):self.data=data;self.pos=0
 def take(self,n):
  if n<0 or n>len(self.data)-self.pos:raise FormatError(f'truncated at 0x{self.pos:x}: need {n}')
  b=self.data[self.pos:self.pos+n];self.pos+=n;return b
 def i32(self):return struct.unpack('<i',self.take(4))[0]
 def ints(self,n):return [self.i32() for _ in range(n)]
 def count(self):
  n=self.i32()
  if not 0<=n<=10000:raise FormatError(f'invalid count {n} at 0x{self.pos-4:x}')
  return n
 def flag(self):
  n=self.i32()
  if n not in (0,1):raise FormatError(f'invalid flag {n} at 0x{self.pos-4:x}')
  return n
 def text(self):return self.take(255).split(b'\0')[0].decode('cp1252',errors='replace')
 def bitmap(self):
  size=self.count_size();off=self.pos;blob=self.take(size)
  if len(blob)<54 or blob[:2]!=b'BM':raise FormatError(f'invalid BMP at 0x{off:x}')
  file_size,pixel_offset=struct.unpack_from('<I',blob,2)[0],struct.unpack_from('<I',blob,10)[0]
  width,height,planes,bpp,compression=struct.unpack_from('<iiHHI',blob,18)
  if file_size!=size or not 54<=pixel_offset<=size or planes!=1 or width<=0 or not height:raise FormatError(f'invalid BMP header at 0x{off:x}')
  return dict(offset=off,size=size,width=width,height=height,bpp=bpp,compression=compression,sha256=hashlib.sha256(blob).hexdigest())
 def count_size(self):
  n=self.i32()
  if n<0 or n>len(self.data)-self.pos:raise FormatError(f'invalid size {n} at 0x{self.pos-4:x}')
  return n
 def image(self):
  if not self.flag():return None
  if self.flag():return self.bitmap()
  return dict(external=self.text())

NAMES={3:'play_quicktime',5:'new_place',6:'quit_game',20:'load_background',23:'custom',31:'condition',32:'set_condition',42:'end_condition',45:'else'}
LAYOUT={int(x['opcode']):x['reads'] for x in json.loads(Path(__file__).with_name('opcode-layout.json').read_text())}
def commands(r):
 result=[]
 for _ in range(100000):
  offset=r.pos;op=r.i32()
  if op==0:return result
  if op not in LAYOUT:raise FormatError(f'unknown opcode {op} at 0x{offset:x}')
  args=[r.text() if n==255 else r.i32() for n in LAYOUT[op]]
  result.append(dict(offset=offset,opcode=op,name=NAMES.get(op,f'op_{op}'),args=args,delay=r.i32()))
 raise FormatError('command limit exceeded')
def optional_commands(r):return commands(r) if r.flag() else []
def sprite(r):
 d=dict(offset=r.pos,clone=r.i32())
 if d['clone']==-1:d['frames']=[[r.bitmap(),r.bitmap()] for _ in range(r.count())]
 d.update(layer=r.i32(),visible=r.flag(),xy=r.ints(2))
 d['click_enabled']=r.flag()
 if d['click_enabled']:d.update(click_type=r.i32(),click=commands(r))
 d['drag_enabled']=r.flag()
 if d['drag_enabled']:d['drag']=commands(r)
 d['rect']=r.ints(4)
 d['mouse_in']=optional_commands(r);d['mouse_out']=optional_commands(r)
 d['auto_frame']=r.flag()
 if d['auto_frame']:d['frame_data']=r.ints(3)
 d['auto_move']=r.flag()
 if d['auto_move']:d['move_data']=r.ints(5)
 d['has_cursor']=r.flag()
 if d['has_cursor']:d['cursor']=r.i32()
 return d

def parse(data):
 r=Reader(data);d={};d['mode']=r.i32()
 if d['mode'] not in (0,1,3):raise FormatError('unknown place mode')
 d['navigation']=r.ints(3) if d['mode']==1 else None
 d['background']=r.image();d['control']=r.image()
 d['intro_sound']=r.flag()
 if d['intro_sound']:d['intro_sound_id']=r.i32()
 d.update(layers=r.count(),sprite_count=r.count(),sound_count=r.count(),movie_count=r.count(),cursor_count=r.count(),legacy_name=r.text())
 d['sprites']=[sprite(r) for _ in range(d['sprite_count'])]
 d['sounds']=[r.ints(2) for _ in range(d['sound_count'])]
 d['movies']=[r.text() for _ in range(d['movie_count'])]
 d['scripts']=[commands(r) for _ in range(r.count())]
 d['mouse_rects']=[dict(rect=r.ints(4),click=optional_commands(r),mouse_in=optional_commands(r),mouse_out=optional_commands(r)) for _ in range(r.count())]
 d['conditions']=[r.ints(6) for _ in range(r.count())]
 d['consumed']=r.pos;d['size']=len(data)
 if r.pos!=len(data):raise FormatError(f'trailing {len(data)-r.pos} bytes at 0x{r.pos:x}')
 return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 result=[]
 for p in sorted((args.root/'PLACES').glob('P*/MEGAFILE.HYP'),key=lambda p:int(p.parent.name[1:])):
  row=dict(place=p.parent.name)
  try:
   data=p.read_bytes();d=parse(data);row.update(ok=True,size=len(data),sprites=d['sprite_count'],scripts=len(d['scripts']))
   (args.out/(p.parent.name+'.json')).write_text(json.dumps(d,indent=2))
  except (FormatError,struct.error) as e:row.update(ok=False,error=str(e))
  result.append(row)
 (args.out/'validation.json').write_text(json.dumps(result,indent=2));print('Parsed',sum(x['ok'] for x in result),'/',len(result));print([x for x in result if not x['ok']][:25])
if __name__=='__main__':main()
