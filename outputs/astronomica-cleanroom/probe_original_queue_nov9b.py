"""Replay original queue/copy/wrapper/control bodies, with reduced non-scalar effects.

This is original-instruction test evidence, not original Windows execution.
The accepted cleanroom interpreter is extended only for bounded queue API calls.
"""
from pathlib import Path
import hashlib,json,struct
template=Path(__file__).with_name('probe_original_scene_scalars_nov7.py')
pin=json.loads(Path('work/fresh-20260913/original-scene-scalars-nov7/proof.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(template)==pin['author_sha256']
prefix=template.read_text().split('inventory=json.loads(a.inventory.read_text());',1)[0]
prefix=prefix.replace('(0x2000,0x3000,0x4000,0x5000)','(0x2000,0x3000,0x4000,0x5000,0x6000)')
prefix=prefix.replace("else 200)and pc in ins","else 2000)and pc in ins")
prefix=prefix.replace("elif op=='inc':self.assign", "elif op=='dec':self.assign(i,o[0],self.value(i,o[0])-1)\n            elif op=='inc':self.assign")
prefix=prefix.replace("                if kind in('rng','rng-next-draw')", """                if kind=='pend'and pc==0x19c3:
                    source=self.stack(6,4);dest=self.stack(-6,4);old_sp=self.get('sp')
                    frame(self,0x6000,{6:source,10:dest},lambda:self.run(execute,0x1a1b,0x1b24,'copy'))
                    self.put('sp',old_sp+2)
                elif kind=='execute'and pc in(0x119f,0x16ab,0x1705,0x178f):
                    source=self.read(self.get('ss'),self.get('sp')+2,4);old_sp=self.get('sp');pend(self,source);self.put('sp',old_sp+2)
                elif kind=='wrapper'and pc==0x42:
                    source=self.stack(6,4);old_sp=self.get('sp');execute_one(self,source);self.put('sp',old_sp+2)
                elif kind=='pending'and pc==0x1c05:
                    source=self.stack(-0xe,4);old_sp=self.get('sp');do_command(self,source);self.put('sp',old_sp+2)
                elif kind in('rng','rng-next-draw')""")
prefix=prefix.replace("                if kind=='range-helper'", """                if kind=='pending'and pc==0x1b48:self.put('ax',self.clock&65535);self.put('dx',self.clock>>16)
                elif kind=='pending'and pc==0x1c43:
                    source=self.stack(-0xe,4);assert source not in self.freed;self.freed.add(source)
                elif kind=='range-helper'""")
prefix=prefix.replace("self.put('ax',0);self.put('dx',0)","self.put('ax',self.clock&65535);self.put('dx',self.clock>>16)")
exec(compile(prefix,str(template),'exec'),globals())
execute.update({i.address:i for lo,hi in((0x25,0x60),(0x199a,0x1c6d))for i in md.disasm(exe[base(15)+lo:base(15)+hi],lo)})

def frame(m,bp,arguments,body):
    saved={r:m.get(r)for r in('bp','sp','si','di')}
    m.put('bp',bp);m.put('sp',bp-0x142)
    for offset,value in arguments.items():m.stack(offset,4,value)
    body()
    for r,v in saved.items():m.put(r,v)

def pend(m,source):
    assert source and source not in m.freed
    dest=0x60000010+m.allocations*0x48;m.allocations+=1;assert m.allocations<850
    m.tags[dest]=m.tags[source]
    def body():
        m.stack(-6,4,dest);m.run(execute,0x19b5,0x1a08,'pend')
    frame(m,0x7000,{6:source},body)

def execute_one(m,source):
    assert source not in m.freed
    opcode=m.read(source>>16,source&65535,4)
    def body():
        m.put('si',1);m.stack(-0xa,2,0);m.executed+=1
        if opcode==31:m.run(execute,0xc70,0x1636,'predicate')
        elif opcode==32:m.run(execute,0xe99,0x1636,'assignment')
        elif opcode==46:m.run(execute,0x159b,0x1636,'addition')
        elif opcode==41:m.run(execute,0x118b,0x1636,'execute')
        elif opcode==42:m.run(execute,0xe81,0x1636,'execute')
        elif opcode==45:m.run(execute,0xe8a,0x1636,'execute')
        else:
            assert opcode==9;m.actions.append(m.tags[source])
        m.run(execute,0x1636,0x1799,'execute')
    frame(m,0x8000,{6:source},body)

def do_command(m,source):
    def body():
        m.put('si',1);m.run(execute,0x33,0x5b,'wrapper')
    frame(m,0x5000,{6:source},body)

def setup(programs,root,seed,loaded):
    m=Machine();m.clock=loaded;m.allocations=0;m.freed=set();m.tags={};m.executed=0;m.actions=[]
    for off in range(0x1832,0x187a):m.write(0x5000,off,1,exe[base(15)+off])
    # Assignment/addition dispatch tables also come from original CS bytes.
    for off in range(0x17a2,0x1832):m.write(0x5000,off,1,exe[base(15)+off])
    m.write(0x2000,0x7a8,4,0x4000c000);m.write(0x2000,0xc88,4,0x4000d000)
    for scope,offset in ((0,0xc00a),(1,0xd3f8)):
        for ident in range(100):m.write(0x4000,offset+ident*4,4,seed)
    roots=[];used=0
    for script in programs+[root]:
        assert script
        original,links=links_for(script);start=0x40000010+used*0x48;roots.append(start)
        for i,c in enumerate(script):
            dest=start+i*0x48;assert(dest&65535)+0x48<0xc000
            for j in range(0x48):m.write(0x4000,(dest&65535)+j,1,original.read(0x4000,(ptr(i)&65535)+j,1))
            for field in(0x38,0x40):
                p=original.read(0x4000,(ptr(i)&65535)+field,4)
                m.write(0x4000,(dest&65535)+field,4,start+(p-ptr(0))if p else 0)
            m.write(0x4000,dest&65535,4,c['opcode']);m.write(0x4000,(dest&65535)+0x30,4,loaded)
            m.write(0x4000,(dest&65535)+0x34,4,c['delay'])
            for j,value in enumerate(c['args']):m.write(0x4000,(dest&65535)+4+j*4,4,value)
            m.tags[dest]=c['tag']
        used+=len(script)
    for i,p in enumerate(roots[:-1]):m.write(0x2000,0xcd8+i*4,4,p)
    pend(m,roots[-1]);return m

def tick(m,now):
    m.clock=now;m.actions=[]
    frame(m,0x9000,{6:0},lambda:m.run(execute,0x1b38,0x1c6d,'pending'))
    h=2166136261
    for v in m.actions:h=((h^v)*16777619)&0xffffffff
    values=[m.read(0x4000,offset+i*4,4)for offset in(0xc00a,0xd3f8)for i in range(100)]
    return m.executed,m.read(0x2000,0x6a9,4),len(m.actions),h,values

inventory=json.loads(a.inventory.read_text());assert digest(a.inventory)==pin['inventory_sha256']
retained={31,32,41,42,45,46};records=[]
for scene in inventory['scenes']:
    if scene['scene']not in(423,429,510,515,536):continue
    next_tag=[1]
    def reduce(script):
        result=[]
        for index_ in script['command_indices']:
            c=inventory['commands'][index_];op=c['opcode']if c['opcode']in retained else 9
            tag=next_tag[0];next_tag[0]+=1;assert tag<=923
            result.append(dict(opcode=op,args=c['args']if op in retained else[tag],delay=c['delay_ms'],tag=tag))
        return result
    programs=[reduce(s)for s in scene['scripts']if s['trigger'].startswith('entry/')]
    for ordinal in({423:[0],429:[0],510:[0],515:[14,19],536:[14,19]}[scene['scene']]):
        root=reduce(scene['scripts'][ordinal])
        for seed in(-1,0,1,2,3,4,5,6,7,10):
            loaded=100;ticks=[100,101,109,110,200,300,600,1000,3600,10000,169100,500000]
            m=setup(programs,root,seed,loaded);rows=[(now,*tick(m,now))for now in ticks]
            records.append((scene['scene'],ordinal,seed,loaded,programs,root,rows))
fixture=bytearray(b'QSCN0001')+struct.pack('<I',len(records))
for scene,ordinal,seed,loaded,programs,root,rows in records:
    fixture.extend(struct.pack('<IIiIII',scene,ordinal,seed,loaded,len(programs),len(rows)))
    for script in programs+[root]:
        fixture.extend(struct.pack('<I',len(script)))
        for c in script:
            fixture.extend(struct.pack('<IiI',c['opcode'],c['delay'],len(c['args'])))
            fixture.extend(struct.pack('<'+'i'*len(c['args']),*c['args']))
    for now,executed,pending,actions,h,values in rows:
        fixture.extend(struct.pack('<5I',now,executed,pending,actions,h));fixture.extend(struct.pack('<200I',*values))
a.out.mkdir(exist_ok=False,parents=True);(a.out/'fixture.bin').write_bytes(fixture)
proof=dict(status='ORIGINAL_QUEUE_INSTRUCTION_FIXTURE_READY',original_exe_sha256=sha(exe),
           template_sha256=digest(template),author_sha256=digest(Path(__file__)),fixture_sha256=sha(fixture),
           cases=len(records),ticks=sum(len(r[-1])for r in records),instruction_steps=sum(counts.values()),
           limits=['Original queue/copy/control/wrapper bodies replayed; allocator,free and clock modeled',
                   'Only31/32/41/42/45/46retain effects; others are timed trace markers',
                   'No original Windows execution or complete scene gameplay claim'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Queue fixture ready:',proof['cases'],'cases,',proof['ticks'],'ticks')

