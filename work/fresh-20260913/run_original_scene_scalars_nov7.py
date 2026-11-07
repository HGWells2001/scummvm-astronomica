"""Compare original control-instruction replay to the real native ScriptRunner."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];b=w/'p523-recipients-nov5-stage/complete-build';out=w/'original-scene-scalars-native-nov7';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
base=read(b/'proof.json');seal=read(w/'opening-rgb-seal-nov6-status.json');reference=read(w/'original-scene-scalars-nov7/proof.json');fixture=w/'original-scene-scalars-nov7/control-fixture.bin'
helpers=read(w/'original-random-helper-relocations-nov7.json');assert helpers['status']=='ORIGINAL_RANDOM_HANDLER_MATH_RELOCATIONS_PASS'and helpers['original_exe_sha256']==reference['original_exe_sha256']
assert reference['fixture_sha256']==sha(fixture)and reference['reader_link_model_matches']and reference['predicate_body_replayed']
assert sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
for n,h in base['object_sha256'].items():assert sha(Path(n))==h
native_library=w/'opening-rgb-nov6-stage/bin/astronomica.lib';library_pin=sha(native_library)
source=r/'outputs/astronomica-cleanroom/scene_scalar_probe_nov7.cpp'
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
rows=re.findall(r'Original control native script: PASS \(P(\d+),script(\d+),commands(\d+),cases(\d+)\)',text)
summary=re.search(r'Original condition-control native verification: PASS \(scripts(\d+),cases(\d+),aggregate([0-9a-f]+);',text)
assert summary and int(summary[1])==len(rows)==reference['nonempty_scripts']and int(summary[2])==reference['control_cases']
assert sum(int(row[2])for row in rows)==reference['original_commands']and sum(int(row[3])for row in rows)==reference['control_cases']
assert sha(fixture)==reference['fixture_sha256']and sha(native_library)==library_pin and sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
for n,h in base['object_sha256'].items():assert sha(Path(n))==h
proof=dict(status='ORIGINAL_SCENE_METADATA_SCALAR_REAL_NATIVE_RUNNER_PASS',completed_at=datetime.now(timezone.utc).isoformat(),original_exe_sha256=reference['original_exe_sha256'],bit_helper_proof_sha256=sha(w/'original-random-helper-relocations-nov7.json'),analytical_replay_proof_sha256=sha(w/'original-scene-scalars-nov7/proof.json'),fixture_sha256=sha(fixture),probe_source_sha256=sha(source),native_runner_source_sha256=sha(r/'outputs/astronomica-cleanroom/engine/astronomica/script.cpp'),native_engine_library_sha256=library_pin,probe_exe_sha256=sha(out/'scummvm.exe'),installed_main_exe_sha256=seal['exe_sha256'],native_log_sha256=sha(out/'native.log'),nonempty_scripts=int(summary[1]),control_cases=int(summary[2]),fixture_command_positions=reference['original_commands'],original_command_positions=reference['source_original_commands'],original_nonempty_scripts=reference['original_nonempty_scripts'],synthetic_scripts=reference['synthetic_scripts'],all_200_scalar_words_compared=True,original_scene_metadata_used=True,original_condition_tests=reference['condition_tests'],native_aggregate=summary[3],main_and_originals_unchanged=True,gameplay_complete=False,A03_complete=False,limits=reference['limits']+['Native comparison runs the real ScriptRunner from the verified current engine library in a console test entry point, not the full game main executable','No original input, game source, core source, user preferences or personal save is modified'])
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Original reduced-control/native runner PASS:',summary[1],'scripts,',summary[2],'cases')
