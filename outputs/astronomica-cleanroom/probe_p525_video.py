"""Document P525 movie requirements from original files, without claiming support."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from astro_reader import parse

ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--out', type=Path, required=True)
args = ap.parse_args()
raw = (args.root/'PLACES/P525/MEGAFILE.HYP').read_bytes()
s = parse(raw)
assert s['movies'] == ['FSUN.MOV'] and len(s['mouse_rects']) == 1
commands = s['mouse_rects'][0]['click']
segments = [c['args'][1:] for c in commands if c['opcode'] == 37]
assert segments == [[150,179],[453,209],[900,452],[1800,480]]
assert all(c['args'] == [0,160,40,0] for c in commands if c['opcode'] == 3)
b = (args.root/'PLACES/P525/FSUN.MOV').read_bytes()
def atoms(start, end):
    while start+8 <= end:
        size, kind = struct.unpack_from('>I4s',b,start)
        assert size >= 8 and start+size <= end
        if kind == b'mvhd':
            yield struct.unpack_from('>II',b,start+20)
        if kind == b'moov':
            yield from atoms(start+8,start+size)
        start += size
headers = list(atoms(0,len(b)))
assert len(headers) == 1 and headers[0][0] == 30
assert all(start+length <= headers[0][1] for start,length in segments)
exe = (args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols = json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
load = next(x for x in symbols if x['name'] == '_load_place')
base = load['file_offset']-load['offset']
# The movie-bearing scene branch formats the direct intro WAV path and
# calls MMSYSTEM ordinal 2 (sndPlaySound) with zero flags, synchronously.
assert exe[base+0x1c7c:base+0x1c89] == bytes.fromhex('16 8d 86 b6 fe 50 6a 00 9a ff ff 00 00')
assert exe[0x21200+0x35e:].startswith(b'%s/PLACES/P%ld/S%ld.WAV\0')
assert s['intro_sound_id'] == 300
args.out.write_text(json.dumps(dict(scene=525,resource_sha256=hashlib.sha256(raw).hexdigest(),movie='PLACES/P525/FSUN.MOV',movie_sha256=hashlib.sha256(b).hexdigest(),timescale=headers[0][0],duration_ticks=headers[0][1],segments=segments,position=[160,40],activation_rect=s['mouse_rects'][0]['rect'],intro=dict(file='S300.WAV',handler='9:1c51-1c8f',synchronous=True),image_update='49 -> _UpdateGame 13:0eba -> _SWUpdateSpriteWorld 6:069d, full world copy overwrites retained movie pixels',runtime_evidence='runtime.log: P525 interaction verification; continuous playback checked separately'),indent=2))
print('Original P525 movie requirements: PASS',headers)
