import subprocess,os
from pathlib import Path
base=Path('work/fresh-20260913').resolve();build=base/'build';env={k.upper():v for k,v in os.environ.items()}
cmd=[r'C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe',str(build/'scummvm.sln'),'/p:Configuration=Release','/p:Platform=x64','/p:WindowsTargetPlatformVersion=10.0','/m:4','/verbosity:minimal','/nologo']
with (base/'build.log').open('w') as f:p=subprocess.run(cmd,cwd=build,env=env,stdout=f,stderr=subprocess.STDOUT)
print('exit',p.returncode);print((base/'build.log').read_text(errors='replace')[-7000:]);raise SystemExit(p.returncode)
