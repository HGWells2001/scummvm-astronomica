from pathlib import Path
import collections,json,sys,io
sys.path.insert(0,str(Path('outputs/astronomica-cleanroom').resolve()));from astro_reader import Reader
root=Path(r'D:\astro')
for id,off in [(406,24),(502,0x8f2cf),(503,0x96b5f),(504,0xa04d3),(533,0x86223)]:
 b=(root/f'PLACES/P{id}/MEGAFILE.HYP').read_bytes();tail=b[off:];print(id,len(b),b[:24].hex(),len(tail),'unique',len(set(tail)),'prefix',tail[:80].hex())
