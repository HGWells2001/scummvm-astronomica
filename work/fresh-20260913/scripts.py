from pathlib import Path
import struct,collections,re
root=Path(r'D:\astro')
for i in [0,1,2,3,29,98,103,512]:
 p=root/f'PLACES/P{i}/PLACEDEF'
 if p.exists(): print('\nSCRIPT',i,'\n',p.read_text(errors='replace')[:7000])
b=(root/'SETUP/ASTRO.EXE').read_bytes();start=len(b)-struct.unpack_from('<I',b,len(b)-4)[0];print('DEBUG START',hex(start),b[start:start+128].hex(' '))
print('hyp first words distribution',collections.Counter(tuple(struct.unpack_from('<4I',p.read_bytes())) for p in (root/'PLACES').glob('*/MEGAFILE.HYP')).most_common(15))
