"""Extract ASTRO.EXE's original Borland symbol records and opcode read layouts.
Requires capstone==5.0.9. All game-specific offsets are guarded by SHA-256.
General Borland format reference: https://gist.github.com/hezi/1360089cc31b6b30b5f63b93d9ec2d49
The 4.01 variant below uses wider fields; its layout was verified on this EXE.
"""
from pathlib import Path
import argparse,struct,json,hashlib

def extract(path,out):
 from capstone import Cs,CS_ARCH_X86,CS_MODE_16
 b=path.read_bytes()
 if hashlib.sha256(b).hexdigest()!='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e':raise ValueError('Unverified executable variant: refusing fixed-offset analysis')
 assert b[0x250:0x252]==b'NE' and b[0x24600:0x24604]==b'NB02'
 names=['']+[x.decode('latin1') for x in b[0x61ff5:-8].split(b'\0')];syms=[]
 for i in range(3686):
  name,typ,off,seg,flags=struct.unpack_from('<IIHHH',b,0x24690+14*i)
  if name>=len(names):raise ValueError('bad symbol name index')
  item=dict(name=names[name],type=typ,offset=off,segment=seg,flags=flags)
  if flags==24 and 1<=seg<=20:item['file_offset']=(struct.unpack_from('<H',b,0x290+8*(seg-1))[0]<<9)+off
  syms.append(item)
 out.mkdir(exist_ok=True,parents=True);(out/'symbols.json').write_text(json.dumps(syms,indent=2))
 md=Cs(CS_ARCH_X86,CS_MODE_16)
 for name in ['_load_place','_read_command_mem','_execute_command','_do_custom','_load_game']:
  s=next(s for s in syms if s['name']==name);off=s['offset'];seg=s['segment'];base=s['file_offset']-off
  end=min([x['offset'] for x in syms if x['segment']==seg and x['offset']>off and x['flags']==s['flags']] or [struct.unpack_from('<H',b,0x292+8*(seg-1))[0]])
  lines=[f'{i.address:04x}: {i.mnemonic:8} {i.op_str}' for i in md.disasm(b[base+off:base+end],off)]
  (out/(name+'.asm')).write_text('\n'.join(lines))
 base=0x14600;instructions={i.address:i for i in md.disasm(b[base+0x2ff2:base+0x3528],0x2ff2)};rows=[]
 for i in range(49):
  op=struct.unpack_from('<I',b,base+0x3528+4*i)[0];addr=struct.unpack_from('<H',b,base+0x35ec+2*i)[0];entry=addr;reads=[];size=4;seen=set()
  # Trace argument-read paths up to the common delay/next-opcode epilogue.
  # Conditional jumps here concern allocation/index fixups, not read counts.
  while addr!=0x33f4:
   if addr in seen:raise ValueError('unexpected cycle')
   seen.add(addr);inst=instructions[addr]
   if inst.mnemonic=='push' and inst.op_str=='0xff':size=255
   if inst.mnemonic=='call' and inst.op_str=='0x2fcd':reads.append(size);size=4
   addr=int(inst.op_str,16) if inst.mnemonic=='jmp' else addr+inst.size
  rows.append(dict(opcode=op,entry=entry,reads=reads))
 (out/'opcode-layout.json').write_text(json.dumps(rows,indent=2))
 print(f'{len(syms)} symbol records, {len(rows)} opcode layouts')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('exe',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();extract(a.exe,a.out)
