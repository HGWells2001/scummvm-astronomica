"""Replay original P512 validation including the state seen at voice dispatch."""
from pathlib import Path
import hashlib,itertools,json,struct
w=Path('work/fresh-20260913').resolve();template=Path(__file__).with_name('probe_original_scene_scalars_nov7.py')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pin=json.loads((w/'original-scene-scalars-nov7/proof.json').read_text());assert digest(template)==pin['author_sha256']
prefix=template.read_text().split('inventory=json.loads(a.inventory.read_text());',1)[0]
prefix=prefix.replace('else 200)and pc in ins','else 2000)and pc in ins')
prefix=prefix.replace("                if kind=='range-helper'", """                if kind=='weather':
                    target=relocations[pc+1]
                    if pc==0x52bc:
                        assert target==(18,0x18ba)
                        self.run(empty,0x18c4,0x18c6,'empty-helper')
                    else:
                        assert target==(9,0x3b07)
                        sound=self.read(self.get('ss'),self.get('sp'),2);assert sound in(10,11,12)
                        self.voices.append((sound,self.read(0x4000,0xd40c,4)))
                elif kind=='range-helper'""")
exec(compile(prefix,str(template),'exec'),globals())
weather={i.address:i for i in md.disasm(exe[base(4)+0x52bc:base(4)+0x5634],0x52bc)}
empty={i.address:i for i in md.disasm(exe[base(18)+0x18c4:base(18)+0x18c6],0x18c4)}
assert [(i.mnemonic,i.op_str)for i in empty.values()]==[('jmp','0x18c6')]
relocations={};length,flags=struct.unpack_from('<HH',exe,table+3*8+2);at=base(4)+(length or 65536)
for i in range(struct.unpack_from('<H',exe,at)[0]):
    kind,flag,offset,t1,t2=struct.unpack_from('<BB3H',exe,at+2+i*8);seen=set()
    while offset!=65535:
        assert offset not in seen;seen.add(offset)
        if kind==3 and flag&3==0:relocations[offset]=(t1,t2)
        if flag&4:break
        offset=struct.unpack_from('<H',exe,base(4)+offset)[0]
inventory=json.loads(a.inventory.read_text());scene=next(s for s in inventory['scenes']if s['scene']==512)
data=(a.root/scene['path']).read_bytes();assert sha(data)==scene['sha256']
resource_calls=[c for c in inventory['commands']if c['scene']==512 and c['opcode']==23 and c['args']==[24,0,0,0,0,0]]
assert resource_calls
for c in resource_calls:assert struct.unpack_from('<7i',data,c['file_offset'])==(23,24,0,0,0,0,0)
inputs={(s,*v)for s in range(1,7)for v in itertools.product(range(16),repeat=3)}
edges=(-2147483648,-1,0,1,7,8,9,14,15,16,2147483647)
inputs.update((s,*v)for s in range(1,7)for v in itertools.product(edges,repeat=3))
inputs.update((s,*v)for s in(-2147483648,-1,0,7,2147483647)for v in itertools.product((0,8,9,15),repeat=3))
records=[]
for scenario,a_,b_,c_ in sorted(inputs):
    for initial in(0,1):
        m=Machine();m.voices=[];m.write(0x2000,0xc88,4,0x4000d000)
        for ident,value in ((0,a_),(1,b_),(2,c_),(4,scenario),(5,initial)):m.write(0x4000,0xd3f8+4*ident,4,value)
        for off in range(0x6d60,0x6d84):m.write(0x5000,off,1,exe[base(4)+off])
        m.run(weather,0x52bc,0x5632,'weather');assert len(m.voices)<=1
        final=m.read(0x4000,0xd40c,4);sound,old=m.voices[0]if m.voices else(0xffffffff,0)
        records.append((scenario,a_,b_,c_,initial,final,sound,old))
fixture=bytearray(b'WFXO0001')+struct.pack('<I',len(records))
for row in records:fixture.extend(struct.pack('<8I',*(v&0xffffffff for v in row)))
a.out.mkdir(exist_ok=False);(a.out/'fixture.bin').write_bytes(fixture)
proof=dict(status='ORIGINAL_WEATHER_VOICE_ORDER_INSTRUCTION_FIXTURE_READY',author_sha256=digest(Path(__file__)),template_sha256=digest(template),original_exe_sha256=sha(exe),original_p512_sha256=sha(data),fixture_sha256=sha(fixture),cases=len(records),distinct_input_settings=len(inputs),original_ui_domain_included=True,result_initial_values=[0,1],signed_extremes_included=True,instruction_steps=sum(counts.values()),voice_cases=sum(r[6]!=0xffffffff for r in records),limits=['Original mode0 validator and empty in_custom helper body; original voice call reduced to sound ID and result snapshot','Other media operations and OS playback not executed; no original Windows run','Controlled initial result/settings include values outside ordinary UI; natural play reachability not claimed'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Original weather order fixture:',len(records),'cases')
