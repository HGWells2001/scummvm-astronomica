"""Commit the qualified paired export, verify a fresh clone, then advance main."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
assert git('branch','--show-current')=='codex/shared-door-music-nov18'
installer=read(w/'door-music-install-n18/proof.json');assert installer['status']=='DOOR_MUSIC_EXPORTED_INSTALLER_INTEGRATION_PASS'
name='work/fresh-20260913/door-music-install-n18/proof.json';dest=pub/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(w/'door-music-install-n18/proof.json',dest)
m=read(pub/'SOURCE-MANIFEST.json');names=set(m['sha256'])|{name};assert set(git('ls-files','--others','--exclude-standard').splitlines())<=names;m['sha256']={n:sha(pub/n)for n in sorted(names)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True);git('-c','core.whitespace=cr-at-eol','diff','--check')
changed=git('diff','--name-only').splitlines()+git('ls-files','--others','--exclude-standard').splitlines();assert all(n=='SOURCE-MANIFEST.json'or n in names for n in changed)
git('add','--',*changed);git('commit','-m','Keep shared door effects over uninterrupted exploration music');git('push','-u','origin','codex/shared-door-music-nov18');commit=git('rev-parse','HEAD')
clone=r/'publish/verify-door-music-nov18';assert not clone.exists();subprocess.run(['git','clone','--single-branch','--branch','codex/shared-door-music-nov18',git('remote','get-url','origin'),str(clone)],check=True)
assert subprocess.check_output(['git','-C',str(clone),'rev-parse','HEAD'],text=True).strip()==commit;subprocess.run(['python',str(clone/'tools/verify_export.py')],check=True)
assert git('ls-remote','origin','refs/heads/main').split()[0]==read(w/'source-download-launcher-seal-nov18.json')['published_commit']
git('switch','main');git('merge','--ff-only','codex/shared-door-music-nov18');git('push','origin','main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
(w/'door-music-release-commit-nov18.json').write_text(json.dumps(dict(status='DOOR_MUSIC_SOURCE_MAIN_PUBLISHED_PASS',at=datetime.now(timezone.utc).isoformat(),commit=commit,independent_clone=str(clone)),indent=2)+'\n',encoding='utf-8');print('DOOR_MUSIC_SOURCE_MAIN_PUBLISHED_PASS',commit)
