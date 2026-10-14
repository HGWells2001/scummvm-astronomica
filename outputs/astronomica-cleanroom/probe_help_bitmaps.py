"""Decode original help bitmap streams; research only, no native rendering yet."""
import argparse,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
d=(a.root/'HELP/ASTRONOM.HLP').read_bytes();directory=json.loads((a.out.parent/'help-directory.json').read_text());assert hashlib.sha256(d).hexdigest()==directory['source_sha256']
def lz(data):
 out=bytearray();pos=0
 while pos<len(data):
  flags=data[pos];pos+=1
  for bit in range(8):
   if pos>=len(data):break
   if flags&(1<<bit):
    assert pos+2<=len(data);word=struct.unpack_from('<H',data,pos)[0];pos+=2;distance=(word&4095)+1
    assert distance<=len(out)
    for _ in range((word>>12)+3):out.append(out[-distance])
   else:out.append(data[pos]);pos+=1
   assert len(out)<=65536
 return bytes(out)
class Reader:
 def __init__(self,data):self.data=data;self.pos=10
 def packed(self,small=False):
  count=1 if small else 2
  assert self.pos+count<=len(self.data)
  value=int.from_bytes(self.data[self.pos:self.pos+count],'little')
  if value&1:
   count*=2;assert self.pos+count<=len(self.data)
   value=int.from_bytes(self.data[self.pos:self.pos+count],'little')
  self.pos+=count;return value>>1
rows=[]
for index in range(31):
 info=directory['streams'][f'|bm{index}'];b=d[info['offset']+9:info['offset']+9+info['used']]
 assert b[:8]==bytes.fromhex('6c50010008000000') and b[8]==6 and b[9] in (0,2)
 r=Reader(b);dpi_x=r.packed();dpi_y=r.packed();planes=r.packed(True);bits=r.packed(True)
 width=r.packed();height=r.packed();colors=r.packed();important=r.packed();size=r.packed();hotspots=r.packed()
 offset,hotspot_offset=struct.unpack_from('<II',b,r.pos);r.pos+=8
 assert planes==1 and bits==8 and 0<width<=640 and 0<height<=480 and colors==256 and important==256
 assert hotspots==hotspot_offset==0 and 8+offset==r.pos+4*colors and 8+offset+size==len(b)
 palette=b[r.pos:r.pos+4*colors];stored=b[8+offset:]
 pixels=lz(stored) if b[9]==2 else stored
 pitch=((width*bits+31)//32)*4;assert len(pixels)==pitch*height
 rows.append(dict(index=index,width=width,height=height,pitch=pitch,bit_depth=bits,dpi=[dpi_x,dpi_y],compression=b[9],
  compressed_bytes=size,decoded_bytes=len(pixels),palette_sha256=hashlib.sha256(palette).hexdigest(),pixels_sha256=hashlib.sha256(pixels).hexdigest(),
  orientation='Bottom-up DIB; preview of bitmap0 inspected',palette_format='256 BGRA entries'))
a.out.write_text(json.dumps(dict(status='Original bitmap decode research; native help images not yet rendered',source_sha256=hashlib.sha256(d).hexdigest(),
 image_count=len(rows),lz_images=sum(r['compression']==2 for r in rows),raw_images=sum(r['compression']==0 for r in rows),images=rows,
 findings=['Packed32 fields use16 bits unless low bit is1, then32; packed16 uses8 or16. Values shift right1.',
 'Image type6, planes1,8 bits per pixel,256 palette entries. Image group has one image at offset8.',
 'Compression2 uses the same bounded LZ token scheme as help topics. Bitmap12 uses compression0 (raw).',
 'All stream extents, palette boundaries and decoded pitch*height sizes match. No hotspot payloads.']),indent=2))
print('Original help bitmaps:31 decoded,30 LZ +1 raw, palette/extents/row-size checks PASS')
