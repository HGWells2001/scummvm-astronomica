from pathlib import Path
import struct
b=Path(r'D:\astro\SETUP\ASTRO.EXE').read_bytes();pool=len(b)-8-16971
print('pool',hex(pool),b[pool:pool+120])
for off in range(0x24670,0x24750,16):print(hex(off),b[off:off+16].hex(' '))
