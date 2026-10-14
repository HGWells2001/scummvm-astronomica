"""Execute the original photon callback for all nine settings and timing edges."""
import json,struct,hashlib
import probe_p526_motion as p

symbols=json.loads((p.Path(__file__).parent/'evidence/debug/symbols.json').read_text())
names={(s['segment'],s['offset']):s['name'] for s in symbols}
size=struct.unpack_from('<H',p.exe,p.table+8*2+2)[0];relocs={}
for j in range(struct.unpack_from('<H',p.exe,p.base(3)+size)[0]):
    typ,flags,src,t1,t2=struct.unpack_from('<BBHHH',p.exe,p.base(3)+size+2+8*j);seen=set()
    while src!=65535 and src not in seen and src+2<=size:
        seen.add(src);relocs[src]=names.get((t1,t2))
        if flags&4:break
        src=struct.unpack_from('<H',p.exe,p.base(3)+src)[0]
ins={i.address:i for i in p.md.disasm(p.exe[p.base(3)+0x706:p.base(3)+0xb1e],0x706)}

def run(m,sprite):
    m.reg={'ebp':0x9000,'esp':0x8f00};m.write(0x9006,sprite);pc=0x706;compare=0
    for _ in range(500):
        if pc==0xb18:return
        i=ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[m.value(i,t) for t in o]
        if op=='mov':m.put(i,o[0],v[1])
        elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
        elif op=='add':m.put(i,o[0],v[0]+v[1])
        elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
        elif op=='push':m.push(v[0],o[0].size)
        elif op=='nop':pass
        elif op=='call':
            assert v[0]==0x33e5;m.pop();sp=m.getreg('sp');id=m.read(sp,2)
            assert id==32;target=m.read(0x1000+0x20+4*id)
            for off in (0xad,0xc9):m.write(target+off,-1)
            m.write(target+0x10,0,2);m.write(target+0x7d,0,2);m.write(target+0x7f,0,2)
        elif op=='lcall':
            sp=m.getreg('sp');target=m.read(sp);value=m.read(sp+4,2);name=relocs[i.address+1]
            assert name in ('_SWSetSpriteVisible','_SWSetCurrentFrameIndex'),name
            m.write(target+(0x10 if name=='_SWSetSpriteVisible' else 0x5b),value,2 if name=='_SWSetSpriteVisible' else 4)
        elif op in ('jmp','jne','jle'):
            if {'jmp':True,'jne':compare!=0,'jle':compare<=0}[op]:pc=v[0]
        else:raise AssertionError((hex(i.address),op))
    raise AssertionError('callback did not return')

def machine(setting,x=177,visible=1):
    m=p.Machine();m.write(0xc88,0x1000);m.write(0x1000+0x3f8,setting)
    for id in range(9,33):m.write(0x1000+0x20+4*id,0x2000+id*0x200)
    s=m.read(0x10a0);m.write(s+0x17,x,2);m.write(s+0x7d,10-setting,2);m.write(s+0x10,visible,2)
    return m,s

rows=[]
for setting in range(1,10):
    m,s=machine(setting);ticks=0;h=2166136261
    while m.read(s+0x10,2):
        proposed=m.read(s+0x17,2)+p.signed(m.read(s+0x7d,2),2);run(m,s);m.write(s+0x17,proposed,2);ticks+=1
        for b in struct.pack('<i',proposed):h=((h^b)*16777619)&0xffffffff
        assert ticks<300
    digits=[m.read(m.read(0x1000+0x20+4*id)+0x5b) for id in (9,10,11)]
    shown=[id for id in range(12,18) if m.read(m.read(0x1000+0x20+4*id)+0x10,2)]
    assert ticks==266//(10-setting)+(266%(10-setting)>0)
    rows.append(dict(setting=setting,ticks=ticks,last_x=proposed,digits=digits,shown=shown,fnv1a32=hex(h)))
    for visible in (0,1):
        for proposed in (442,443):
            edge,target=machine(setting,proposed-(10-setting),visible);run(edge,target)
            assert edge.read(target+0x10,2)==int(visible and proposed<=442)
            assert (edge.read(target+0xad)==0xffffffff)==bool(visible and proposed>442)
p.args.out.write_text(json.dumps(dict(scene=513,status='Original evidence; native checks recorded separately',
 traces=rows,boundary_cases=36,source='original callback instructions; observed SpriteWorld setters and hide_and_stop modeled',
 code_sha256=hashlib.sha256(p.exe[p.base(3)+0x6ee:p.base(3)+0xb1e]).hexdigest()),indent=2))
print('Original P513 photon motion: PASS',rows)
