"""Deliberately break queue, individual scalar and RNG expectations independently."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,struct,subprocess
w=Path(__file__).resolve().parent;out=w/'scalar-queue-negative-controls-nov9';out.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
positive=read(w/'original-scalar-queue-native-nov9b/proof.json');exe=w/'original-scalar-queue-native-nov9b/scummvm.exe';fixture=w/'original-scalar-queue-nov9/fixture.bin'
assert positive['status']=='ORIGINAL_QUEUE_REAL_NATIVE_COMPARISON_PASS' and sha(exe)==positive['probe_exe_sha256'] and sha(fixture)==positive['fixture_sha256']
data=fixture.read_bytes();assert data[:8]==b'QSCN0003';pos=12
_,_,_,_,programs,steps,initial=struct.unpack_from('<7I',data,pos);pos+=28+800
assert steps and 1<=initial<=3
for n in range(programs+1):
 commands=struct.unpack_from('<I',data,pos)[0];pos+=4
 for _ in range(commands):
  op,delay,args=struct.unpack_from('<IiI',data,pos);pos+=12+4*args
first_tick=pos;results=[]
for label,offset,expected_code,marker in [('executed-count',first_tick+4,6,'FAIL queue '),('scalar-word',first_tick+20,7,'FAIL queue scalar '),('next-rng-draw',first_tick+820,8,'FAIL queue RNG ')]:
 broken=bytearray(data);v=struct.unpack_from('<I',broken,offset)[0];struct.pack_into('<I',broken,offset,v^1)
 path=out/(label+'.bin');path.write_bytes(broken)
 run=subprocess.run([str(exe),str(path)],capture_output=True,text=True,cwd=w,timeout=30)
 log=out/(label+'.log');log.write_text(run.stdout+run.stderr)
 assert run.returncode==expected_code and marker in run.stdout+run.stderr,(label,run.returncode,run.stdout,run.stderr)
 results.append(dict(label=label,byte_offset=offset,exit_code=run.returncode,native_log_sha256=sha(log),fixture_sha256=sha(path)))
assert sha(fixture)==positive['fixture_sha256'] and sha(exe)==positive['probe_exe_sha256']
j=dict(status='NATIVE_SCALAR_QUEUE_NEGATIVE_CONTROLS_PASS',completed_at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),positive_proof_sha256=sha(w/'original-scalar-queue-native-nov9b/proof.json'),positive_fixture_sha256=sha(fixture),probe_exe_sha256=sha(exe),independent_expected_corruptions_rejected=len(results),results=results,engine_runtime_changed=False)
(out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print('Native scalar/queue negative controls PASS:',len(results),'independent refusals')
