"""Replay original custom25 scene dispatch and completion side effects.

The OS voice call is an observation boundary, not Windows execution. Its
globals/counter snapshot is compared with the actual engine's blocking voice.
"""
from pathlib import Path
import hashlib,json,struct
template=Path(__file__).with_name('probe_original_scene_scalars_nov7.py')
w=Path('work/fresh-20260913').resolve();pin=json.loads((w/'original-scene-scalars-nov7/proof.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert digest(template)==pin['author_sha256']
prefix=template.read_text().split('inventory=json.loads(a.inventory.read_text());',1)[0]
prefix=prefix.replace("else 200)and pc in ins","else 2000)and pc in ins")
prefix=prefix.replace("                if kind=='range-helper'", """                if kind=='custom25':
                    target=relocations[4,pc+1]
                    if target==(3,0x39ae):self.run(success_body,0x39b8,0x39c6,'success-helper')
                    else:
                        assert target==play_sound,target
                        voice(self)
                elif kind=='success-helper':
                    assert relocations[3,pc+1]==play_sound
                    voice(self)
                elif kind=='range-helper'""")
exec(compile(prefix,str(template),'exec'),globals())
names=['']+[s.decode('latin1')for s in exe[0x61ff5:-8].split(b'\0')];sound_symbols=[]
for i in range(3686):
    name,typ,offset,segment,flags=struct.unpack_from('<IIHHH',exe,0x24690+14*i)
    if names[name]=='_playSound'and flags==24:sound_symbols.append((segment,offset))
assert len(sound_symbols)==1;play_sound=sound_symbols[0]
custom={i.address:i for i in md.disasm(exe[base(4)+0x56b5:base(4)+0x5a8e],0x56b5)}
success_body={i.address:i for i in md.disasm(exe[base(3)+0x39b8:base(3)+0x39c6],0x39b8)}
relocations={}
for segment in (3,4):
    length,flags=struct.unpack_from('<HH',exe,table+(segment-1)*8+2);assert flags&0x100
    at=base(segment)+(length or 65536)
    for i in range(struct.unpack_from('<H',exe,at)[0]):
        kind,flag,offset,t1,t2=struct.unpack_from('<BB3H',exe,at+2+i*8);seen=set()
        while offset!=65535:
            assert offset not in seen;seen.add(offset)
            if kind==3 and flag&3==0:relocations[segment,offset]=(t1,t2)
            if flag&4:break
            offset=struct.unpack_from('<H',exe,base(segment)+offset)[0]

def values(m):return [m.read(0x4000,0xc00a+i*4,4)for i in range(100)]
def fnv(words):
    h=2166136261
    for v in words:h=((h^v)*16777619)&0xffffffff
    return h
def voice(m):
    sound=m.read(m.get('ss'),m.get('sp'),2);assert sound==912
    m.voices.append(dict(sound=sound,counter=m.read(0x2000,0x153,4),globals_hash=fnv(values(m))))

inventory=json.loads(a.inventory.read_text());assert digest(a.inventory)==pin['inventory_sha256']
invocations={}
for c in inventory['commands']:
    if c['opcode']==23 and c['args']==[25,0,0,0,0,0]:invocations.setdefault(c['scene'],c)
scenes={s['scene']:s for s in inventory['scenes']};records=[];details=[]
for scene,command in sorted(invocations.items()):
    asset=a.root/scenes[scene]['path'];data=asset.read_bytes();assert sha(data)==scenes[scene]['sha256']
    assert struct.unpack_from('<7i',data,command['file_offset'])==(23,25,0,0,0,0,0)
    # Derive a tested flag from the original first comparison, never engine mapping.
    scene_ids=struct.unpack_from('<34i',exe,base(4)+0x6c94);targets=struct.unpack_from('<34H',exe,base(4)+0x6d1c)
    target=dict(zip(scene_ids,targets)).get(scene);flag=None
    if target is not None:
        first=list(md.disasm(exe[base(4)+target:base(4)+target+24],target))
        if len(first)>1 and first[1].mnemonic=='cmp':
            operand=first[1].operands[0];assert operand.type==X86_OP_MEM and operand.mem.disp>=10
            flag=(operand.mem.disp-10)//4;assert 0<=flag<100 and 10+4*flag==operand.mem.disp
    for seed in (-2147483648,-2,0,1,2,2147483647):
        for counter in (0,0xffffffff):
            initial=[(0x7f4a7c15+i*0x9e3779b9+seed)&0xffffffff for i in range(100)]
            if flag is not None:initial[flag]=seed&0xffffffff
            m=Machine();m.voices=[];m.stack(-0x8e,4,scene);m.write(0x2000,0xc8c,4,scene)
            m.write(0x2000,0x7a8,4,0x4000c000);m.write(0x2000,0x153,4,counter)
            for i,v in enumerate(initial):m.write(0x4000,0xc00a+i*4,4,v)
            for off in range(0x6c94,0x6d60):m.write(0x5000,off,1,exe[base(4)+off])
            results=[]
            for repeat in range(2):
                old=len(m.voices);m.run(custom,0x56b5,0x5a8e,'custom25');new=m.voices[old:];assert len(new)<=1
                results.append(dict(counter=m.read(0x2000,0x153,4),voices=len(new),voice_counter=new[0]['counter']if new else 0,voice_hash=new[0]['globals_hash']if new else 0,globals=values(m)))
            records.append((scene,command['file_offset'],counter,initial,results))
            details.append(dict(scene=scene,seed=seed,initial_counter=counter,flag=flag,results=results))
fixture=bytearray(b'SCFX0001')+struct.pack('<I',len(records))
for scene,offset,counter,initial,results in records:
    fixture.extend(struct.pack('<4I',scene,offset,counter,len(results)));fixture.extend(struct.pack('<100I',*initial))
    for result in results:
        fixture.extend(struct.pack('<4I',result['counter'],result['voices'],result['voice_counter'],result['voice_hash']));fixture.extend(struct.pack('<100I',*result['globals']))
a.out.mkdir(exist_ok=False);(a.out/'fixture.bin').write_bytes(fixture);(a.out/'effects-local.json').write_text(json.dumps(details,indent=2)+'\n')
proof=dict(status='ORIGINAL_COMPLETION_EFFECTS_INSTRUCTION_FIXTURE_READY',original_exe_sha256=sha(exe),author_sha256=digest(Path(__file__)),template_sha256=digest(template),inventory_sha256=digest(a.inventory),fixture_sha256=sha(fixture),cases=len(records),invocations=sum(len(r[-1])for r in records),scenes=sorted(invocations),instruction_steps=sum(counts.values()),voice_calls=sum(x['voices']for r in records for x in r[-1]),limits=['Original custom25 dispatcher and handler bodies, including original completion helper; OS voice call modeled as an observation boundary','Counter/scalar owners are modeled; no original Windows execution','Resource command operands byte-verified; isolated kernel calls normalize command delay to minus1','Controlled globals and counter limits, not natural reachable histories or a whole-game claim'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Original completion effects fixture:',len(records),'cases,',proof['voice_calls'],'voices')
