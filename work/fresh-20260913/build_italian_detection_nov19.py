from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];b=w/'p523-recipients-nov5-stage/complete-build';s=w/'italian-detection-nov19-stage';j=w/'speech-duck-candidate-nov19d-stage'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
seal=read(w/'speech-duck-seal-nov19.json');assert sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256'];(s/'bin').mkdir()
foundation=read(b/'proof.json')
for name,h in foundation['object_sha256'].items():assert sha(Path(name))==h
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

det='obj/scummvm-detection/scummvm-.21F7A724.tlog/'
c=block(det+'CL.command.1.tlog');c=replace(c,b/'source/engines/astronomica/detection.cpp',s/'source/engines/astronomica/detection.cpp');c=replace(c,b/'obj/scummvm-detection/0000-detection.obj',s/'detection.obj');c=replace(c,b/'bin/scummvm-detection.pdb',s/'detection.pdb');run('cl',c,'cl-detection')
c=block(det+'Lib.command.1.tlog');c=replace(c,b/'obj/scummvm-detection/0000-detection.obj',s/'detection.obj');c=replace(c,b/'bin/scummvm-detection.lib',s/'bin/scummvm-detection.lib');run('lib',c,'lib-detection')
c=(j/'link.rsp').read_text();c=replace(c,b/'bin/scummvm-detection.lib',s/'bin/scummvm-detection.lib')
for name in ['scummvm.exe','scummvm.pdb','scummvm.lib']:c=replace(c,j/'bin'/name,s/'bin'/name)
c=replace(c,j/'scummvm.iobj',s/'scummvm.iobj');run('link',c,'link');shutil.copyfile(j/'bin/SDL2.dll',s/'bin/SDL2.dll')
proof=dict(status='ITALIAN_DETECTION_BUILD_PASS',exe_sha256=sha(s/'bin/scummvm.exe'),detection_sha256=sha(s/'source/engines/astronomica/detection.cpp'),parent_exe_sha256=seal['exe_sha256'],runtime_engine_archive_sha256=sha(j/'bin/astronomica.lib'),only_detection_translation_unit_changed=True)
(s/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(proof['status'])
