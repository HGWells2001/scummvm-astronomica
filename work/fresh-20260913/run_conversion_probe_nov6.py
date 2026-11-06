"""Use the exact reviewed full-build framework objects in an isolated console probe."""
from pathlib import Path
import hashlib,json,os,re,subprocess,shutil
w=Path(__file__).resolve().parent;b=w/'p523-recipients-nov5-stage/complete-build';out=w/'opening-ui-nov6/conversion-build';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((b/'proof.json').read_text())
for n,h in proof['object_sha256'].items():assert sha(Path(n))==h
msvc=Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231');sdkroot=Path('C:/Program Files (x86)/Windows Kits/10');sdk=sdkroot/'Include/10.0.26100.0'
env={k.upper():v for k,v in os.environ.items()};env['INCLUDE']=';'.join(map(str,[msvc/'include',sdk/'ucrt',sdk/'shared',sdk/'um',sdk/'winrt']))
env['LIB']=';'.join(map(str,[msvc/'lib/x64',sdkroot/'Lib/10.0.26100.0/ucrt/x64',sdkroot/'Lib/10.0.26100.0/um/x64',w/'SDL2-2.32.6/lib/x64']))
env['PATH']=str(msvc/'bin/Hostx64/x64')+';'+env.get('PATH','')
def run(tool,text):
 for m in re.finditer(r'/(?:Fo|Fd|OUT:|PDB:|LTCGOUT:|IMPLIB:)"([^"]+)"',text,re.I):assert Path(m.group(1)).resolve().is_relative_to(out)
 rsp=out/(tool+'.rsp');rsp.write_text(text);p=subprocess.run([str(msvc/'bin/Hostx64/x64'/(tool+'.exe')),'@'+str(rsp)],env=env,capture_output=True,text=True,cwd=w/'build');(out/(tool+'.log')).write_text(p.stdout+p.stderr);p.check_returncode()
def replace(s,a,z):return re.sub(re.escape(str(a)),lambda m:str(z),s,flags=re.I)
c=(b/'obj/astronomica/astronomica.tlog/CL.command.1.tlog').read_text(encoding='utf-16').splitlines()[1]
c=replace(c,b/'source/engines/astronomica/astronomica.cpp',w/'opening-ui-nov6/conversion_probe.cpp')
c=replace(c,b/'obj/astronomica/0000-astronomica.obj',out/'probe.obj');c=replace(c,b/'bin/astronomica.pdb',out/'probe.pdb');run('cl',c)
c='\n'.join((b/'obj/scummvm/scummvm.tlog/link.command.1.tlog').read_text(encoding='utf-16').splitlines()[1:])
for name in ('scummvm.exe','scummvm.pdb','scummvm.lib'):c=replace(c,b/'bin'/name,out/name)
c=replace(c,b/'obj/scummvm/scummvm.iobj',out/'scummvm.iobj')
c=c.replace('/ENTRY:"WinMainCRTStartup"','/ENTRY:"mainCRTStartup"')
assert '/ENTRY:"mainCRTStartup"'in c
c+='\n"'+str(out/'probe.obj')+'"\n';run('link',c)
shutil.copyfile(b/'bin/SDL2.dll',out/'SDL2.dll')
original=Path('D:/astro/PLACES/P1/MEGAFILE.HYP');pin=sha(original)
p=subprocess.run([str(out/'scummvm.exe')],capture_output=True,text=True,env=env,timeout=30)
(out/'native.log').write_text(p.stdout+p.stderr);assert sha(original)==pin
for n,h in proof['object_sha256'].items():assert sha(Path(n))==h
print(p.stdout+p.stderr);print('Exit',p.returncode);p.check_returncode()
