from pathlib import Path
import subprocess,sys
work=Path('work/fresh-20260913');root=Path('outputs/astronomica-cleanroom')
log=(work/'endings.log').read_text();assert 'endings interaction verification: PASS' in log and 'FAIL' not in log
for name in ('runtime_test.py','record_advice_checkpoint.py'):
 result=subprocess.run([sys.executable,str(work/name)])
 if result.returncode:
  (root/'RUN-IN-PROGRESS.md').write_text('Final verification/checkpoint failed at '+name+'. Inspect work/fresh-20260913 logs before further development.\n')
  sys.exit(result.returncode)
print('Final full suite and checkpoint PASS')
