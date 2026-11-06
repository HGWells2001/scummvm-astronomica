"""Replay bounded original Win16 link/control instructions; emit a local native-runner fixture.

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
ops=struct.unpack_from('<49i',exe,base(9)+0x3528);targets=struct.unpack_from('<49H',exe,base(9)+0x35ec)
dispatch=dict(zip(ops,targets));assert {k:dispatch[k]for k in(31,42,45)}=={31:0x3289,42:0x334e,45:0x335d}
counts=collections.Counter();calls=collections.Counter()
class Machine:
    def __init__(self):
        self.mem={};self.reg=dict(eax=0,ebx=0,ecx=0,edx=0,ebp=0x8000,esp=0x7000,esi=0,edi=0,ds=0x2000,ss=0x3000,es=0x4000);self.comparison=(0,0);self.next_allocation=0
    def get(self,name):
        if not name:return 0
        return self.reg.get('e'+name,0)&65535 if name in('ax','bx','cx','dx','bp','sp','si','di')else self.reg[name]
    def put(self,name,value):
        if name in('ax','bx','cx','dx','bp','sp','si','di'):
            key='e'+name;self.reg[key]=(self.reg[key]&0xffff0000)|(value&65535)
        else:self.reg[name]=value&(65535 if name in('ds','ss','es')else 0xffffffff)
    def read(self,segment,offset,size):return sum(self.mem.get((segment<<16)|((offset+i)&65535),0)<<(8*i)for i in range(size))
    def write(self,segment,offset,size,value):
        assert segment in(0x2000,0x3000,0x4000),'Unmapped modeled selector'
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
            assert steps<200 and pc in ins,('Unbounded/unknown instruction',kind,hex(pc));steps+=1
            i=ins[pc];op=i.mnemonic;o=i.operands;following=pc+i.size;counts[(kind,pc)]+=1
            if op=='mov':self.assign(i,o[0],self.value(i,o[1]))
            elif op=='les':
                value=self.read(*self.address(i,o[1]),4);self.put(i.reg_name(o[0].reg),value&65535);self.put('es',value>>16)
            elif op in('cmp','or','xor'):
                left=self.value(i,o[0]);right=self.value(i,o[1]);bits=o[0].size*8;mask=(1<<bits)-1
                if op!='cmp':left=(left|right)if op=='or'else(left^right);self.assign(i,o[0],left);right=0
                signed=lambda v:(v&mask)-(1<<bits)if(v&mask)&(1<<(bits-1))else(v&mask)
                self.comparison=(signed(left),signed(right))
            elif op in('je','jne','jl','jg','jmp'):
                left,right=self.comparison
                if op=='jmp'or(op=='je'and left==right)or(op=='jne'and left!=right)or(op=='jl'and left<right)or(op=='jg'and left>right):following=self.value(i,o[0])
            elif op=='push':
                self.put('sp',self.get('sp')-o[0].size);self.write(self.get('ss'),self.get('sp'),o[0].size,self.value(i,o[0]))
            elif op=='pop':
                self.assign(i,o[0],self.read(self.get('ss'),self.get('sp'),o[0].size));self.put('sp',self.get('sp')+o[0].size)
            elif op=='lcall':
                calls[(kind,pc)]+=1
                if kind=='reader'and pc==0x34a2:self.put('ax',self.next_allocation&65535);self.put('dx',self.next_allocation>>16)
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
        m.write(0x4000,(ptr(n)&65535),4,c['opcode']if c['opcode']in(31,42,45)else 9)
        m.write(0x4000,(ptr(n)&65535)+0x34,4,0xffffffff)
    return m,links
def trace_for(original,body,seed):
    m=Machine();m.mem=original.mem.copy();position=0;trace=[];actions=[]
    while position is not None:
        assert len(trace)<=len(body)and 0<=position<len(body);trace.append(position);c=body[position]
        m.stack(6,4,ptr(position));m.stack(-0xa,2,0);m.put('si',1);m.write(0x2000,0xfce,4,0)
        if c['opcode']==31:
            low,high,comparison=c['args'][2:5]
            result=(seed==low)if comparison==0 else(seed<low)if comparison==1 else(seed>low)if comparison==2 else low<=seed<=high
            m.put('si',int(result));m.write(0x2000,0x6a7,2,int(result))
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
    return h,len(trace),len(actions)
inventory=json.loads(a.inventory.read_text());assert inventory['status']=='ORIGINAL_HYP_SYNTACTIC_BRANCH_INVENTORY_ONLY'
records=[];fixtures=bytearray(b'CBLK0001');summary=[];case_count=0
for scene in inventory['scenes']:
    for ordinal,script in enumerate(scene['scripts']):
        body=[inventory['commands'][i]for i in script['command_indices']]
        if not body:continue
        machine,links=links_for(body)
        seeds={-2147483648,-1,0,1,2147483647}
        for c in body:
            if c['opcode']==31:
                for boundary in c['args'][2:4]:
                    seeds.update(v for v in(boundary-1,boundary,boundary+1)if -2147483648<=v<=2147483647)
        rows=[(seed,*trace_for(machine,body,seed))for seed in sorted(seeds)];case_count+=len(rows)
        records.append((scene['scene'],ordinal,body,rows));summary.append(dict(scene=scene['scene'],trigger=script['trigger'],commands=len(body),cases=len(rows),links=links))
fixtures.extend(struct.pack('<I',len(records)))
for scene,ordinal,body,rows in records:
    fixtures.extend(struct.pack('<4I',scene,ordinal,len(body),len(rows)))
    for n,c in enumerate(body):
        opcode=c['opcode']if c['opcode']in(31,42,45)else 9;args=c['args']if opcode==31 else[n+1]if opcode==9 else[]
        fixtures.extend(struct.pack('<II',opcode,len(args)))
        for v in args:assert isinstance(v,int);fixtures.extend(struct.pack('<i',v))
    for seed,h,executed,actions in rows:fixtures.extend(struct.pack('<iIII',seed,h,executed,actions))
a.out.mkdir(exist_ok=False,parents=True);(a.out/'control-fixture.bin').write_bytes(fixtures)
proof=dict(status='ORIGINAL_WIN16_LINK_AND_CONTROL_REPLAY_FIXTURE_READY',created_at=datetime.now(timezone.utc).isoformat(),original_exe_sha256=sha(exe),inventory_sha256=sha(a.inventory.read_bytes()),author_sha256=sha(Path(__file__).read_bytes()),capstone_version=capstone.__version__,fixture_sha256=sha(fixtures),nonempty_scripts=len(records),control_cases=case_count,original_commands=sum(len(r[2])for r in records),condition_tests=inventory['summary']['condition_tests'],reader_link_model_matches=True,executed_instruction_steps=sum(counts.values()),instruction_sites=len(counts),modeled_calls=[dict(kind=k,address=hex(p),count=n)for(k,p),n in sorted(calls.items())],reader_ranges=[['9:3289','9:3295'],['9:3337','9:334b'],['9:334e','9:3357'],['9:335d','9:3366'],['9:3436','9:34fe'],['9:3507','9:3521']],execute_ranges=[['15:0e81','15:0e99'],['15:1636','15:1799']],scripts=summary,limits=['Original Win16program not run; this is bounded instruction interpretation','Resource operand-copy calls omitted after independent exact-byte inventory verification','Allocator returns deterministic distinct modeled far pointers; clock API returns0','Comparison predicates supplied from uniform controlled values using the declared comparison policy; original predicate machine body is not replayed','Noncontrol commands replaced by sound-action trace markers with no sound handler; original gameplay effects are not executed','All command delays normalized to-1 for topology only; no original timer fidelity claim','Uniform threshold cases are not exhaustive real gameplay states and do not close A03'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Original bounded link/control fixture ready:',len(records),'scripts,',case_count,'controlled cases,',sum(counts.values()),'original instruction steps')
