"""Ensure the native original-instruction comparison detects independent corruptions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,struct,subprocess
w=Path(__file__).resolve().parent;out=w/'weather-order-negative-nov10';out.mkdir(exist_ok=False)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(w/'weather-order-fixed-native-nov10/proof.json');fixture=w/'original-weather-order-nov10/fixture.bin';exe=w/'weather-order-fixed-native-nov10/scummvm.exe'
assert p['status']=='ORIGINAL_WEATHER_VOICE_ORDER_REAL_NATIVE_PASS'and sha(fixture)==p['fixture_sha256']and sha(exe)==p['probe_exe_sha256']
data=fixture.read_bytes();voice=None
for at in range(12,len(data),32):
 if struct.unpack_from('<8I',data,at)==(1,0,0,0,1,0,10,1):voice=at;break
assert voice is not None
results=[]
for label,offset,expected,marker in [('final-result',12+20,7,'FAIL weather final state'),('voice-prior-result',voice+28,8,'FAIL weather voice order'),('selected-sound',voice+24,4,'FAIL weather pure answer')]:
 broken=bytearray(data);v=struct.unpack_from('<I',broken,offset)[0];struct.pack_into('<I',broken,offset,v^1);path=out/(label+'.bin');path.write_bytes(broken)
 run=subprocess.run([str(exe),str(path)],cwd=w,capture_output=True,text=True,timeout=60);log=out/(label+'.log');log.write_text(run.stdout+run.stderr)
 assert run.returncode==expected and marker in run.stdout+run.stderr,(label,run.returncode,run.stdout,run.stderr)
 results.append(dict(label=label,byte_offset=offset,exit_code=run.returncode,native_log_sha256=sha(log)))
assert sha(exe)==p['probe_exe_sha256']and sha(fixture)==p['fixture_sha256']
j=dict(status='WEATHER_ORDER_NATIVE_NEGATIVE_CONTROLS_PASS',completed_at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),positive_proof_sha256=sha(w/'weather-order-fixed-native-nov10/proof.json'),fixture_sha256=sha(fixture),probe_exe_sha256=sha(exe),independent_expected_corruptions_rejected=len(results),results=results,main_unchanged=True)
(out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print('Weather native negative controls PASS:',len(results),'distinct refusals')
