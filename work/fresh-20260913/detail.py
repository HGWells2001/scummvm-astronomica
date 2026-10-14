from pathlib import Path
import struct,json
b=Path(r'D:\astro\SETUP\ASTRO.EXE').read_bytes(); n=struct.unpack_from('<I',b,60)[0]
print('NE',b[n:n+64].hex(' '));print('TAIL',b[-128:].hex(' '))
s=json.loads(Path('outputs/astronomica-cleanroom/exe-strings.json').read_text())
print('\n'.join(f"{x['offset']:x} {x['text']}" for x in s if x['offset']>403000))
for id in [0,2,3,29]:
 p=Path(fr'D:\astro\PLACES\P{id}\MEGAFILE.HYP');b=p.read_bytes()
 if id==0:
  for off in range(0x950,len(b),16): print(f'{off:04x}',b[off:off+16].hex(' '))
