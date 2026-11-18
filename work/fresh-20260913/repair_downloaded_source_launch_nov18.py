"""Add the locally qualified runtime to the user's explicitly identified source ZIP folder."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parent
target=Path('C:/Users/mgian/Downloads/Compressed/scummvm-astronomica-main_4/scummvm-astronomica-main').resolve()
assert target.is_dir() and (target/'Avvia-Astronomica.cmd').is_file()
assert target.is_relative_to(Path('C:/Users/mgian/Downloads/Compressed').resolve())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=json.loads((w/'p513-control-music-seal-nov17.json').read_text())
assert sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']
def userfiles():
    folder=target/'userdata'
    return {str(p.relative_to(folder)):sha(p)for p in folder.rglob('*')if p.is_file()}if folder.exists()else{}
before=userfiles()
items=[(w/'build/Releasex64/scummvm.exe','work/fresh-20260913/build/Releasex64/scummvm.exe'),
       (w/'build/Releasex64/SDL2.dll','work/fresh-20260913/build/Releasex64/SDL2.dll'),
       (w/'SDL2-2.32.6/LICENSE.txt','work/fresh-20260913/build/Releasex64/SDL2-LICENSE.txt'),
       (w/'scummvm/dists/engine-data/fonts.dat','work/fresh-20260913/fonts/fonts.dat')]
created=[]
for source,name in items:
    dest=target/name;assert dest.resolve().is_relative_to(target)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert sha(dest)==sha(source),'Existing different file: '+name
    else:
        with source.open('rb')as src,dest.open('xb')as dst:shutil.copyfileobj(src,dst)
        created.append(name)
    assert sha(dest)==sha(source)
exe=target/items[0][1]
version=subprocess.run([str(exe),'--version'],capture_output=True,text=True,cwd=exe.parent)
assert version.returncode==0 and 'ScummVM'in version.stdout,version.stderr
assert userfiles()==before
receipt=dict(status='DOWNLOADED_SOURCE_RUNTIME_REPAIRED',at=datetime.now(timezone.utc).isoformat(),target=str(target),exe_sha256=sha(exe),created=created,sha256={n:sha(target/n)for _,n in items},version_command_exit_code=version.returncode,existing_userdata_unchanged=True,game_assets_copied=False,personal_installation_ignored=True,limits=['Copies the already-qualified local runtime; not a new compilation or a public binary release','The standard GitHub source ZIP still does not contain a compiled executable'])
(w/'downloaded-source-runtime-repair-nov18.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(receipt['status'],str(target))
