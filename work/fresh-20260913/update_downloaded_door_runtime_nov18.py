"""Deliver the qualified engine to the explicitly identified download, preserving an open game."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=read(w/'door-music-seal-nov18.json');assert seal['status']=='DOOR_MUSIC_PUBLISHED_WORKSPACE_SEAL_PASS'
remote=subprocess.check_output(['git','-C',str(r/'publish/scummvm-astronomica'),'ls-remote','origin','refs/heads/main'],text=True).split()[0];assert remote==seal['published_commit']
target=Path(read(w/'downloaded-source-runtime-repair-nov18.json')['target']).resolve();assert target.is_relative_to(Path('C:/Users/mgian/Downloads/Compressed').resolve())
source=w/'build/Releasex64/scummvm.exe';assert sha(source)==seal['exe_sha256'];binary=target/'work/fresh-20260913/build/Releasex64';old=binary/'scummvm.exe';new=binary/'scummvm-door-music.exe'
assert sha(old)==read(w/'p513-control-music-seal-nov17.json')['exe_sha256'] and sha(binary/'SDL2.dll')==sha(w/'build/Releasex64/SDL2.dll')
def userfiles():
    folder=target/'userdata';return {str(p.relative_to(folder)):sha(p)for p in folder.rglob('*')if p.is_file()}if folder.exists()else{}
before=userfiles()
if new.exists():assert sha(new)==seal['exe_sha256']
else:
    with source.open('rb')as src,new.open('xb')as dst:shutil.copyfileobj(src,dst)
launcher=target/'Avvia-Astronomica.cmd';previous=launcher.read_bytes();needle=b'\\scummvm.exe"';assert previous.count(needle)==1
backup=target/'Avvia-Astronomica-prima-porte.cmd';assert not backup.exists();backup.write_bytes(previous)
updated=previous.replace(needle,b'\\scummvm-door-music.exe"');temp=launcher.with_suffix('.cmd.door-update.tmp');temp.write_bytes(updated);os.replace(temp,launcher)
version=subprocess.run([str(new),'--version'],capture_output=True,text=True,cwd=binary);assert version.returncode==0 and 'ScummVM'in version.stdout
assert sha(new)==seal['exe_sha256'] and userfiles()==before and old.exists()
receipt=dict(status='QUALIFIED_DOWNLOADED_DOOR_RUNTIME_UPDATED',at=datetime.now(timezone.utc).isoformat(),target=str(target),exe_sha256=sha(new),published_commit=seal['published_commit'],runtime_filename=new.name,launcher_sha256=sha(launcher),previous_launcher_sha256=sha(backup),previous_executable_retained=True,existing_userdata_unchanged=True,version_command_exit_code=0,no_application_terminated=True,personal_installation_ignored=True,limits=['Existing running game,if any,keeps its old executable until the user exits;next launcher invocation uses the qualified fix','Only the explicitly reported downloaded source folder is changed'])
(w/'downloaded-door-runtime-update-nov18.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(receipt['status'])
