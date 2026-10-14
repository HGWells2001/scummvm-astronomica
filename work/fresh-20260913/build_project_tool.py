import os,subprocess
from pathlib import Path
root=Path('work/fresh-20260913/scummvm').resolve();env={k.upper():v for k,v in os.environ.items()}
cmd=[r'C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe',str(root/'devtools/create_project/msvc/create_project.vcxproj'),'/p:Configuration=Release','/p:Platform=Win32','/p:PlatformToolset=v145','/p:WindowsTargetPlatformVersion=10.0','/p:SolutionDir='+str(root/'devtools/create_project/msvc')+'\\','/verbosity:minimal','/nologo']
raise SystemExit(subprocess.call(cmd,cwd=root,env=env))
