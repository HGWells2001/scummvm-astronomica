"""Reuse the accepted console build orchestration with a new real-runner test."""
from pathlib import Path
w=Path(__file__).resolve().parent
t=(w/'run_original_scalar_queue_nov9b.py').read_text()
t=t[:t.index("with(out/'native.log')")]
t=t.replace("out=w/'original-scalar-queue-native-nov9b'","out=w/'weather-order-baseline-native-nov10'")
t=t.replace('original-scalar-queue-nov9','original-weather-order-nov10').replace('scalar_queue_probe_nov9.cpp','weather_order_probe_nov10.cpp')
t=t.replace("reference['status']=='ORIGINAL_QUEUE_INSTRUCTION_FIXTURE_READY'","reference['status']=='ORIGINAL_WEATHER_VOICE_ORDER_INSTRUCTION_FIXTURE_READY'")
t+='''with(out/'native.log').open('w')as log:result=subprocess.run([str(out/'scummvm.exe'),str(fixture)],env=env,cwd=w,stdout=log,stderr=subprocess.STDOUT,timeout=180)
text=(out/'native.log').read_text()
assert result.returncode==8 and 'FAIL weather voice order' in text,text
assert sha(fixture)==reference['fixture_sha256'] and sha(native_library)==library_pin and sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
proof=dict(status='ORIGINAL_WEATHER_VOICE_ORDER_BASELINE_COUNTEREXAMPLE_OBSERVED',completed_at=datetime.now(timezone.utc).isoformat(),oracle_proof_sha256=sha(w/'original-weather-order-nov10/proof.json'),probe_source_sha256=sha(source),probe_exe_sha256=sha(out/'scummvm.exe'),native_library_sha256=library_pin,fixture_sha256=sha(fixture),installed_main_exe_sha256=seal['exe_sha256'],native_log_sha256=sha(out/'native.log'),exit_code=result.returncode,counterexample=text.strip(),runtime_unchanged=True,limits=reference['limits'])
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\\n');print(text.strip())
'''
(w/'run_weather_order_baseline_nov10.py').write_text(t)
