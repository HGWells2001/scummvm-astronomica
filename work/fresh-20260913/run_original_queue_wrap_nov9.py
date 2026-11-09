"""Compare original control-instruction replay to the real native ScriptRunner."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];b=w/'p523-recipients-nov5-stage/complete-build';out=w/'original-queue-wrap-native-nov9';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
base=read(b/'proof.json');seal=read(w/'opening-rgb-seal-nov6-status.json');reference=read(w/'original-queue-wrap-nov9/proof.json');fixture=w/'original-queue-wrap-nov9/fixture.bin'
assert reference['status']=='ORIGINAL_QUEUE_INSTRUCTION_FIXTURE_READY'and reference['fixture_sha256']==sha(fixture)
assert sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
for n,h in base['object_sha256'].items():assert sha(Path(n))==h
native_library=w/'opening-rgb-nov6-stage/bin/astronomica.lib';library_pin=sha(native_library)
source=r/'outputs/astronomica-cleanroom/queue_wrap_probe_nov9.cpp'
msvc=Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231');sdkroot=Path('C:/Program Files (x86)/Windows Kits/10');sdk=sdkroot/'Include/10.0.26100.0'
env={k.upper():v for k,v in os.environ.items()};env['INCLUDE']=';'.join(map(str,[msvc/'include',sdk/'ucrt',sdk/'shared',sdk/'um',sdk/'winrt']))
env['LIB']=';'.join(map(str,[msvc/'lib/x64',sdkroot/'Lib/10.0.26100.0/ucrt/x64',sdkroot/'Lib/10.0.26100.0/um/x64',w/'SDL2-2.32.6/lib/x64']))
env['PATH']=str(msvc/'bin/Hostx64/x64')+';'+env.get('PATH','')
def replace(s,a,z):return re.sub(re.escape(str(a)),lambda m:str(z),s,flags=re.I)
def run(tool,text):
    for match in re.finditer(r'/(?:Fo|Fd|OUT:|PDB:|LTCGOUT:|IMPLIB:)"([^"]+)"',text,re.I):assert Path(match.group(1)).resolve().is_relative_to(out)
    rsp=out/(tool+'.rsp');rsp.write_text(text)
    result=subprocess.run([str(msvc/'bin/Hostx64/x64'/(tool+'.exe')),'@'+str(rsp)],cwd=w/'build',env=env,capture_output=True,text=True)
    (out/(tool+'.log')).write_text(result.stdout+result.stderr);result.check_returncode()
c=(b/'obj/astronomica/astronomica.tlog/CL.command.1.tlog').read_text(encoding='utf-16').splitlines()[1]
c=replace(c,b/'source/engines/astronomica/astronomica.cpp',source);c=replace(c,b/'obj/astronomica/0000-astronomica.obj',out/'probe.obj');c=replace(c,b/'bin/astronomica.pdb',out/'probe.pdb');run('cl',c)
c='\n'.join((b/'obj/scummvm/scummvm.tlog/link.command.1.tlog').read_text(encoding='utf-16').splitlines()[1:])
for name in('scummvm.exe','scummvm.pdb','scummvm.lib'):c=replace(c,b/'bin'/name,out/name)
c=replace(c,b/'obj/scummvm/scummvm.iobj',out/'scummvm.iobj');c=replace(c,b/'bin/astronomica.lib',native_library)
c=c.replace('/ENTRY:"WinMainCRTStartup"','/ENTRY:"mainCRTStartup"');assert '/ENTRY:"mainCRTStartup"'in c
c+='\n"'+str(out/'probe.obj')+'"\n';run('link',c);shutil.copyfile(b/'bin/SDL2.dll',out/'SDL2.dll')
with(out/'native.log').open('w')as log:result=subprocess.run([str(out/'scummvm.exe'),str(fixture)],env=env,cwd=w,stdout=log,stderr=subprocess.STDOUT,timeout=180)
text=(out/'native.log').read_text();result.check_returncode();assert 'FAIL'not in text
summary=re.search(r'Original queue native PASS:cases(\d+),ticks(\d+),aggregate([0-9a-f]+)',text)
assert summary and int(summary[1])==reference['cases']and int(summary[2])==reference['ticks']
assert sha(fixture)==reference['fixture_sha256']and sha(native_library)==library_pin and sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
for n,h in base['object_sha256'].items():assert sha(Path(n))==h
proof=dict(status='ORIGINAL_QUEUE_REAL_NATIVE_COMPARISON_PASS',completed_at=datetime.now(timezone.utc).isoformat(),original_exe_sha256=reference['original_exe_sha256'],fixture_sha256=sha(fixture),oracle_proof_sha256=sha(w/'original-queue-wrap-nov9/proof.json'),probe_source_sha256=sha(source),probe_exe_sha256=sha(out/'scummvm.exe'),installed_main_exe_sha256=seal['exe_sha256'],native_log_sha256=sha(out/'native.log'),cases=int(summary[1]),ticks=int(summary[2]),aggregate=summary[3],runtime_unchanged=True,limits=reference['limits'])
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Original queue/native PASS:',summary[1],'cases,',summary[2],'ticks')
