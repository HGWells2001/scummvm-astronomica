"""Recover opcode 33 evidence exclusively from original NE executables."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

def exports(data):
    ne = struct.unpack_from('<I',data,60)[0]
    assert data[ne:ne+2] == b'NE'
    result = {}
    for p in (ne+struct.unpack_from('<H',data,ne+0x26)[0],
              struct.unpack_from('<I',data,ne+0x2c)[0]):
        while data[p]:
            size = data[p]
            name = data[p+1:p+1+size].decode('ascii')
            ordinal = struct.unpack_from('<H',data,p+1+size)[0]
            result[ordinal] = name
            p += size+3
    return result

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    exe=(args.root/'SETUP/ASTRO.EXE').read_bytes()
    dll=(args.root/'SETUP/BC40RTL.DLL').read_bytes()
    assert hashlib.sha256(exe).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
    symbol=exports(dll).get(632)
    result={'runtime_sha256':hashlib.sha256(dll).hexdigest(),
            'runtime_ordinal_632':symbol,
            'executable_ds_0726_float':struct.unpack_from('<f',exe,0x21200+0x726)[0],
            'handler':'15:0f08','global_set':'15:0f87 OR',
            'global_clear':'15:0fec TEST then 15:1040 SUB',
            'local_set':'15:10ae OR','local_clear':'15:1115 TEST then 15:116b SUB'}
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result)
