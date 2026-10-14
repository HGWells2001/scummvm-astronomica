import subprocess,sys
for name in ("build.py","check_logo.py","check_postcredits.py","check_endings.py"):
 r=subprocess.run([sys.executable,"work/fresh-20260913/"+name])
 if r.returncode:sys.exit(r.returncode)
