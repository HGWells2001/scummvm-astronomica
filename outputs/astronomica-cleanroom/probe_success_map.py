from pathlib import Path
import json,re,struct,argparse,hashlib
ap=argparse.ArgumentParser(); ap.add_argument("exe",type=Path); ap.add_argument("--evidence",type=Path,default=Path(__file__).parent/"evidence"); ap.add_argument("--out",type=Path,required=True); args=ap.parse_args()
b=args.exe.read_bytes();syms=json.loads((args.evidence/'debug/symbols.json').read_text());sym=next(s for s in syms if s['name']=='_do_custom');base=sym['file_offset']-sym['offset']
asm=(args.evidence/'interpreter/_do_custom.asm').read_text();rows=[]
assert hashlib.sha256(b).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
for i in range(34):
 scene=struct.unpack_from('<i',b,base+0x6c94+4*i)[0];target=struct.unpack_from('<H',b,base+0x6c94+4*i+2*(34-i)+0x44)[0]
 if scene in (352,359,513,529,530):continue
 section=asm[asm.index(f'{target:04x}:'):];section=section[:section.index('jmp      0x5a8e')]
 offsets=re.findall(r'es:\[bx \+ (0x[0-9a-f]+)\]',section)
 assert len(offsets)==2 and offsets[0]==offsets[1] and '_puzzle_successful' in section
 flag=(int(offsets[0],16)-10)//4;assert int(offsets[0],16)==10+4*flag
 rows.append(dict(scene=scene,handler=f'4:{target:04x}',global_id=flag))
args.out.write_text(json.dumps(rows,indent=2))
print(rows)


