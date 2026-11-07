"""Verify the original bit handler's NE relocations and bounded math inputs."""
from pathlib import Path
import argparse, hashlib, json, struct
from analyze_bits import exports

ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--proof', type=Path, required=True)
a = ap.parse_args()
sha = lambda b: hashlib.sha256(b).hexdigest()
x = (a.root/'SETUP/ASTRO.EXE').read_bytes()
dll = (a.root/'SETUP/BC40RTL.DLL').read_bytes()
assert sha(x) == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
assert exports(dll)[632] == '_pow'
ne = struct.unpack_from('<I', x, 60)[0]
table = ne + struct.unpack_from('<H', x, ne+0x22)[0]
shift = struct.unpack_from('<H', x, ne+0x32)[0]
base = lambda seg: struct.unpack_from('<H', x, table+(seg-1)*8)[0] << shift
data_segment = struct.unpack_from('<H', x, ne+0x0e)[0]
assert struct.unpack_from('<f', x, base(data_segment)+0x726)[0] == 2.0
mod_table = ne + struct.unpack_from('<H', x, ne+0x28)[0]
names = ne + struct.unpack_from('<H', x, ne+0x2a)[0]
modules = {}
for i in range(struct.unpack_from('<H', x, ne+0x1e)[0]):
    p = names + struct.unpack_from('<H', x, mod_table+i*2)[0]
    modules[i+1] = x[p+1:p+1+x[p]].decode('ascii')
pow_calls = {0xf66,0xfcb,0x101a,0x108d,0x10f4,0x1144,0x12d3,0x135b,0x13e8,0x1448}
ftol_calls = {0xf6e,0xfd3,0x1022,0x1095,0x10fc,0x114c,0x12db,0x1363,0x13f0,0x1450}
wanted = {pc+1 for pc in pow_calls|ftol_calls}|{0x1d40}
seg_base = base(15)
length, flags = struct.unpack_from('<HH', x, table+14*8+2)
assert flags & 0x100
reloc = seg_base+(length or 65536)
found = {}
for i in range(struct.unpack_from('<H', x, reloc)[0]):
    kind, flag, offset, target1, target2 = struct.unpack_from('<BB3H', x, reloc+2+i*8)
    seen = set()
    while offset != 0xffff:
        assert offset not in seen
        seen.add(offset)
        if offset in wanted:
            assert kind == 3 and offset not in found and x[seg_base+offset-1] == 0x9a
            if offset-1 in pow_calls:
                assert flag & 3 == 1 and modules[target1] == 'BC40RTL' and target2 == 632
                found[offset] = 'BC40RTL.ordinal632._pow'
            elif offset==0x1d40:
                assert flag & 3 == 0 and target1 == 1 and target2 == 0xb6b
                found[offset] = 'internal.1:0b6b.rand'
            else:
                assert flag & 3 == 0 and target1 == 1 and target2 == 0x15c3
                found[offset] = 'internal.1:15c3.FTOL@'
        if flag & 4:
            break
        offset = struct.unpack_from('<H', x, seg_base+offset)[0]
assert set(found) == wanted
assert not a.proof.exists()
a.proof.write_text(json.dumps(dict(
    status='ORIGINAL_RANDOM_HANDLER_MATH_RELOCATIONS_PASS',
    original_exe_sha256=sha(x), runtime_sha256=sha(dll),
    author_sha256=sha(Path(__file__).read_bytes()), data_segment=data_segment,
    original_radix_float=2.0, pow_export='_pow',
    relocations={format(k,'04x'):v for k,v in sorted(found.items())},
    limits=['Relocation identity and original constant checked; no original math helper body or Windows execution',
            'The subsequent oracle models only exact powers for admitted integer bit indices0..30']
), indent=2)+'\n')
print('Original random helpers PASS:21 relocations, BC40RTL._pow, internal FTOL@/rand, radix2.0')
