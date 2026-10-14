from pathlib import Path
import hashlib,json
r=Path(r'D:\astro')
for p in ['PLACES/GAMEDATA','SETUP/ASTRO.EXE']:b=(r/p).read_bytes();print(p,len(b),hashlib.md5(b[:5000]).hexdigest(),hashlib.sha256(b).hexdigest())
