"""Verify original NE command-reader dispatch and sound-id decrement."""
import argparse,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('exe',type=Path);ap.add_argument('--symbols',type=Path,default=Path(__file__).parent/'evidence/debug/symbols.json');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
b=args.exe.read_bytes();assert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
s=next(s for s in json.loads(args.symbols.read_text()) if s['name']=='_read_command_mem');base=s['file_offset']-s['offset'];table={}
for i in range(49):
 op=struct.unpack_from('<i',b,base+0x3528+4*i)[0]
 target=struct.unpack_from('<H',b,base+0x3528+4*i+2*(49-i)+0x62)[0];table[op]=target
assert table[9]==0x306d and table[27]==0x30b0
# Opcode 9 is a short jump to the common reader for opcode 27.
assert b[base+0x306d]==0xeb and 0x306f+struct.unpack_from('<b',b,base+0x306e)[0]==0x30b0
assert b[base+0x30d3:base+0x30d5]==bytes.fromhex('6648') # DEC EAX
report=dict(reader='9:2ff2',dispatch={str(k):f'9:{table[k]:04x}' for k in (9,10,27)},decrement='9:30d3 DEC EAX',conversion='serialized argument minus one; only command-derived ids',p508=dict(correct_answer=dict(command=9,file='PLACES/P508/S8.WAV'),wrong_answer=dict(command=8,file='PLACES/P508/S7.WAV'),loop=dict(command=7,file='PLACES/P508/S6.WAV')),internal_success='Direct _playSound(912) is not decremented; SOUNDS/S12.WAV')
args.out.write_text(json.dumps(report,indent=2));print('Original sound-id decrement: PASS')
