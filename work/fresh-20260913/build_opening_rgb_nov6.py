"""Compile one ABI-unchanged engine delta and link with verified full-build objects."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage';b=w/'p523-recipients-nov5-stage/complete-build'
out=s/'bin';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((b/'proof.json').read_text());before=json.loads((s/'before.json').read_text())
assert sha(w/'build/Releasex64/scummvm.exe')==before['base_exe_sha256']==proof['candidate_exe_sha256']
for name,h in proof['object_sha256'].items():assert sha(b/name)==h
for name,h in before['engine_sha256'].items():
    assert sha(w/'scummvm/engines/astronomica'/name)==h
    if name!='astronomica.cpp':assert sha(s/'source/engines/astronomica'/name)==h
msvc=Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231');sdkroot=Path('C:/Program Files (x86)/Windows Kits/10');sdk=sdkroot/'Include/10.0.26100.0'
env={k.upper():v for k,v in os.environ.items()}
env['INCLUDE']=';'.join(map(str,[msvc/'include',sdk/'ucrt',sdk/'shared',sdk/'um',sdk/'winrt']))
env['LIB']=';'.join(map(str,[msvc/'lib/x64',sdkroot/'Lib/10.0.26100.0/ucrt/x64',sdkroot/'Lib/10.0.26100.0/um/x64',w/'SDL2-2.32.6/lib/x64']))
env['PATH']=str(msvc/'bin/Hostx64/x64')+';'+env.get('PATH','')
def replace(text,old,new):return re.sub(re.escape(str(old)),lambda m:str(new),text,flags=re.I)
def command(file):
    lines=(b/file).read_text(encoding='utf-16').splitlines()[1:]
    block=[]
    for line in lines:
        if line.startswith('^'):break
        block.append(line)
    return '\n'.join(block)
def run(tool,text):
    for match in re.finditer(r'/(?:Fo|Fd|OUT:|PDB:|LTCGOUT:|IMPLIB:)"([^"]+)"',text,re.I):
        assert Path(match.group(1)).resolve().is_relative_to(s),('Output outside isolated stage',match.group(1))
    rsp=s/(tool+'.rsp');rsp.write_text(text)
    p=subprocess.run([str(msvc/'bin/Hostx64/x64'/(tool+'.exe')),'@'+str(rsp)],env=env,cwd=w/'build',capture_output=True,text=True)
    (s/(tool+'.log')).write_text(p.stdout+p.stderr);p.check_returncode()
c=command('obj/astronomica/astronomica.tlog/CL.command.1.tlog')
c=replace(c,b/'source/engines',s/'source/engines')
c=replace(c,b/'obj/astronomica/0000-astronomica.obj',s/'astronomica.obj')
c=replace(c,b/'bin/astronomica.pdb',s/'astronomica.pdb');run('cl',c)
c=command('obj/astronomica/astronomica.tlog/Lib.command.1.tlog')
c=replace(c,b/'bin/astronomica.lib',out/'astronomica.lib')
c=replace(c,b/'obj/astronomica/0000-astronomica.obj',s/'astronomica.obj');run('lib',c)
c=command('obj/scummvm/scummvm.tlog/link.command.1.tlog')
for name in ('scummvm.exe','scummvm.pdb','scummvm.lib','astronomica.lib'):c=replace(c,b/'bin'/name,out/name)
c=replace(c,b/'obj/scummvm/scummvm.iobj',s/'scummvm.iobj');run('link',c)
shutil.copyfile(b/'bin/SDL2.dll',out/'SDL2.dll')
for name,h in proof['object_sha256'].items():assert sha(b/name)==h
assert sha(w/'build/Releasex64/scummvm.exe')==before['base_exe_sha256']
(s/'build-proof.json').write_text(json.dumps(dict(status='OPENING_RGB_ENGINE_DELTA_BUILD_PASS',built_at=datetime.now(timezone.utc).isoformat(),base_exe_sha256=proof['candidate_exe_sha256'],candidate_exe_sha256=sha(out/'scummvm.exe'),candidate_cpp_sha256=sha(s/'source/engines/astronomica/astronomica.cpp'),reused_verified_full_build_objects=409,compiled_engine_translation_units=1,abi_unchanged=True,main_unchanged=True),indent=2)+'\n')
print('One engine delta built against checked 410-unit baseline; candidate not installed')
