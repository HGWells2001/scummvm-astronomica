import importlib.util
for name in ['capstone','PIL','pefile']:
 print(name,importlib.util.find_spec(name))
from pathlib import Path
import struct
b=Path(r'D:\astro\SETUP\ASTRO.EXE').read_bytes()
for i in range(20):
 off,size,flags,alloc=struct.unpack_from('<4H',b,0x290+i*8);print(i+1,hex(off<<9),size,hex(flags),alloc)
