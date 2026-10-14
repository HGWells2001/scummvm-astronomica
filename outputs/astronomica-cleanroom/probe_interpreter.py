from pathlib import Path
import json,struct,sys
import argparse
ap=argparse.ArgumentParser(); ap.add_argument('exe',type=Path); ap.add_argument('--symbols',type=Path,default=Path(__file__).parent/'evidence/debug/symbols.json'); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
b=args.exe.read_bytes();syms=json.loads(args.symbols.read_text());md=Cs(CS_ARCH_X86,CS_MODE_16)
lookup={(x['segment'],x['offset']):x['name'] for x in syms if x['flags']==24}
lookup.update({(x['segment'],x['offset']):x['name'] for x in syms if x['name'] in ('_calloc','_malloc','_free')})
import hashlib
assert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e', 'Unknown executable'
out=args.out;out.mkdir(parents=True,exist_ok=True)
for name in ['_execute_command','_do_command','_pend_command','_handle_pending','_copy_command','_read_command_mem','_do_mouse','_fxm_PtInRect','_CreateGame','_do_place','_place_loop','WINMAIN','_clear_globals','_create_place','_load_place','_load_game','_BlitPixieSpriteDrawProc','_BlitPixieMaskDrawProc','_SWSetSpriteLocation','_SWAddSprite','_CreateFrameFromMegaFile','_SWStdDrawProc','_SWMoveSprite','_SWOffsetSprite','_CloneGameSprite','_SWCloneSprite','_SWSetCurrentFrameIndex','_SWCreateSprite','_SWIsPointInSprite','_SWProcessSpriteWorld','_SWAddFrame','_SWSetSpriteFrameTime','_CreateGameSpriteFromMem','_CreateSpriteFromBmpMem','_SWSetCurrentFrame','_playSound','_stop_sounds','_InitSounds','_in_custom','_RangedRdm','_SWSetSpriteFrameRange','_do_custom','_playLoop','_puzzle_successful','_UpdateGame','_SWUpdateSpriteWorld','_SWCreateSpriteWorld']:
 s=next(x for x in syms if x['name']==name);seg=s['segment'];off=s['offset'];base=s['file_offset']-off;size=struct.unpack_from('<H',b,0x292+8*(seg-1))[0];end=min([x['offset'] for x in syms if x['segment']==seg and x['offset']>off and x['flags']==24] or [size]);relocs={}
 n=struct.unpack_from('<H',b,base+size)[0]
 for j in range(n):
  typ,flags,src,t1,t2=struct.unpack_from('<BBHHH',b,base+size+2+8*j);target=lookup.get((t1,t2),f'{t1}:{t2:04x}') if flags&3==0 else f'import({flags&3},{t1},{t2})'
  seen=set()
  while src!=65535 and src not in seen and src+2<=size:
   seen.add(src);relocs[src]=target
   if flags&4:break
   src=struct.unpack_from('<H',b,base+src)[0]
 lines=[]
 for ins in md.disasm(b[base+off:base+end],off):
  note=relocs.get(ins.address+1,'') if ins.mnemonic=='lcall' else lookup.get((seg,int(ins.op_str,16)),'') if ins.mnemonic=='call' and ins.op_str.startswith('0x') else ''
  lines.append(f'{ins.address:04x}: {ins.mnemonic:8} {ins.op_str}'+(' ; '+note if note else ''))
 (out/(name+'.asm')).write_text('\n'.join(lines))
 print(name,f'{seg}:{off:04x}',end-off)
 if name=='_execute_command':
  rows=[]
  for i in range(48):
   op=struct.unpack_from('<I',b,base+0x187a+4*i)[0];entry=struct.unpack_from('<H',b,base+0x193a+2*i)[0];rows.append(dict(opcode=op,entry=entry))
  (out/'dispatch.json').write_text(json.dumps(rows,indent=2));print(rows)













