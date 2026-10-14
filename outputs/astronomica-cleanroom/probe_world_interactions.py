"""Record original world-movie scripts and redraw/cursor-flag dispatch."""
import json,struct,hashlib
import probe_p526_motion as p
from astro_reader import parse
names={(s['segment'],s['offset']):s['name'] for s in json.loads((p.Path(__file__).parent/'evidence/debug/symbols.json').read_text())}
def target(seg,address):
 size=struct.unpack_from('<H',p.exe,p.table+8*(seg-1)+2)[0]
 for j in range(struct.unpack_from('<H',p.exe,p.base(seg)+size)[0]):
  typ,flags,src,a,b=struct.unpack_from('<BBHHH',p.exe,p.base(seg)+size+2+8*j);seen=set()
  while src!=65535 and src not in seen and src+2<=size:
   seen.add(src)
   if src==address:return dict(flags=flags,segment=a,offset=b,name=names.get((a,b)))
   if flags&4:break
   src=struct.unpack_from('<H',p.exe,p.base(seg)+src)[0]
 raise AssertionError((seg,address))
assert target(4,0x6895)['name']=='_UpdateGame'
assert target(13,0xecf)['name']=='_SWUpdateSpriteWorld'
assert p.exe[p.base(15)+0x2ee:p.base(15)+0x2f4]==bytes.fromhex('c706d1010000')
assert p.exe[p.base(9)+0x1035:p.base(9)+0x103a]==bytes.fromhex('833ed10100')
cursor=list(p.md.disasm(p.exe[p.base(9)+0x1035:p.base(9)+0x104b],0x1035))
assert any(i.mnemonic=='cmp' and i.op_str=='ax, word ptr [0xcc6]' for i in cursor)
assert any(i.mnemonic=='jge' and i.op_str=='0x104b' for i in cursor)
redraw_tail=list(p.md.disasm(p.exe[p.base(6)+0x792:p.base(6)+0x7c8],0x792))
assert any(i.mnemonic=='lcall' and i.op_str=='es:[bx + 0x18]' for i in redraw_tail)
rows=[]
for n in (29,82,222,231):
 data=(p.args.root/f'PLACES/P{n}/MEGAFILE.HYP').read_bytes();s=parse(data)
 rows.append(dict(place=n,sha256=hashlib.sha256(data).hexdigest(),mode=s['mode'],layers=s['layers'],movies=s['movies'],conditions=s['conditions'],entry=s['scripts'],sprite_controls=[{k:v for k,v in x.items() if k in ('xy','visible','click_enabled','click','auto_frame','auto_move')} for x in s['sprites']],mouse_rects=s['mouse_rects']))
regions={}
for seg,start,end in ((4,0x688c,0x689c),(13,0xeba,0xeda),(6,0x69d,0x7c8),(9,0x1035,0x10b3),(15,0x2e5,0x2f7),(17,0x209,0x2e3)):
 regions[f'{seg}:{start:04x}-{end:04x}']=hashlib.sha256(p.exe[p.base(seg)+start:p.base(seg)+end]).hexdigest()
p.args.out.write_text(json.dumps(dict(status='Original research; native integration tracked separately',scenes=rows,custom29_calls=[target(4,0x6895),target(13,0xecf)],command35='Clears DS:01d1; command34 sets it; PlayMovie also sets it',cursor='Mouse update 9:1035 clamps y below DS:0cc6 when DS:01d1 is set; PlayMovie sets bottom+5 at17:0265',redraw='SWUpdateSpriteWorld copies background then visible sprites and invokes final display callback through world+0x18 at6:07ba; it does not stop the movie',regions_sha256=regions),indent=2))
print('Original world-movie scripts, custom29 redraw call chain and command35 flag: PASS')
