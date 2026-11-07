"""Measure reached original condition outcomes in the already-accepted scalar matrix.

Every replay result is rechecked against the accepted fixture. Other game effects
remain markers. The local per-command report is not a whole-game coverage claim.
"""
from pathlib import Path
import collections,hashlib,json,struct
template=Path(__file__).with_name('probe_original_scene_scalars_nov7.py')
w=Path('work/fresh-20260913').resolve()
reference=json.loads((w/'original-scene-scalars-nov7/proof.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(template)==reference['author_sha256']
prefix=template.read_text().split('inventory=json.loads(a.inventory.read_text());',1)
assert len(prefix)==2
exec(compile(prefix[0],str(template),'exec'),globals())
inventory=json.loads(a.inventory.read_text())
assert digest(a.inventory)==reference['inventory_sha256']
originals={}
for scene in inventory['scenes']:
    for ordinal,script in enumerate(scene['scripts']):
        body=[inventory['commands'][i]for i in script['command_indices']]
        if body:originals[scene['scene'],ordinal]=body
visits=collections.Counter();outcomes=collections.defaultdict(collections.Counter);context={}
original_run=Machine.run
def tracked(self,ins,start,stop,kind):
    if kind=='execute'and start==0x1636:
        i=index(self.stack(6,4));key=(context['scene'],context['ordinal'],i)
        visits[key]+=1
        if context['body'][i]['opcode']==31:outcomes[key][bool(self.read(0x2000,0x6a7,2))]+=1
    return original_run(self,ins,start,stop,kind)
Machine.run=tracked
path=w/'original-scene-scalars-nov7/control-fixture.bin'
assert digest(path)==reference['fixture_sha256']
data=path.read_bytes();assert data[:8]==b'CBLK0008'
pos=12;cases=0;sequences=0
retained={31,32,33,39,40,42,45,46}
for _ in range(struct.unpack_from('<I',data,8)[0]):
    scene,ordinal,length,count=struct.unpack_from('<4I',data,pos);pos+=16
    widths=list(struct.unpack_from('<200i',data,pos));pos+=800
    commands=[]
    for i in range(length):
        op,n=struct.unpack_from('<2I',data,pos);pos+=8
        args=list(struct.unpack_from('<'+'i'*n,data,pos));pos+=4*n;commands.append((op,args))
    body=originals.get((scene,ordinal))
    if body is None:
        assert scene==10000;pos+=828*count;continue
    assert len(body)==length
    for i,c in enumerate(body):
        expected=(c['opcode'],c['args'])if c['opcode']in retained else(9,[i+1])
        assert commands[i]==expected
    original,links=links_for(body);context.update(scene=scene,ordinal=ordinal,body=body)
    for _ in range(count):
        seed,mode,h,executed,actions,state=struct.unpack_from('<i5I',data,pos)
        values=list(struct.unpack_from('<200I',data,pos+24));next_draw=struct.unpack_from('<I',data,pos+824)[0];pos+=828
        assert trace_for(original,body,seed,mode,widths)==(h,executed,actions,state,values,next_draw)
        cases+=1
    sequences+=1
assert pos==len(data)and sequences==936
rows=[];categories=collections.Counter();semantic_visited=collections.Counter()
for (scene,ordinal),body in originals.items():
    for i,c in enumerate(body):
        key=(scene,ordinal,i)
        if visits[key]and c['opcode']in retained:semantic_visited[c['opcode']]+=1
        if c['opcode']!=31:continue
        observed=outcomes[key]
        category='both'if observed[False]and observed[True]else'true_only'if observed[True]else'false_only'if observed[False]else'unvisited'
        categories[category]+=1
        rows.append(dict(scene=scene,script=ordinal,command=i,category=category,true_visits=observed[True],false_visits=observed[False]))
assert len(rows)==1392
a.out.mkdir(exist_ok=False,parents=True)
local=a.out/'condition-outcomes-local.json';local.write_text(json.dumps(rows,indent=2)+'\n')
proof=dict(status='ACCEPTED_SCALAR_MATRIX_ORIGINAL_BRANCH_MEASUREMENT_PASS',
           template_sha256=digest(template),author_sha256=digest(Path(__file__)),
           accepted_fixture_sha256=digest(path),local_detail_sha256=digest(local),
           original_sequences=sequences,original_controlled_cases=cases,condition_positions=len(rows),
           categories=dict(categories),visited_retained_positions_by_opcode=dict(semantic_visited),
           limits=['Only coverage of the accepted reduced scalar matrix; effects and gameplay reachability remain outside scope',
                   'Unvisited or one-sided conditions are follow-up targets, not proven engine defects or unreachable game branches',
                   'Per-command original detail stays local; no whole-game completion percentage'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Original scalar branch measurement PASS:',cases,'cases,',dict(categories))
