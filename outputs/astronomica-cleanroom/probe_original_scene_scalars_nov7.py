"""Replay original Win16 predicates AND link/control instructions into a native fixture.

Allocation and time APIs are modeled, operand parsing is independently byte-verified,
and noncontrol commands become trace markers. This is not original Windows execution.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json,struct,sys
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('inventory',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deps',type=Path,default=Path('work/fresh-20260913/deps-verified'));a=ap.parse_args()
sys.path.insert(0,str(a.deps.resolve()))
import capstone
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
from capstone.x86_const import X86_OP_IMM,X86_OP_MEM,X86_OP_REG
sha=lambda b:hashlib.sha256(b).hexdigest()
exe=(a.root/'SETUP/ASTRO.EXE').read_bytes();assert sha(exe)=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
ne=struct.unpack_from('<I',exe,0x3c)[0];assert exe[ne:ne+2]==b'NE'
table=ne+struct.unpack_from('<H',exe,ne+0x22)[0];shift=struct.unpack_from('<H',exe,ne+0x32)[0]
def base(n):return struct.unpack_from('<H',exe,table+8*(n-1))[0]<<shift
md=Cs(CS_ARCH_X86,CS_MODE_16);md.detail=True
reader={i.address:i for i in md.disasm(exe[base(9)+0x2ff2:base(9)+0x3528],0x2ff2)}
execute={i.address:i for i in md.disasm(exe[base(15)+0x60:base(15)+0x1799],0x60)}
execute.update({i.address:i for i in md.disasm(exe[base(15)+0x1d20:base(15)+0x1d6f],0x1d20)})
rng={i.address:i for start,end in((0xb3c,0xb53),(0xb6b,0xb94))for i in md.disasm(exe[base(1)+start:base(1)+end],start)}
ops=struct.unpack_from('<49i',exe,base(9)+0x3528);targets=struct.unpack_from('<49H',exe,base(9)+0x35ec)
dispatch=dict(zip(ops,targets));assert {k:dispatch[k]for k in(31,42,45)}=={31:0x3289,42:0x334e,45:0x335d}
counts=collections.Counter();calls=collections.Counter()
class Machine:
    def __init__(self):
        self.carry=0;self.fpu=[];self.mem={};self.reg=dict(eax=0,ebx=0,ecx=0,edx=0,ebp=0x8000,esp=0x7000,esi=0,edi=0,ds=0x2000,ss=0x3000,es=0x4000,cs=0x5000);self.comparison=(0,0);self.next_allocation=0
    def get(self,name):
        if not name:return 0
        return self.reg.get('e'+name,0)&65535 if name in('ax','bx','cx','dx','bp','sp','si','di')else self.reg[name]
    def put(self,name,value):
        if name in('ax','bx','cx','dx','bp','sp','si','di'):
            key='e'+name;self.reg[key]=(self.reg[key]&0xffff0000)|(value&65535)
        else:self.reg[name]=value&(65535 if name in('ds','ss','es')else 0xffffffff)
    def read(self,segment,offset,size):return sum(self.mem.get((segment<<16)|((offset+i)&65535),0)<<(8*i)for i in range(size))
    def write(self,segment,offset,size,value):
        assert segment in(0x2000,0x3000,0x4000,0x5000),'Unmapped modeled selector'
        for i in range(size):self.mem[(segment<<16)|((offset+i)&65535)]=(value>>(8*i))&255
    def address(self,i,o):
        segment=i.reg_name(o.mem.segment)or('ss'if i.reg_name(o.mem.base)in('bp','sp','ebp','esp')else'ds')
        offset=(self.get(i.reg_name(o.mem.base))+self.get(i.reg_name(o.mem.index))*o.mem.scale+o.mem.disp)&65535
        return self.get(segment),offset
    def value(self,i,o):
        if o.type==X86_OP_IMM:return o.imm
        if o.type==X86_OP_REG:return self.get(i.reg_name(o.reg))
        assert o.type==X86_OP_MEM
        return self.read(*self.address(i,o),o.size)
    def assign(self,i,o,value):
        if o.type==X86_OP_REG:self.put(i.reg_name(o.reg),value)
        else:self.write(*self.address(i,o),o.size,value)
    def stack(self,disp,size,value=None):
        if value is None:return self.read(self.get('ss'),(self.get('bp')+disp)&65535,size)
        self.write(self.get('ss'),(self.get('bp')+disp)&65535,size,value)
    def run(self,ins,start,stop,kind):
        pc=start;steps=0
        while pc!=stop:
            assert steps<(10000 if kind=='choose-bit'else 200)and pc in ins,('Unbounded/unknown instruction',kind,hex(pc));steps+=1
            i=ins[pc];op=i.mnemonic;o=i.operands;following=pc+i.size;counts[(kind,pc)]+=1
            if op=='mov':self.assign(i,o[0],self.value(i,o[1]))
            elif op=='les':
                value=self.read(*self.address(i,o[1]),4);self.put(i.reg_name(o[0].reg),value&65535);self.put('es',value>>16)
            elif op=='xchg':
                left=self.value(i,o[0]);right=self.value(i,o[1]);self.assign(i,o[0],right);self.assign(i,o[1],left)
            elif op in('movsx','movzx'):
                value=self.value(i,o[1]);bits=o[1].size*8
                if op=='movsx'and value&(1<<(bits-1)):value-=1<<bits
                self.assign(i,o[0],value)
            elif op=='cwde':
                value=self.get('ax');self.put('eax',value-65536 if value&32768 else value)
            elif op=='cdq':self.put('edx',0xffffffff if self.get('eax')&0x80000000 else 0)
            elif op=='inc':self.assign(i,o[0],self.value(i,o[0])+1)
            elif op=='jcxz':
                if not self.get('cx'):following=self.value(i,o[0])
            elif op=='mul':
                assert o[0].size==2;value=self.get('ax')*self.value(i,o[0]);self.put('ax',value&65535);self.put('dx',value>>16)
            elif op=='imul':
                assert len(o)in(2,3)and o[0].size in(2,4)
                bits=o[0].size*8;mask=(1<<bits)-1
                signed=lambda v:(v&mask)-(1<<bits)if v&(1<<(bits-1))else(v&mask)
                left,right=(o[0],o[1])if len(o)==2 else(o[1],o[2]);self.assign(i,o[0],signed(self.value(i,left))*signed(self.value(i,right)))
            elif op=='idiv':
                assert o[0].size==4
                dividend=(self.get('edx')<<32)|self.get('eax');dividend-=1<<64 if dividend&(1<<63)else 0
                divisor=self.value(i,o[0]);divisor-=1<<32 if divisor&(1<<31)else 0
                assert divisor
                quotient=abs(dividend)//abs(divisor);quotient=-quotient if(dividend<0)!=(divisor<0)else quotient
                assert -2147483648<=quotient<=2147483647
                self.put('eax',quotient);self.put('edx',dividend-quotient*divisor)
            elif op in('add','adc','sub','shl'):
                left=self.value(i,o[0]);right=self.value(i,o[1]);result=left+right+(self.carry if op=='adc'else 0)if op in('add','adc')else left-right if op=='sub'else left<<right
                self.carry=int(result<0 or result>=(1<<(8*o[0].size)));self.assign(i,o[0],result)
            elif op=='loop':
                self.put('cx',self.get('cx')-1)
                if self.get('cx'):following=self.value(i,o[0])
            elif op in('cmp','or','xor','test','and'):
                left=self.value(i,o[0]);right=self.value(i,o[1]);bits=o[0].size*8;mask=(1<<bits)-1
                if op=='test':left=left&right;right=0
                elif op!='cmp':left=(left|right)if op=='or'else(left&right)if op=='and'else(left^right);self.assign(i,o[0],left);right=0
                signed=lambda v:(v&mask)-(1<<bits)if(v&mask)&(1<<(bits-1))else(v&mask)
                self.comparison=(signed(left),signed(right))
            elif op in('je','jne','jl','jg','jge','jle','jmp'):
                left,right=self.comparison
                if op=='jmp'or(op=='je'and left==right)or(op=='jne'and left!=right)or(op=='jl'and left<right)or(op=='jg'and left>right)or(op=='jge'and left>=right)or(op=='jle'and left<=right):following=self.value(i,o[0])
            elif op=='push':
                self.put('sp',self.get('sp')-o[0].size);self.write(self.get('ss'),self.get('sp'),o[0].size,self.value(i,o[0]))
            elif op=='pop':
                self.assign(i,o[0],self.read(self.get('ss'),self.get('sp'),o[0].size));self.put('sp',self.get('sp')+o[0].size)
            elif op in('wait','nop'):pass
            elif op in('fild','fld'):
                value=self.value(i,o[0])
                if op=='fild':value=value-0x100000000 if value&0x80000000 else value
                else:value=struct.unpack('<f'if o[0].size==4 else '<d',value.to_bytes(o[0].size,'little'))[0]
                self.fpu.append(float(value))
            elif op=='fstp':
                assert o[0].size==8 and self.fpu
                self.assign(i,o[0],int.from_bytes(struct.pack('<d',self.fpu.pop()),'little'))
            elif op=='call':
                calls[(kind,pc)]+=1
                if kind in('rng','rng-next-draw')and pc==0xb7b:self.run(rng,0xb3c,0xb52,'multiply')
                elif kind in('range-command','choose-bit')and pc in(0x1543,0x1574,0x131a):
                    saved_bp,saved_sp,saved_si=self.get('bp'),self.get('sp'),self.get('si')
                    low=self.read(self.get('ss'),saved_sp+2,2);high=self.read(self.get('ss'),saved_sp+4,2)
                    assert(0<=low<=high<=32767 and high-low<32767)or(pc==0x131a and low==1 and high==0)
                    self.put('bp',0x6000);self.put('sp',0x5e00);self.stack(6,2,low);self.stack(8,2,high)
                    self.run(execute,0x1d2e,0x1d67,'range-helper')
                    self.put('bp',saved_bp);self.put('sp',saved_sp+2);self.put('si',saved_si)
                else:raise AssertionError(('Unmodeled near call',kind,hex(pc)))
            elif op=='lcall':
                calls[(kind,pc)]+=1
                if kind=='range-helper'and pc==0x1d3f:self.run(rng,0xb6b,0xb93,'rng')
                elif kind in('bits','choose-bit')and pc in(0xf66,0xfcb,0x101a,0x108d,0x10f4,0x1144,0x12d3,0x135b,0x13e8,0x1448):
                    # Original imported BC40RTL ordinal632 (_pow); model only exact2^integer0..30.
                    decode=lambda off:struct.unpack('<d',self.read(self.get('ss'),off,8).to_bytes(8,'little'))[0]
                    radix=decode(self.get('sp'));exponent=decode(self.get('sp')+8)
                    assert radix==2.0 and exponent==int(exponent)and 0<=exponent<=30
                    self.fpu.append(float(1<<int(exponent)))
                elif kind in('bits','choose-bit')and pc in(0xf6e,0xfd3,0x1022,0x1095,0x10fc,0x114c,0x12db,0x1363,0x13f0,0x1450):
                    # Original internal FTOL@1:15c3: bounded exact integer conversion, not helper-body execution.
                    value=self.fpu.pop();assert value==int(value)and 1<=value<=0x40000000
                    self.put('ax',int(value)&65535);self.put('dx',int(value)>>16)
                elif kind=='reader'and pc==0x34a2:self.put('ax',self.next_allocation&65535);self.put('dx',self.next_allocation>>16)
                elif kind=='execute'and pc in(0x1669,0x16c3,0x1730):self.put('ax',0);self.put('dx',0)
                else:raise AssertionError(('Unmodeled original external call',kind,hex(pc)))
            else:raise AssertionError(('Unmodeled instruction',kind,hex(pc),op))
            pc=following
def ptr(index):return 0x40000010+index*0x48
def index(pointer):
    assert pointer>>16==0x4000 and(pointer&65535)>=0x10 and((pointer&65535)-0x10)%0x48==0
    return((pointer&65535)-0x10)//0x48
def links_for(body):
    m=Machine();m.stack(-0xe,4,0);m.stack(-0xa,4,ptr(0))
    for n,c in enumerate(body):
        pointer=ptr(n);assert m.stack(-0xa,4)==pointer
        m.write(0x4000,pointer&65535,4,c['opcode'])
        if c['opcode']==31:
            m.run(reader,0x3289,0x3295,'reader');m.run(reader,0x3337,0x334b,'reader')
        elif c['opcode']in(42,45):m.run(reader,dispatch[c['opcode']],0x33f4,'reader')
        m.stack(-6,4,body[n+1]['opcode']if n+1<len(body)else 0)
        m.run(reader,0x3436,0x345a,'reader');m.next_allocation=ptr(n+1);m.run(reader,0x345a,0x34fe,'reader')
    m.run(reader,0x3507,0x3521,'reader')
    links=[m.read(0x4000,(ptr(n)&65535)+0x40,4)for n in range(len(body))]
    links=[index(p)if p else -1 for p in links]
    # Exact source-model cross-check is separate from the instruction replay.
    expected=[-1]*len(body);last=-1
    for n,c in enumerate(body):
        if c['opcode']==31:last=n
        if last>=0 and n+1<len(body):
            if c['opcode']==45:expected[last]=n
            if c['opcode']==42:expected[last]=n+1
    assert links==expected
    for n,c in enumerate(body):
        m.write(0x4000,(ptr(n)&65535),4,c['opcode']if c['opcode']in(31,32,33,39,40,42,45,46)else 9)
        m.write(0x4000,(ptr(n)&65535)+0x34,4,0xffffffff)
    return m,links
def controlled_value(seed,scope,ident,mode):
    raw=(seed+(ident*0x9e3779b9+scope*0x7f4a7c15 if mode else 0))&0xffffffff
    return raw-0x100000000 if raw&0x80000000 else raw

def trace_for(original,body,seed,mode,widths):
    m=Machine();m.mem=original.mem.copy();position=0;trace=[];actions=[]
    # Exact original code-segment tables, with separate modeled global/local owners.
    for off in range(0x17a2,0x187a):m.write(0x5000,off,1,exe[base(15)+off])
    m.write(0x2000,0x726,4,0x40000000);m.write(0x2000,0x984,4,seed&65535)
    m.write(0x2000,0x7a8,4,0x4000c000);m.write(0x2000,0xc88,4,0x4000d000)
    for ident in range(100):
        m.write(0x4000,0xc000+0xa+ident*4,4,controlled_value(seed,0,ident,mode))
        m.write(0x4000,0xd000+0x3f8+ident*4,4,controlled_value(seed,1,ident,mode))
    for ident in range(100):
        m.write(0x4000,0xc000+0x19a+ident*12,4,widths[ident]);m.write(0x4000,0xd000+0x588+ident*12,4,widths[100+ident])
    for n,c in enumerate(body):
        if c['opcode']in(31,32,33,39,40,46):
            for j,value in enumerate(c['args']):m.write(0x4000,(ptr(n)&65535)+4+j*4,4,value)
    while position is not None:
        assert len(trace)<=len(body)and 0<=position<len(body);trace.append(position);c=body[position]
        m.stack(6,4,ptr(position));m.stack(-0xa,2,0);m.put('si',1);m.write(0x2000,0xfce,4,0)
        if c['opcode']==31:
            m.run(execute,0xc70,0x1636,'predicate')
        elif c['opcode']==39:
            m.put('sp',m.get('bp')-0x142);m.run(execute,0x11a8,0x1636,'choose-bit');assert not m.fpu
        elif c['opcode']==40:
            m.put('sp',m.get('bp')-0x142);m.run(execute,0x1508,0x1636,'range-command')
        elif c['opcode']==33:
            m.put('sp',m.get('bp')-0x142);m.run(execute,0xf08,0x1636,'bits');assert not m.fpu
        elif c['opcode']==32:m.run(execute,0xe99,0x1636,'assignment')
        elif c['opcode']==46:m.run(execute,0x159b,0x1636,'addition')
        elif c['opcode']==42:m.run(execute,0xe81,0x1636,'execute')
        elif c['opcode']==45:m.run(execute,0xe8a,0x1636,'execute')
        else:actions.append(position)
        m.run(execute,0x1636,0x1799,'execute')
        following=m.read(0x2000,0xfce,4)if m.get('ax')else 0
        if following:
            next_position=index(following);assert next_position>position;position=next_position
        else:position=None
    h=2166136261
    for n in actions:h=((h^(n+1))*16777619)&0xffffffff
    state=2166136261;values=[]
    for scope,offset in ((0,0xc000+0xa),(1,0xd000+0x3f8)):
        for ident in range(100):
            value=m.read(0x4000,offset+ident*4,4);values.append(value);state=((state^value)*16777619)&0xffffffff
    m.run(rng,0xb6b,0xb93,"rng-next-draw");return h,len(trace),len(actions),state,values,m.get("ax")
inventory=json.loads(a.inventory.read_text());assert inventory['status']=='ORIGINAL_HYP_SYNTACTIC_BRANCH_INVENTORY_ONLY'
# Explicit synthetic scripts exercise global comparisons absent from original corpus,
# id99, negative operands, inclusive bounds, reversed bounds and integer extremes.
synthetic_scripts=[]
for scope in range(2):
    for ident in (0,99):
        for comparison in range(4):
            for low,high in ((-2147483648,-2147483648),(-1,1),(2147483647,2147483647),(1,-1)):
                indices=[]
                for opcode,args in ((32,[scope,ident,high]),(46,[scope,ident,low]),(33,[scope,ident,comparison*10,1]),(33,[scope,ident,comparison*10,0]),(40,[scope,ident,(0,1,0,32767)[comparison],(0,3,32766,32767)[comparison]]),(39,[scope,ident,scope if comparison==0 else 1-scope,ident if comparison==0 else 99-ident]),(31,[scope,ident,low,high,comparison,0]),(9,[1]),(42,[]),(9,[2])):
                    indices.append(len(inventory['commands']));inventory['commands'].append(dict(opcode=opcode,args=args))
                synthetic_scripts.append(dict(trigger='synthetic-edge',command_indices=indices))
for scope in range(2):
    for ident in (0,99):
        for same in (False,True):
            indices=[]
            for opcode,args in ((39,[scope,ident,scope if same else 1-scope,ident if same else 99-ident]),(9,[1])):
                indices.append(len(inventory['commands']));inventory['commands'].append(dict(opcode=opcode,args=args))
            synthetic_scripts.append(dict(trigger='synthetic-mask-exhaustion',command_indices=indices))
inventory['scenes'].append(dict(scene=10000,scripts=synthetic_scripts))
records=[];fixtures=bytearray(b'CBLK0008');summary=[];case_count=0
metadata_checks=[]
for scene in inventory['scenes']:
    widths=[31]*200 if scene['scene']==10000 else [0]*200
    if scene['scene']!=10000:
        data=(a.root/scene['path']).read_bytes();assert sha(data)==scene['sha256']
        raw=scene['conditions'];start=scene['parsed_bytes']-len(raw)*24-4
        assert start>=0 and struct.unpack_from('<i',data,start)[0]==len(raw)
        for i,row in enumerate(raw):
            assert list(struct.unpack_from('<6i',data,start+4+i*24))==row
            if row[0]in(0,1)and 0<=row[1]<100:widths[row[0]*100+row[1]]=row[2]
        metadata_checks.append(dict(scene=scene['scene'],records=len(raw),condition_table_sha256=sha(data[start:scene['parsed_bytes']])))
    for ordinal,script in enumerate(scene['scripts']):
        body=[inventory['commands'][i]for i in script['command_indices']]
        if not body:continue
        for c in body:
            if c['opcode']==39:assert 1<=widths[c['args'][0]*100+c['args'][1]]<=31
        machine,links=links_for(body)
        seeds={-2147483648,-1,0,1,1073741823,2147483647}
        for c in body:
            if c['opcode']==31:
                for boundary in c['args'][2:4]:
                    seeds.update(v for v in(boundary-1,boundary,boundary+1)if -2147483648<=v<=2147483647)
        rows=[(seed,mode,*trace_for(machine,body,seed,mode,widths))for mode in (0,1)for seed in sorted(seeds)];case_count+=len(rows)
        records.append((scene['scene'],ordinal,body,rows,widths));summary.append(dict(scene=scene['scene'],trigger=script['trigger'],commands=len(body),cases=len(rows),links=links))
fixtures.extend(struct.pack('<I',len(records)))
for scene,ordinal,body,rows,widths in records:
    fixtures.extend(struct.pack('<4I',scene,ordinal,len(body),len(rows)));fixtures.extend(struct.pack('<200i',*widths))
    for n,c in enumerate(body):
        opcode=c['opcode']if c['opcode']in(31,32,33,39,40,42,45,46)else 9;args=c['args']if opcode in(31,32,33,39,40,46)else[n+1]if opcode==9 else[]
        fixtures.extend(struct.pack('<II',opcode,len(args)))
        for v in args:assert isinstance(v,int);fixtures.extend(struct.pack('<i',v))
    for seed,mode,h,executed,actions,state,values,next_draw in rows:
        fixtures.extend(struct.pack('<iIIIII',seed,mode,h,executed,actions,state));fixtures.extend(struct.pack('<200I',*values));fixtures.extend(struct.pack('<I',next_draw))
a.out.mkdir(exist_ok=False,parents=True);(a.out/'control-fixture.bin').write_bytes(fixtures)
proof=dict(status='ORIGINAL_WIN16_SCENE_METADATA_SCALAR_REPLAY_READY',created_at=datetime.now(timezone.utc).isoformat(),original_exe_sha256=sha(exe),inventory_sha256=sha(a.inventory.read_bytes()),author_sha256=sha(Path(__file__).read_bytes()),capstone_version=capstone.__version__,fixture_sha256=sha(fixtures),nonempty_scripts=len(records),control_cases=case_count,original_commands=sum(len(r[2])for r in records),source_original_commands=sum(len(r[2])for r in records if r[0]!=10000),condition_tests=inventory['summary']['condition_tests'],reader_link_model_matches=True,predicate_body_replayed=True,heterogeneous_values=True,assignment_body_replayed=True,addition_body_replayed=True,bit_handler_replayed=True,bit_floating_helpers_modeled=True,range_handler_replayed=True,range_helper_replayed=True,rng_and_multiply_bodies_replayed=True,post_script_rng_draw_checked=True,choose_bit_handler_replayed=True,original_metadata_byte_verified=True,synthetic_metadata_width=31,metadata_scenes=len(metadata_checks),metadata_checks=metadata_checks,scalar_words_checked=200,scalar_comparison="all200words_exact_plus_FNV_summary",synthetic_scripts=len(synthetic_scripts),original_nonempty_scripts=len(records)-len(synthetic_scripts),executed_instruction_steps=sum(counts.values()),instruction_sites=len(counts),instruction_site_counts={kind+':'+format(pc,'04x'):n for(kind,pc),n in sorted(counts.items())},modeled_calls=[dict(kind=k,address=hex(p),count=n)for(k,p),n in sorted(calls.items())],reader_ranges=[['9:3289','9:3295'],['9:3337','9:334b'],['9:334e','9:3357'],['9:335d','9:3366'],['9:3436','9:34fe'],['9:3507','9:3521']],execute_ranges=[['15:11a8','15:1508'],['1:0b3c','1:0b53'],['1:0b6b','1:0b94'],['15:1508','15:159b'],['15:1d2e','15:1d67'],['15:0f08','15:118b'],['15:0e99','15:0f08'],['15:159b','15:1636'],['15:0c70','15:0e81'],['15:0e81','15:0e99'],['15:1636','15:1799']],scripts=summary,limits=['Original Win16program not run; this is bounded instruction interpretation','BC40RTL ordinal632 (_pow) and internal FTOL@ helper results modeled only for exactly representable2^integer0..30; helper bodies and general x87 behavior not executed','Resource operand-copy calls omitted after independent exact-byte inventory verification','Allocator returns deterministic distinct modeled far pointers; clock API returns0','Original scene widths are byte-verified from their final condition tables; synthetic widths31; scalar states still controlled rather than reconstructed gameplay history','Original predicate body and eleven CS dispatch tables replayed; scalar owner pointers and controlled uniform/heterogeneous values modeled, no original Windows execution','Commands other than31/32/33/39/40/42/45/46 replaced by sound-action trace markers with no sound handler; original gameplay effects are not executed','All command delays normalized to-1 for topology only; no original timer fidelity claim','Uniform and heterogeneous controlled cases are not exhaustive real gameplay states and do not close A03','Synthetic cases explicitly separate from original corpus; original command total in this extended fixture includes656 synthetic positions'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Original scalar/control fixture ready:',len(records),'scripts,',case_count,'controlled cases,',sum(counts.values()),'original instruction steps')
