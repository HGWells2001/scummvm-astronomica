"""Build the actual engine with one temporary condition log, without header/ABI changes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom'
b=w/'p523-recipients-nov5-stage/complete-build';s=w/'builder-mask-guard-nov9-stage';s.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
seal=read(w/'opening-rgb-seal-nov6-status.json');foundation=read(b/'proof.json')
assert sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
for name,h in foundation['object_sha256'].items():assert sha(Path(name))==h
src=s/'source/engines/astronomica';src.mkdir(parents=True)
for name,h in seal['engine_sha256'].items():
    assert sha(o/'engine/astronomica'/name)==h
    if name!='astronomica.cpp':assert sha(b/'source/engines/astronomica'/name)==h
    shutil.copyfile(o/'engine/astronomica'/name,src/name)
from builder_profile_guard_source_nov9 import harden
from builder_profile_probe_source_nov9 import inject
p=src/'astronomica.cpp';p.write_text(inject(harden(p.read_text()),True))
assert {n:sha(src/n)for n in seal['engine_sha256']if n!='astronomica.cpp'}=={n:h for n,h in seal['engine_sha256'].items()if n!='astronomica.cpp'}
before=dict(base_exe_sha256=seal['exe_sha256'],engine_sha256=seal['engine_sha256'],framework_sha256=seal['framework_sha256'],candidate_astronomica_sha256=sha(p))
(s/'before.json').write_text(json.dumps(before,indent=2)+'\n');(s/'bin').mkdir()
msvc=Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231');sdkroot=Path('C:/Program Files (x86)/Windows Kits/10');sdk=sdkroot/'Include/10.0.26100.0'
env={k.upper():v for k,v in os.environ.items()}
env['INCLUDE']=';'.join(map(str,[msvc/'include',sdk/'ucrt',sdk/'shared',sdk/'um',sdk/'winrt']))
env['LIB']=';'.join(map(str,[msvc/'lib/x64',sdkroot/'Lib/10.0.26100.0/ucrt/x64',sdkroot/'Lib/10.0.26100.0/um/x64',w/'SDL2-2.32.6/lib/x64']))
env['PATH']=str(msvc/'bin/Hostx64/x64')+';'+env.get('PATH','')
def replace(text,old,new):return re.sub(re.escape(str(old)),lambda m:str(new),text,flags=re.I)
def block(path):
    lines=(b/path).read_text(encoding='utf-16').splitlines()[1:];result=[]
    for line in lines:
        if line.startswith('^'):break
        result.append(line)
    return '\n'.join(result)
def run(tool,command,label):
    for m in re.finditer(r'/(?:Fo|Fd|OUT:|PDB:|LTCGOUT:|IMPLIB:)"([^"]+)"',command,re.I):assert Path(m[1]).resolve().is_relative_to(s)
    rsp=s/(label+'.rsp');rsp.write_text(command)
    p=subprocess.run([str(msvc/'bin/Hostx64/x64'/(tool+'.exe')),'@'+str(rsp)],cwd=w/'build',env=env,capture_output=True,text=True)
    (s/(label+'.log')).write_text(p.stdout+p.stderr);p.check_returncode()
for name in ('astronomica',):
    c=block('obj/astronomica/astronomica.tlog/CL.command.1.tlog')
    c=replace(c,b/'source/engines/astronomica/astronomica.cpp',src/(name+'.cpp'))
    c=replace(c,b/'source/engines',s/'source/engines')
    c=replace(c,b/'obj/astronomica/0000-astronomica.obj',s/(name+'.obj'))
    c=replace(c,b/'bin/astronomica.pdb',s/(name+'.pdb'));run('cl',c,'cl-'+name)
c=block('obj/astronomica/astronomica.tlog/Lib.command.1.tlog')
c=replace(c,b/'obj/astronomica/0000-astronomica.obj',s/'astronomica.obj')
c=replace(c,b/'bin/astronomica.lib',s/'bin/astronomica.lib');run('lib',c,'lib')
c=block('obj/scummvm/scummvm.tlog/link.command.1.tlog')
for name in('scummvm.exe','scummvm.pdb','scummvm.lib','astronomica.lib'):c=replace(c,b/'bin'/name,s/'bin'/name)
c=replace(c,b/'obj/scummvm/scummvm.iobj',s/'scummvm.iobj');run('link',c,'link')
shutil.copyfile(b/'bin/SDL2.dll',s/'bin/SDL2.dll')
for name,h in foundation['object_sha256'].items():assert sha(Path(name))==h
assert sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
(s/'proof.json').write_text(json.dumps(dict(status='BUILDER_PROFILE_GUARD_ENGINE_CANDIDATE_BUILD_PASS',created_at=datetime.now(timezone.utc).isoformat(),base_exe_sha256=seal['exe_sha256'],candidate_exe_sha256=sha(s/'bin/scummvm.exe'),engine_headers_unchanged=True,compiled_translation_units=1,reused_verified_foundation_objects=409,candidate_engine_sha256={n:sha(src/n)for n in seal['engine_sha256']},candidate_installed=False,main_unchanged=True),indent=2)+'\n')
print('Real engine condition-trace candidate built; main unchanged')
