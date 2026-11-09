"""Verify original builder phase mask initialization and every serialized scalar writer."""
from pathlib import Path
import argparse,hashlib,json,struct,sys
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
here=Path(__file__).resolve().parent;inventory=json.loads(Path('work/fresh-20260913/original-branches-nov6/inventory.json').read_text())
rows=[]
for place,mask in ((515,24),(536,7)):
    scene=next(s for s in inventory['scenes']if s['scene']==place);path=a.root/scene['path'];data=path.read_bytes();assert sha(path)==scene['sha256']
    conditions=scene['conditions'];start=scene['parsed_bytes']-4-24*len(conditions)
    assert struct.unpack_from('<i',data,start)[0]==len(conditions)
    for i,row in enumerate(conditions):assert list(struct.unpack_from('<6i',data,start+4+i*24))==row
    assert next(c for c in conditions if c[:2]==[1,0])[2:4]==[5,mask]
    writers=[]
    for script in scene['scripts']:
        for index in script['command_indices']:
            c=inventory['commands'][index];op,args=c['opcode'],c['args']
            if op not in(23,32,33,39,40,46):continue
            assert struct.unpack_from('<i',data,c['file_offset'])[0]==op
            assert list(struct.unpack_from('<'+'i'*len(args),data,c['file_offset']+4))==args
            if op==23:assert args==[25,0,0,0,0,0]
            if op in(32,33,40,46)and args[:2]==[1,0]:
                assert op==32 and args==[1,0,7];writers.append(dict(opcode=op,operation='reset-to-original-reserved-mask'))
            if op==39:
                assert args==[1,0,1,1];writers.append(dict(opcode=op,operation='OR-selected-free-bit;store-1-based-index-in-local1'))
            if op in(32,33,40,46):assert args[:2]!=[1,1]
    # All 5-bit masks with the phase's reserved bits set stay within that phase.
    masks=[m for m in range(32)if(m&mask==mask)or(m&7==7)];selected=set()
    for m in masks:
        for bit in range(5):
            if not(m&(1<<bit)):
                assert(m|(1<<bit))in masks;selected.add(bit+1)
    assert selected==({1,2,3,4,5}if place==515 else{4,5})
    rows.append(dict(scene=place,original_hyp_sha256=sha(path),initial_scenario=next(c for c in conditions if c[:2]==[1,1])[3],initial_mask=mask,
                     reset_mask=7,closed_masks=masks,selected_indices=sorted(selected),
                     serialized_writers=writers,custom_commands=[[25,0,0,0,0,0]]))
exe=(a.root/'SETUP/ASTRO.EXE').read_bytes();assert hashlib.sha256(exe).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
ne=struct.unpack_from('<I',exe,60)[0];table=ne+struct.unpack_from('<H',exe,ne+0x22)[0];shift=struct.unpack_from('<H',exe,ne+0x32)[0]
base=lambda n:struct.unpack_from('<H',exe,table+(n-1)*8)[0]<<shift
dispatch=dict(zip(struct.unpack_from('<34i',exe,base(4)+0x6c94),struct.unpack_from('<34H',exe,base(4)+0x6c94+136)))
assert 515 not in dispatch and dispatch[536]==0x584c
sys.path.insert(0,str(Path('work/fresh-20260913/deps-verified').resolve()))
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
body=[(i.mnemonic,i.op_str)for i in Cs(CS_ARCH_X86,CS_MODE_16).disasm(exe[base(4)+0x584c:base(4)+0x586f],0x584c)]
assert body==[('les','bx, ptr [0x7a8]'),('cmp','dword ptr es:[bx + 0x86], 0'),('jne','0x585e'),('lcall','0, 0xffff'),('les','bx, ptr [0x7a8]'),('mov','dword ptr es:[bx + 0x86], 1'),('jmp','0x5a8e')]
assert not a.out.exists();a.out.write_text(json.dumps(dict(status='ORIGINAL_BUILDER_PHASE_MASK_CLOSURE_PASS',
    author_sha256=sha(Path(__file__)),original_exe_sha256=hashlib.sha256(exe).hexdigest(),scenes=rows,
    custom25_dispatch={515:'no handler',536:'global31 success handler'},
    limits=['Serialized scene scalar writers and original success dispatch verified; no original Windows execution',
            'Imported native states must separately enforce this normal-play invariant; this does not prove every branch unreachable']
),indent=2)+'\n')
print('Original builder phase masks PASS:P515 initial24/reset7/design1..5;P536 initial7/reset7/design4..5')
