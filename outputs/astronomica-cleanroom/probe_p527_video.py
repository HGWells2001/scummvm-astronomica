"""Read the four original P527 selections and QuickTime time scale."""
import argparse, hashlib, json, struct
from pathlib import Path
from astro_reader import parse
ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
s = parse((args.root/'PLACES/P527/MEGAFILE.HYP').read_bytes())
assert s['movies'] == ['FLATRING.MOV']
segments = [c['args'][1:] for c in s['scripts'][0] if c['opcode'] == 37]
assert segments == [[1800,599],[2568,959],[900,899],[0,899]]
assert all(c['args'] == [0,10,10,0] for c in s['scripts'][0] if c['opcode'] == 3)
b = (args.root/'PLACES/P527/FLATRING.MOV').read_bytes()
def atoms(start,end):
    while start+8 <= end:
        size,kind = struct.unpack_from('>I4s',b,start)
        assert size >= 8 and start+size <= end
        if kind == b'mvhd': yield struct.unpack_from('>II',b,start+20)
        if kind == b'moov': yield from atoms(start+8,start+size)
        start += size
headers = list(atoms(0,len(b)))
assert len(headers) == 1 and headers[0][0] == 30
assert all(a+n <= headers[0][1] for a,n in segments)
args.out.write_text(json.dumps(dict(movie='PLACES/P527/FLATRING.MOV',sha256=hashlib.sha256(b).hexdigest(),
    timescale=headers[0][0],duration_ticks=headers[0][1],segments=segments,position=[10,10],
    success_global=43,destination=174),indent=2))
print('Original P527 movie metadata: PASS',headers)
