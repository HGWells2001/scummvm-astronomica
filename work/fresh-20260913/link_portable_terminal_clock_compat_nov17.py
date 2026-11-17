"""Finish the already compiled isolated all-engine observer; preserve original link inputs."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
from datetime import datetime,timezone
w=Path(__file__).resolve().parent;s=w/'portable-terminal-clock-compat-nov17-stage';b=Path('D:/00/_BUILD_SCUMMVM_ALL_VS');portable=Path('D:/00/_SCUMMVM_PORTATILE')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin=sha(portable/'scummvm.exe');assert pin=='e73a9ecdca25193c6b01804722c6e6623c9f7ccb1950fa2e68e3da963ae70d77'
names=('astronomica','conditions_test','help','metaengine','resource','script','sprites')
for n in names:
 assert (s/(n+'.obj')).exists()and 'error C'not in(s/('cl-'+n+'.log')).read_text()
lines=(b/'Releasex64/scummvm/scummvm.tlog/link.command.1.tlog').read_text(encoding='utf-16').splitlines()
assert sum(l.startswith('^')for l in lines)==1
link='\n'.join(l for l in lines if not l.startswith('^'));inputs={}
paths=re.findall(r'"([^"]+\.(?:lib|obj|res))"',link,re.I)
paths.extend(l.strip().strip('"')for l in link.splitlines()if re.fullmatch(r'[A-Za-z]:\\[^\r\n]+\.(?:lib|obj|res)',l.strip(),re.I))
for path in paths:
 p=Path(path);p=p if p.is_absolute()else b/p
 if p.exists():inputs[str(p.resolve())]=sha(p)
old=next(p for p in inputs if Path(p).name.lower()=='astronomica.lib')
link=re.sub(re.escape(old),lambda m:str(s/'bin/astronomica.lib'),link,flags=re.I)
for flag,name in [('OUT','scummvm.exe'),('PDB','scummvm.pdb'),('IMPLIB','scummvm.lib'),('LTCGOUT','scummvm.iobj'),('PGD','scummvm.pgd'),('MAP','scummvm.map'),('ILK','scummvm.ilk'),('MANIFESTFILE','scummvm.intermediate.manifest')]:
 link=re.sub('/'+flag+r':"[^"]+"',lambda m:'/'+flag+':"'+str(s/'bin'/name)+'"',link,flags=re.I)
assert '/OUT:"'+str(s/'bin/scummvm.exe')+'"'in link
msvc=Path('C:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/MSVC/14.51.36231');sdk=Path('C:/Program Files (x86)/Windows Kits/10/Lib/10.0.26100.0')
env={k.upper():v for k,v in os.environ.items()};env['LIB']=';'.join(map(str,[msvc/'lib/x64',sdk/'ucrt/x64',sdk/'um/x64']));env['PATH']=str(msvc/'bin/Hostx64/x64')+';'+env.get('PATH','')
(s/'link.rsp').write_text(link);result=subprocess.run([str(msvc/'bin/Hostx64/x64/link.exe'),'@'+str(s/'link.rsp')],cwd=b,env=env,capture_output=True,text=True)
(s/'link.log').write_text(result.stdout+result.stderr);result.check_returncode()
for n,h in inputs.items():assert sha(Path(n))==h
assert sha(portable/'scummvm.exe')==pin
for p in portable.glob('*.dll'):shutil.copyfile(p,s/'bin'/p.name)
for name in ('residualvm.zip','fonts.dat','classicmacfonts.dat','encoding.dat'):shutil.copyfile(portable/name,s/'bin'/name)
src=s/'source/engines/astronomica'
(s/'proof.json').write_text(json.dumps(dict(status='PORTABLE_TERMINAL_CLOCK_COMPAT_BUILD_PASS',created_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(s/'bin/scummvm.exe'),selected_portable_exe_sha256=pin,compiled_translation_units=7,original_link_inputs_sha256=inputs,engine_sha256={p.name:sha(p)for p in src.iterdir()if p.is_file()},portable_unchanged=True,installed=False,limitations=['Seven accepted cleanroom engine units plus verified restore fix on selected portable framework; not installed or qualified','Older RichTextWidget focus callback mapped to lostFocusWidget; native behavior requires separate qualification','Explicit object/library inputs pinned, implicit system library resolution not frozen']),indent=2)+'\n')
print('PORTABLE_TERMINAL_CLOCK_COMPAT_BUILD_PASS')
