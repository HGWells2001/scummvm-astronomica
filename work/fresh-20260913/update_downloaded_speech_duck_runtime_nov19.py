"""Update the reported download with matching qualified source/runtime, preserving user data."""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import hashlib,json,os,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=read(w/'speech-duck-seal-nov19.json');assert seal['status']=='SPEECH_DUCK_PUBLISHED_WORKSPACE_SEAL_PASS'
remote=subprocess.check_output(['git','-C',str(pub),'ls-remote','origin','refs/heads/main'],text=True).split()[0]
assert remote==subprocess.check_output(['git','-C',str(pub),'rev-parse','HEAD'],text=True).strip()
base=read(pub/'SCUMMVM_BASE.json');assert base['validated_executable_sha256']==seal['exe_sha256']and base['engine_sha256']==seal['engine_sha256']and base['framework_sha256']==seal['framework_sha256']
target=Path(read(w/'downloaded-source-runtime-repair-nov18.json')['target']).resolve();assert target.is_relative_to(Path('C:/Users/mgian/Downloads/Compressed').resolve())
source=w/'build/Releasex64/scummvm.exe';assert sha(source)==seal['exe_sha256'];exe=target/'work/fresh-20260913/build/Releasex64/scummvm.exe'
assert sha(exe)==read(w/'all-effects-seal-nov19.json')['exe_sha256']
query="Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq '"+str(exe)+"' } | Select-Object -ExpandProperty ProcessId"
assert not subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True).stdout.strip(),'Downloaded game is running; leave it untouched until it exits'
def inside(name):
    assert PurePosixPath(name).as_posix()==name
    path=(target/name).resolve();assert path.is_relative_to(target);return path
old=read(target/'SOURCE-MANIFEST.json');new=read(pub/'SOURCE-MANIFEST.json')
for name,h in old['sha256'].items():assert sha(inside(name))==h,'Modified downloaded source: '+name
for name,h in new['sha256'].items():
    assert sha(pub/name)==h
    p=inside(name)
    if p.exists()and name not in old['sha256']:assert sha(p)==h,'Untracked downloaded source: '+name
def userfiles():
    folder=target/'userdata';return {str(p.relative_to(folder)):sha(p)for p in folder.rglob('*')if p.is_file()}if folder.exists()else{}
before=userfiles();updates={inside(n):(pub/n).read_bytes()for n,h in new['sha256'].items()if not inside(n).exists()or sha(inside(n))!=h}
updates[target/'SOURCE-MANIFEST.json']=(pub/'SOURCE-MANIFEST.json').read_bytes();updates[exe]=source.read_bytes()
saved={p:p.read_bytes()if p.exists()else None for p in updates};backup=w/'downloaded-source-before-speech-duck-update-nov19';backup.mkdir(exist_ok=False)
for p,data in saved.items():
    if data is not None:
        dest=backup/p.relative_to(target);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
done=[]
try:
    for p,data in updates.items():
        p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.qualified-update.tmp');temp.write_bytes(data);os.replace(temp,p);done.append(p)
    subprocess.run(['python',str(target/'tools/verify_export.py')],check=True,capture_output=True)
    version=subprocess.run([str(exe),'--version'],capture_output=True,text=True,cwd=exe.parent);assert version.returncode==0 and 'ScummVM'in version.stdout
    assert sha(exe)==seal['exe_sha256']and userfiles()==before
except Exception:
    for p in reversed(done):
        assert p.resolve().is_relative_to(target)
        if saved[p]is None:p.unlink()
        else:p.write_bytes(saved[p])
    raise
receipt=dict(status='QUALIFIED_DOWNLOADED_SPEECH_DUCK_RUNTIME_UPDATED',at=datetime.now(timezone.utc).isoformat(),target=str(target),exe_sha256=sha(exe),published_commit=remote,engine_release_commit=seal['published_commit'],matching_source_manifest_sha256=sha(target/'SOURCE-MANIFEST.json'),updater_sha256=sha(Path(__file__)),updated_files=len(updates),backup=str(backup),existing_userdata_unchanged=True,version_command_exit_code=0,no_application_terminated=True,personal_installation_ignored=True,limits=['Only the explicitly reported source download is changed; existing source hashes must match before replacement','Previous source/runtime retained in a local backup; settings and saves untouched'])
(w/'downloaded-speech-duck-runtime-update-nov19.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(receipt['status'])
