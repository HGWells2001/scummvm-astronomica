"""Trace movie replay in the original bundled QCMC, not in a replacement player."""
import hashlib, json, struct
import probe_p526_motion as p

path=p.args.root/'QTW/QCMC.QTC'
data=path.read_bytes()
ne=struct.unpack_from('<I',data,0x3c)[0]
assert data[ne:ne+2]==b'NE'
table=ne+struct.unpack_from('<H',data,ne+0x22)[0]
shift=struct.unpack_from('<H',data,ne+0x32)[0]
def base(seg): return struct.unpack_from('<H',data,table+8*(seg-1))[0]<<shift
def relocation(seg,address):
    size=struct.unpack_from('<H',data,table+8*(seg-1)+2)[0]
    for row in range(struct.unpack_from('<H',data,base(seg)+size)[0]):
        typ,flags,src,target,offset=struct.unpack_from('<BBHHH',data,base(seg)+size+2+8*row)
        seen=set()
        while src!=65535 and src not in seen and src+2<=size:
            seen.add(src)
            if src==address:return (typ,flags,target,offset)
            if flags&4:break
            src=struct.unpack_from('<H',data,base(seg)+src)[0]
    raise AssertionError((seg,address))
def code(seg,start,end):
    return list(p.md.disasm(data[base(seg)+start:base(seg)+end],start))
def has(seg,start,end,mnemonic,operands):
    assert any(i.mnemonic==mnemonic and i.op_str==operands for i in code(seg,start,end))
# Original ASTRO MCDoAction wrapper dispatches group1, selector1.
original=list(p.md.disasm(p.exe[p.base(1)+0x7d4:p.base(1)+0x7e1],0x7d4))
assert any(i.op_str=='bx, 1' for i in original)
assert any(i.op_str=='ax, 1' for i in original)
# Component descriptor names the standard movie controller and points to3:26ec.
assert data[base(7)+0xd6:base(7)+0xde]==b'playstd '
assert struct.unpack_from('<H',data,base(7)+0xea)[0]==0x26ec
assert relocation(7,0xec)==(2,0,3,0)
assert relocation(3,0x1b)==(2,0,4,0)
assert relocation(4,0xe54)==(2,0,2,0)
assert relocation(4,0xebe)==(2,0,2,0)
assert struct.unpack_from('<H',data,base(3)+0x26b2)[0]==0
has(3,0,0x23,'lcall','0xffff, 0') # selector1 forwards into segment4 via relocation
assert struct.unpack_from('<H',data,base(4)+0x7e+14)[0]==0xd98 # action8
assert struct.unpack_from('<H',data,base(4)+0x7e+22)[0]==0x1124 # action12
# Match the movie-time/duration API selectors with ASTRO's named wrappers.
for native,wrapped,selector in [(0x768,0x3a0a,0x36),(0x600,0x38a2,0x12)]:
    asm=list(p.md.disasm(p.exe[p.base(1)+native:p.base(1)+native+10],native))
    assert any(i.mnemonic=='mov' and i.op_str==f'bx, 0x{selector:x}' for i in asm)
    has(2,wrapped,wrapped+10,'mov',f'bx, 0x{selector:x}')
has(4,0xe44,0xe61,'lcall','0xebe, 0x3a0a')
has(4,0xeaa,0xec3,'lcall','0x7c6, 0x38a2')
has(4,0xf09,0xf1a,'mov','ax, word ptr [bp - 0xf6]')
has(4,0xf09,0xf1a,'jl','0xf2f')
has(4,0xf53,0xf75,'push','0xc')
# Execute the original 16-bit boundary branch independently of ScummVM.
# Inputs are the already-resolved range/current time and signed rate high word.
branch={i.address:i for i in code(4,0xef3,0xf37)}
def replay_branch(start,end,current,rate_high):
    regs={'ax':0,'dx':0}
    mem={0xf2:current&65535,0xf0:current>>16,0xf6:start&65535,
         0xf4:start>>16,0xfa:end&65535,0xf8:end>>16,0xec:rate_high&65535}
    def value(operand):
        if operand in regs:return regs[operand]
        if operand.startswith('word ptr [bp - '):return mem[int(operand[15:-1],16)]
        return int(operand,0)&65535
    pc=0xef3;cf=zf=sf=of=False
    for _ in range(40):
        if pc==0xf85:return current
        if pc==0xf37:return (regs['dx']<<16)|regs['ax']
        i=branch[pc];pc+=i.size;args=i.op_str.split(', ')
        if i.mnemonic=='mov':regs[args[0]]=value(args[1])
        elif i.mnemonic=='cmp':
            a,b=map(value,args);r=(a-b)&65535
            cf=a<b;zf=r==0;sf=bool(r&0x8000);of=bool((a^b)&(a^r)&0x8000)
        else:
            take={'jmp':True,'ja':not cf and not zf,'jb':cf,'jge':sf==of,'jl':sf!=of}[i.mnemonic]
            if take:pc=int(args[0],0)
    raise AssertionError('branch did not terminate')
cases=0;case_hash=hashlib.sha256()
for start in (0,1,65534,65535,65536,0x7fffffff,0xffff0000):
    for length in (1,2,30,65535,65536):
        end=start+length
        if end>0xffffffff:continue
        for current in sorted({0,max(0,start-1),start,start+1,(start+end)//2,end-1,end,min(0xffffffff,end+1),0xffffffff}):
            for high in (-1,0,1):
                expected=(start if high>=0 else end) if current<=start or current>=end else current
                got=replay_branch(start,end,current,high)
                assert got==expected,(start,end,current,high,got,expected)
                case_hash.update(struct.pack('<IIIIi',start,end,current,got,high));cases+=1
regions=[(3,0,0x23),(3,0x26b0,0x2718),(4,0xd98,0xf85),(4,0x1124,0x119d),(7,0xd6,0xf2)]
out=dict(status='Static original binary trace; no native replay implementation yet',
    original_branch_cases=cases,original_branch_sha256=case_hash.hexdigest(),
    source='QTW/QCMC.QTC',sha256=hashlib.sha256(data).hexdigest(),
    dispatch='ASTRO1:07d4 group1/selector1 -> QCMC3:26ec table entry1 ->3:0000 ->4:0000; action8 ->4:0d98',
    findings=[
      'Action8 with nonzero rate queries movie time and duration; selected-range flag can substitute start/end.',
      '4:0ef3 compares current time with end. At/beyond end, positive rate selects start; negative rate selects end.',
      'Changed time is sent through controller action12 at4:0f59. In-range positive playback retains current time.',
      'This explains why a finished movie must be restarted before the P222 repeat control plays again. Verify native integration separately.'
    ],
    regions={f'{seg}:{a:04x}-{b:04x}':dict(sha256=hashlib.sha256(data[base(seg)+a:base(seg)+b]).hexdigest(),
        instructions=[f'{i.address:04x} {i.mnemonic} {i.op_str}' for i in code(seg,a,b)] if seg!=7 else []) for seg,a,b in regions})
p.args.out.write_text(json.dumps(out,indent=2))
print('Original QCMC replay dispatch and boundary trace: PASS (static research)')
