"""Audio routing plus full presentation, save, movie and WASAPI regressions."""
from pathlib import Path
import subprocess,sys
base=Path('work/fresh-20260913')
for name in ('check_audio_channels.py','check_presentation_regressions.py'):
 print('Starting '+name,flush=True)
 p=subprocess.run([sys.executable,str(base/name)],capture_output=True,text=True)
 print(p.stdout[-4500:]+p.stderr[-1000:],flush=True)
 assert p.returncode==0,name
print('Audio channels and full regression suite PASS',flush=True)
