"""Execute original _draw_score instructions with modeled GDI calls; original files stay read-only."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,random,re,struct,sys
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--screenshots',nargs=2,type=Path);a=ap.parse_args();w=a.workspace.resolve();out=a.out.resolve();out.mkdir(exist_ok=True,parents=True);assert not any(out.iterdir()),'Preserve existing research output'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Reuse only the accepted generic x86 memory/register machinery, not an engine implementation.
sys.argv=[str(__file__),str(a.root),'--out',str(out/'unused.json'),'--deps',str(w/'deps-verified')]
import probe_p526_motion as cpu
b=cpu.exe;assert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
# Re-extract original Borland symbols instead of trusting a previous interpretation.
strings=['']+[x.decode('latin1')for x in b[0x61ff5:-8].split(b'\0')];syms=[]
for i in range(3686):
    name,typ,offset,segment,flags=struct.unpack_from('<IIHHH',b,0x24690+14*i);syms.append(dict(name=strings[name],segment=segment,offset=offset))
score=next(s for s in syms if s['name']=='_draw_score');assert(score['segment'],score['offset'])==(3,0x39ca)
def relocations(segment):
    size,flags=struct.unpack_from('<HH',b,cpu.table+8*(segment-1)+2)
    if not flags&0x100:return []
    start=cpu.base(segment);records=[]
    for j in range(struct.unpack_from('<H',b,start+size)[0]):
        typ,flags,src,target,offset=struct.unpack_from('<BBHHH',b,start+size+2+8*j);seen=set()
        while src!=65535 and src not in seen and src+2<=size:
            seen.add(src);records.append((src,typ,flags,target,offset))
            if flags&4:break
            src=struct.unpack_from('<H',b,start+src)[0]
    return records
modules=cpu.ne+struct.unpack_from('<H',b,cpu.ne+0x28)[0];imports=cpu.ne+struct.unpack_from('<H',b,cpu.ne+0x2a)[0]
def module(i):
    pos=imports+struct.unpack_from('<H',b,modules+2*(i-1))[0];return b[pos+1:pos+1+b[pos]].decode('ascii')
calls={}
for src,typ,flags,target,offset in relocations(3):
    if not 0x39ca<=src<0x3ae0:continue
    assert typ==3
    calls[src-1]=(module(target),offset)if flags&3 else('internal',target,offset)
assert set(calls.values())=={('GDI',66),('GDI',45),('GDI',69),('USER',72),('USER',81),('internal',6,0x5f1)}
for name,ordinal in [('CREATESOLIDBRUSH',66),('SELECTOBJECT',45),('DELETEOBJECT',69),('SETRECT',72),('FILLRECT',81)]:assert any(s['name']==name and s['segment']==0xc000+ordinal for s in syms)
callers=[]
for segment in range(1,20):
    for src,typ,flags,target,offset in relocations(segment):
        if not flags&3 and target==3 and offset==0x39ca:callers.append((segment,src-1))
assert callers==[(9,0x1911)]
gate=b[cpu.base(9)+0x1903:cpu.base(9)+0x1916];assert gate[:7]==bytes.fromhex('833e9a0c00740c')and gate[7:14]==bytes.fromhex('833ea501007405')
assert next(s['offset']for s in syms if s['name']=='_monitor_status')==0x1a5 and next(s['offset']for s in syms if s['name']=='_nav_place')==0xc9a
assert struct.unpack_from('<H',b,cpu.base(20)+0x1a5)[0]==1
instructions={i.address:i for i in cpu.md.disasm(b[cpu.base(3)+0x39d8:cpu.base(3)+0x3ad8],0x39d8)}
def run(values,counter=0):
    m=cpu.Machine();m.reg={'ebp':0x9000,'esp':0x8d00,'ss':0x1000};m.write(0x7a8,0x6000);m.write(0x6000,0x6200);m.write(0x620c,0x6300);m.write(0x6300,0xbeef,2);m.write(0x153,counter)
    for index,value in enumerate(values):m.write(0x600a+4*index,value)
    pc=0x39d8;compare=0;rectangles=[];color=None
    for _ in range(10000):
        if pc==0x3ad8:assert color==0xffffff;return rectangles
        i=instructions[pc];pc+=i.size;ops=i.operands;v=[m.value(i,o)for o in ops];op=i.mnemonic
        if op=='mov':m.put(i,ops[0],v[1])
        elif op=='les':m.setreg(i.reg_name(ops[0].reg),v[1]&65535)
        elif op=='lea':m.put(i,ops[0],m.address(i,ops[1]))
        elif op=='push':m.push(v[0],ops[0].size)
        elif op=='add':m.put(i,ops[0],v[0]+v[1])
        elif op=='inc':m.put(i,ops[0],v[0]+1)
        elif op=='shl':m.put(i,ops[0],v[0]<<v[1])
        elif op=='imul':m.put(i,ops[0],cpu.signed(v[-2],ops[-2].size)*cpu.signed(v[-1],ops[-1].size))
        elif op=='cmp':compare=cpu.signed(v[0],ops[0].size)-cpu.signed(v[1],ops[1].size)
        elif op in('jmp','jne','jle'):
            if {'jmp':True,'jne':compare!=0,'jle':compare<=0}[op]:pc=v[0]
        elif op=='lcall':
            api=calls[i.address];sp=m.getreg('sp')
            if api==('GDI',66):color=m.pop(4);m.setreg('ax',0x1111)
            elif api==('GDI',45):m.pop(2);m.pop(2);m.setreg('ax',0x2222)
            elif api==('GDI',69):assert m.pop(2)==0x1111
            elif api==('USER',72):
                bottom,right,top,left=[m.pop(2)for _ in range(4)];pointer=m.pop(2);m.pop(2)
                for n,value in enumerate((left,top,right,bottom)):m.write(pointer+2*n,value,2)
            elif api==('USER',81):
                assert m.pop(2)==0x1111;pointer=m.pop(2);m.pop(2);assert m.pop(2)==0xbeef
                rectangles.append([m.read(pointer+2*n,2)for n in range(4)])
            else:assert api==('internal',6,0x5f1) # cdecl graphics-port setup; original ADD SP follows.
        else:raise AssertionError((hex(i.address),op))
    raise AssertionError('Original score loop did not finish')
def expected(values):
    return [[10+6*i,327,14+6*i,331]if values[i+19]==1 else[11+6*i,328,13+6*i,330]for i in range(1,28 if values[46]==1 else 27)]
cases=[[0]*100,[1]*100]
for index in range(20,47):
    for value in(-1,1,2):row=[0]*100;row[index]=value;cases.append(row)
rng=random.Random(19112026);cases.extend([[rng.choice((-1,0,1,2))for _ in range(100)]for _ in range(128)])
for values in cases:assert run(values)==expected(values)==run(values,9999)
zero=run([0]*100);all_done=run([1]*100);assert len(zero)==26 and all(r[2]-r[0]==2 for r in zero)and len(all_done)==27 and all(r[2]-r[0]==4 for r in all_done)
bindings=[]
for scene,flag in[(511,27),(522,38),(530,46)]:
    k=next(k for k in range(34)if struct.unpack_from('<i',b,cpu.base(4)+0x6c94+4*k)[0]==scene);entry=struct.unpack_from('<H',b,cpu.base(4)+0x6d1c+2*k)[0];block=[]
    for i in cpu.md.disasm(b[cpu.base(4)+entry:cpu.base(4)+entry+80],entry):
        block.append(i)
        if i.mnemonic=='jmp'and i.operands[0].imm==0x5a8e:break
    assert any(i.mnemonic=='mov'and i.operands[0].type==cpu.X86_OP_MEM and i.operands[0].mem.disp==10+4*flag and i.operands[1].type==cpu.X86_OP_IMM and i.operands[1].imm==1 for i in block)
    bindings.append(dict(scene=scene,global_flag=flag,handler=f'4:{entry:04x}'))
screens=[]
if a.screenshots:
    from PIL import Image
    for path in a.screenshots:
        im=Image.open(path).convert('RGB');columns=[]
        for x in range(35,330):
            ys=[y for y in range(551,570)if min(im.getpixel((x,y)))>180]
            if ys:columns.append((x,min(ys),max(ys)))
        groups=[]
        for col in columns:
            if not groups or col[0]>groups[-1][-1][0]+1:groups.append([])
            groups[-1].append(col)
        boxes=[[g[0][0],min(v[1]for v in g),g[-1][0]+1,max(v[2]for v in g)+1]for g in groups];assert len(boxes)==26
        assert all(r-l<=3 or r-l>=5 for l,t,r,bottom in boxes)
        bits=[int(r-l>=5)for l,t,r,bottom in boxes];screens.append(dict(filename=path.name,sha256=sha(path),markers=26,squares=sum(bits),dots=26-sum(bits),bits=bits,bounding_boxes=boxes))
changes=[]
if screens:
    changes=[dict(position=i+1,global_flag=20+i,before=x,after=y)for i,(x,y)in enumerate(zip(screens[0]['bits'],screens[1]['bits']))if x!=y]
    assert changes==[dict(position=8,global_flag=27,before=0,after=1),dict(position=19,global_flag=38,before=0,after=1)]
proof=dict(status='ORIGINAL_PROGRESS_INDICATOR_INSTRUCTION_MODEL_PASS',at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),original_exe_sha256=hashlib.sha256(b).hexdigest(),routine='3:39ca-3adf',routine_sha256=hashlib.sha256(b[cpu.base(3)+0x39ca:cpu.base(3)+0x3ae0]).hexdigest(),modeled_instruction_cases=len(cases),runs_with_distinct_completion_counter=2*len(cases),global_flag_first=20,global_flag_last=46,visible_markers_before_final=26,visible_markers_after_final=27,white_rgb=0xffffff,solved_rectangle_size=[4,4],unsolved_rectangle_size=[2,2],solved_y=327,dot_y=328,horizontal_stride=6,only_value_one_is_solved=True,draw_call='9:1911',draw_gate=['_nav_place!=0','_monitor_status!=0'],monitor_initial_value=1,original_completion_bindings=bindings,screenshot_observations=screens,screenshot_changes=changes,production_engine_changed=False,limits=['Original x86 instructions execute in a bounded interpreter;GDI/USER drawing and port calls are modeled,not original Windows runtime execution','Screenshot segmentation uses the explicitly identified row in these two supplied captures;resampling prevents a full pixel-identical certificate','Flags identify completion groups,not separate indicators for every stage or every puzzle scene','Current ScummVM source is inspected separately;no renderer change or native-game regression is claimed'])
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(proof['status'],len(cases),'cases',[(s['squares'],s['dots'])for s in screens])
