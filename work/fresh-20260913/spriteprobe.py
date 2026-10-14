exec(open('work/fresh-20260913/symbols.py').read().split("for name in ['_load_place'")[0])
for name in ['_CreateGameSpriteFromMem','_CreateSpriteFromMegaFile','_CreateFrameFromMegaFile']:
 s=next(s for s in syms if s['name']==name);seg=s['segment'];off=s['offset'];base=struct.unpack_from('<H',b,0x290+8*(seg-1))[0]<<9;end=min([x['offset'] for x in syms if x['segment']==seg and x['offset']>off and x['flags']==s['flags']] or [struct.unpack_from('<H',b,0x292+8*(seg-1))[0]])
 lines=[f'{i.address:04x}: {i.mnemonic:8} {i.op_str}' for i in md.disasm(b[base+off:base+end],off)]
 Path('work/fresh-20260913/'+name+'.asm').write_text('\n'.join(lines));print(name,hex(base+off),end-off);print('\n'.join(lines[:95]))

