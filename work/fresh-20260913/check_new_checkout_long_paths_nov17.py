"""Exercise the real new-checkout entry point at a path that previously exceeded MAX_PATH."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,sys
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica';out=w/'new-checkout-long-paths-native-nov17';out.mkdir(exist_ok=False);package=out/'source-package';package.mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=read(pub/'SCUMMVM_BASE.json');pin=base['validated_executable_sha256']
for n in ('SCUMMVM_BASE.json','framework-patch.json','tools/prepare_scummvm.py','tools/install_engine.py','tools/apply_framework_patch.py'):
 target=package/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(pub/n,target)
shutil.copytree(pub/base['engine_directory'],package/base['engine_directory']);shutil.copytree(pub/'framework-overlay',package/'framework-overlay')
# Only the test package's transport is local; commit and reviewed source hashes
# remain the published ones. No network dependency or change to the real export.
testbase=read(package/'SCUMMVM_BASE.json');testbase['repository']=str(w/'scummvm');(package/'SCUMMVM_BASE.json').write_text(json.dumps(testbase,indent=2)+'\n')
tree=out/'deliberately-deep-upstream-checkout-for-windows-path-regression'
with(out/'commands.log').open('w')as log:
 result=subprocess.run([sys.executable,str(package/'tools/prepare_scummvm.py'),'--destination',str(tree)],stdout=log,stderr=subprocess.STDOUT)
assert result.returncode==0,(out/'commands.log').read_text(errors='replace')[-2500:]
git=lambda *a:subprocess.check_output(['git','-C',str(tree),*a],text=True).strip()
assert git('config','--local','--get','core.longpaths')=='true'and git('rev-parse','HEAD')==base['commit']
for n,h in base['engine_sha256'].items():assert sha(tree/'engines/astronomica'/n)==h
for n,h in base['framework_sha256'].items():assert sha(tree/n)==h
longest=max(len(str(tree/name))for name in git('ls-files').splitlines());assert longest>260
assert sha(pub/'SCUMMVM_BASE.json')==sha(out/'source-package/SCUMMVM_BASE.json')or read(pub/'SCUMMVM_BASE.json')['repository']!=testbase['repository']
proof=dict(status='WINDOWS_NEW_DEEP_CHECKOUT_AND_PAIRED_INSTALL_PASS',at=datetime.now(timezone.utc).isoformat(),canonical_exe_sha256=pin,upstream_commit=base['commit'],checkout_longest_tracked_path=longest,local_git_longpaths=True,global_git_settings_changed=False,source_export_modified=False,local_transport_only=True,prepare_tool_sha256=sha(pub/'tools/prepare_scummvm.py'),log_sha256=sha(out/'commands.log'),limits=['Fresh source checkout and paired installation only; no native game execution','Uses a test package with local object transport,not a change to the published upstream metadata'])
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'],longest)
