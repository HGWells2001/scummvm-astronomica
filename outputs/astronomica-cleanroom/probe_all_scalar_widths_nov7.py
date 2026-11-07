"""Bounded synthetic free-bit cases for all admitted widths, using the accepted oracle.

The owned template defines the original-instruction interpreter. Only its definitions
are loaded; its inventory/fixture emitter is not executed. Original files stay read-only.
"""
from pathlib import Path
import hashlib, json, re, struct, subprocess

template=Path(__file__).with_name('probe_original_scene_scalars_nov7.py')
workspace=Path('work/fresh-20260913').resolve()
reference=json.loads((workspace/'original-scene-scalars-nov7/proof.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
template_hash=digest(template)
assert template_hash==reference['author_sha256']
prefix=template.read_text().split('inventory=json.loads(a.inventory.read_text());',1)
assert len(prefix)==2
exec(compile(prefix[0],str(template),'exec'),globals())

records=[]
for width in range(1,32):
    mask=(1<<width)-1
    unsigned={0,1,0x80000000,0x7fffffff,0xffffffff,mask,mask^1,mask^(1<<(width-1)),mask|0x80000000}
    seeds=sorted(v-0x100000000 if v&0x80000000 else v for v in unsigned)
    for scope in range(2):
        for ident in (0,99):
            for same in (False,True):
                body=[dict(opcode=39,args=[scope,ident,scope if same else 1-scope,ident if same else 99-ident]),dict(opcode=9,args=[1])]
                original,links=links_for(body)
                widths=[width]*200
                rows=[(seed,mode,*trace_for(original,body,seed,mode,widths))for mode in (0,1)for seed in seeds]
                records.append((body,widths,rows))

fixture=bytearray(b'CBLK0008')+struct.pack('<I',len(records))
for ordinal,(body,widths,rows)in enumerate(records):
    fixture.extend(struct.pack('<4I',10001,ordinal,len(body),len(rows)))
    fixture.extend(struct.pack('<200i',*widths))
    for n,c in enumerate(body):
        args=c['args']if c['opcode']==39 else[n+1]
        fixture.extend(struct.pack('<II',c['opcode'],len(args)))
        fixture.extend(struct.pack('<'+'i'*len(args),*args))
    for seed,mode,h,executed,actions,state,values,next_draw in rows:
        fixture.extend(struct.pack('<iIIIII',seed,mode,h,executed,actions,state))
        fixture.extend(struct.pack('<200I',*values));fixture.extend(struct.pack('<I',next_draw))
a.out.mkdir(exist_ok=False,parents=True)
path=a.out/'all-widths.bin';path.write_bytes(fixture)
stage=workspace/'original-scene-scalars-native-nov7'
native=json.loads((stage/'proof.json').read_text())
assert native['status']=='ORIGINAL_SCENE_METADATA_SCALAR_REAL_NATIVE_RUNNER_PASS'
assert digest(stage/'scummvm.exe')==native['probe_exe_sha256']
result=subprocess.run([str(stage/'scummvm.exe'),str(path.resolve())],cwd=stage,capture_output=True,timeout=60)
(a.out/'native.log').write_bytes(result.stdout+result.stderr)
result.check_returncode()
match=re.search(rb'PASS \(scripts(\d+),cases(\d+),aggregate([0-9a-f]+);',result.stdout)
cases=sum(len(r[2])for r in records)
assert match and int(match[1])==len(records)and int(match[2])==cases
proof=dict(status='ALL_ADMITTED_SCALAR_WIDTHS_REAL_NATIVE_PASS',
           template_sha256=template_hash,author_sha256=digest(Path(__file__)),
           native_exe_sha256=digest(stage/'scummvm.exe'),fixture_sha256=digest(path),
           native_log_sha256=digest(a.out/'native.log'),widths=list(range(1,32)),
           synthetic_sequences=len(records),cases=cases,all_200_words_compared=True,
           next_rng_draw_compared=True,aggregate=match[3].decode(),
           original_instruction_steps=sum(counts.values()),
           limits=['Synthetic cases only; no original game script or scene acceptance claim',
                   'Same instruction replay and bounded modeled floating-helper assumptions as the accepted scene-metadata oracle',
                   'Masks cover zero, exhausted, edge free bits and sign bit; the complete2^31mask space is not enumerated'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('All admitted widths/native PASS:',len(records),'synthetic sequences,',cases,'cases')
