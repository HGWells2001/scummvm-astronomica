"""Ensure the real native regression rejects scalar, trace and RNG mismatches."""
from pathlib import Path
import hashlib, json, struct, subprocess
w=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stage=w/'original-scene-scalars-native-nov7'
source=w/'original-scene-scalars-nov7/control-fixture.bin'
proof=json.loads((stage/'proof.json').read_text())
assert proof['status']=='ORIGINAL_SCENE_METADATA_SCALAR_REAL_NATIVE_RUNNER_PASS'
assert sha(stage/'scummvm.exe')==proof['probe_exe_sha256']
assert sha(source)==proof['fixture_sha256']
b=source.read_bytes();assert b[:8]==b'CBLK0008'
scene,ordinal,length,count=struct.unpack_from('<4I',b,12)
pos=828
for i in range(length):
    opcode,args=struct.unpack_from('<2I',b,pos);pos+=8+4*args
row=b[pos:pos+828];assert len(row)==828
first=b[:8]+struct.pack('<5I',1,scene,ordinal,length,1)+b[28:pos]+row
row_offset=28+(pos-28)
out=w/'scene-scalar-negative-controls-nov7';out.mkdir(exist_ok=False)
receipts=[]
for label,offset,code,message in (
    ('scalar',24,10,'FAIL exact scalar'),
    ('trace',8,6,'FAIL native control'),
    ('rng',824,11,'FAIL rng next draw')
):
    changed=bytearray(first);changed[row_offset+offset]^=1
    fixture=out/(label+'.bin');fixture.write_bytes(changed)
    result=subprocess.run([str(stage/'scummvm.exe'),str(fixture)],cwd=stage,capture_output=True,text=True,timeout=30)
    log=out/(label+'.log');log.write_text(result.stdout+result.stderr)
    assert result.returncode==code and message in log.read_text(),(label,result.returncode,log.read_text())
    receipts.append(dict(label=label,exit_code=code,fixture_sha256=sha(fixture),log_sha256=sha(log)))
(out/'proof.json').write_text(json.dumps(dict(
    status='NATIVE_SCALAR_TRACE_RNG_NEGATIVE_CONTROLS_PASS',
    probe_exe_sha256=sha(stage/'scummvm.exe'),positive_proof_sha256=sha(stage/'proof.json'),
    single_case_only=True,cases=receipts,
    limits=['Deliberate expectation corruptions are test failures as required; no corrupt game save or original file is loaded']
),indent=2)+'\n')
print('Negative controls PASS:exact scalar,action trace,next RNG mismatch all rejected')
