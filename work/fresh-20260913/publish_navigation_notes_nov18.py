"""Back up the final verified scope and current continuation notes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica';o=r/'outputs/astronomica-cleanroom'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'));git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
parent=read(w/'navigation-music-source-extension-seal-nov18.json');engine=read(w/'p513-control-music-seal-nov17.json')
assert git('branch','--show-current')=='main' and not git('status','--porcelain') and git('rev-parse','HEAD')==git('ls-remote','origin','refs/heads/main').split()[0]==parent['published_commit']
assert sha(w/'build/Releasex64/scummvm.exe')==engine['exe_sha256']
assert '1,538' in(o/'EXPLORATION-VERIFICATION-NOV18.md').read_text(encoding='utf-8')
names=['outputs/astronomica-cleanroom/'+n for n in ['EXPLORATION-VERIFICATION-NOV18.md','BEHAVIOR-REQUIREMENTS.md','NEXT-STEPS.md']]+['work/fresh-20260913/'+n for n in ['SESSION-20261118.md','document_navigation_music_nov18.py','publish_navigation_notes_nov18.py']]
git('switch','-c','codex/navigation-checkpoint-nov18')
for n in names:
    dest=pub/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/n,dest)
m=read(pub/'SOURCE-MANIFEST.json');files=set(m['sha256'])|set(names);m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True);git('-c','core.whitespace=cr-at-eol','diff','--check')
changed=git('diff','--name-only').splitlines()+git('ls-files','--others','--exclude-standard').splitlines();assert set(changed)==set(names)|{'SOURCE-MANIFEST.json'}
git('add','--',*changed);git('commit','-m','Document verified navigation scope and current exploration checkpoint');git('push','-u','origin','codex/navigation-checkpoint-nov18');commit=git('rev-parse','HEAD');git('switch','main');git('merge','--ff-only','codex/navigation-checkpoint-nov18');git('push','origin','main')
assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
assert not git('diff',parent['published_commit'],'HEAD','--','outputs/astronomica-cleanroom/engine','framework-overlay','tools','SCUMMVM_BASE.json','framework-patch.json','ports')
receipt=dict(status='VERIFIED_NAVIGATION_CHECKPOINT_SOURCE_EXTENSION_PASS',at=datetime.now(timezone.utc).isoformat(),published_commit=commit,parent_published_commit=parent['published_commit'],parent_extension_sha256=sha(w/'navigation-music-source-extension-seal-nov18.json'),exe_sha256=engine['exe_sha256'],engine_unchanged=True,framework_unchanged=True,export_manifest_sha256=sha(pub/'SOURCE-MANIFEST.json'),whole_game_completion_percent=None,user_installation_ignored=True)
(w/'navigation-checkpoint-source-extension-seal-nov18.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
current=read(o/'CURRENT-LOCAL-BUILD.json');current.update(published_commit=commit,last_published_commit=commit,publication_extension_context='work/fresh-20260913/navigation-checkpoint-source-extension-seal-nov18.json',parent_publication_extension_context='work/fresh-20260913/navigation-music-source-extension-seal-nov18.json',source_publication_pending=False,publication_complete=True);(o/'CURRENT-LOCAL-BUILD.json').write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8');print(receipt['status'],commit)
