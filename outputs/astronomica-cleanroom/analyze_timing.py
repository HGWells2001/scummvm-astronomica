"""Extract original NE import module identities used by interpreter timing."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

def analyze(path):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e':
        raise ValueError('Unknown original executable')
    ne = struct.unpack_from('<I', data, 60)[0]
    u16 = lambda offset: struct.unpack_from('<H', data, offset)[0]
    table = ne + u16(ne + 0x28)
    names = ne + u16(ne + 0x2a)
    modules = {}
    for i in range(u16(ne + 0x1e)):
        offset = names + u16(table + 2*i)
        modules[i+1] = data[offset+1:offset+1+data[offset]].decode('ascii')
    assert modules[3] == 'MMSYSTEM'
    return {'original_sha256': digest, 'ne_import_modules': modules,
            'clock_call': {'segment': 15, 'offset': '1b48', 'module': 3,
                           'ordinal': 607, 'api': 'timeGetTime', 'unit': 'milliseconds'},
            'call_opcode': {'opcode': 41, 'segment': 15, 'offset': '118b',
                            'operation': 'zero-based table lookup, _pend_command'},
            'evidence': ['evidence/interpreter/_handle_pending.asm',
                         'evidence/interpreter/_execute_command.asm',
                         'evidence/interpreter/_copy_command.asm'],
            'abi_sources': ['https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/mmsystem.dll16/mmsystem.dll16.spec',
                            'https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timegettime'],
            'limitation': 'Called templates with a positive first delay are rejected; their timestamp lifecycle is not yet implemented.'}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('exe', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    args.out.write_text(json.dumps(analyze(args.exe), indent=2) + '\n')
