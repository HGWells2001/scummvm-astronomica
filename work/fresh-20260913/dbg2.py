from pathlib import Path
import struct
b=Path(r'D:\astro\SETUP\ASTRO.EXE').read_bytes()
print(b[0x61f40:0x62040])
for base in [0x24688,0x24690]:
 for step in [14,16,18]:
  print('candidate',hex(base),step)
  for i in [300,400,500,600,700]:print(i,b[base+i*step:base+(i+1)*step].hex(' '))
