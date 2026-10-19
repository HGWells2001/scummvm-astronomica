"""P528 v8 followed by prior saves, full-frame, audio and WASAPI suites."""
from pathlib import Path
import subprocess,sys
base=Path('work/fresh-20260913')
for name in ('check_p528_saves.py','check_audio_channel_regressions.py'):
 print('Starting '+name,flush=True)
 p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True)
 print(p.stdout[-4500:]+p.stderr[-1000:],flush=True)
 assert p.returncode==0,name
print('P528 v8 and full compatible regression suite PASS',flush=True)
