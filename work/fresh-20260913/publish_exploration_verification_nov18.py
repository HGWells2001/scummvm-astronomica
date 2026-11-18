"""Publish bounded native evidence and launcher without changing the qualified engine."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, subprocess
w=Path(__file__).resolve().parent; r=w.parents[1]; pub=r/'publish/scummvm-astronomica'; o=r/'outputs/astronomica-cleanroom'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
parent=read(w/'custom-dispatch-source-extension-seal-nov17.json'); engine=read(w/'p513-control-music-seal-nov17.json')
assert git('branch','--show-current')=='main' and not git('status','--porcelain')
assert git('rev-parse','HEAD')==git('ls-remote','origin','refs/heads/main').split()[0]==parent['published_commit']
assert sha(w/'build/Releasex64/scummvm.exe')==engine['exe_sha256']
assert read(w/'exploration-playloop-native-nov18/proof.json')['status']=='ALL_MODE1_NORMAL_FRAME_MUSIC_PASS'
assert read(w/'exploration-player-nov18/user-confirmation.json')['status']=='USER_CONFIRMED_EXPLORATION_MUSIC_AUDIBLE'
assert read(w/'launcher-check-nov18/proof.json')['status']=='WORKSPACE_LAUNCHER_NATIVE_AND_FAILURE_PASS'
names=['Avvia-Astronomica.cmd','outputs/astronomica-cleanroom/EXPLORATION-VERIFICATION-NOV18.md']
helpers=['record_exploration_confirmation_nov18.py','run_exploration_player_nov18.py','check_workspace_launcher_nov18.py','exploration_playloop_source_nov18.py','exploration_playloop_source_nov18b.py','build_exploration_playloop_observer_nov18b.py','check_exploration_playloop_nov18.py','publish_exploration_verification_nov18.py','SESSION-20261118.md','exploration-player-nov18/proof.json','exploration-player-nov18/user-confirmation.json','exploration-playloop-observer-nov18b-stage/proof.json','exploration-playloop-native-nov18/proof.json','launcher-check-nov18/proof.json']
names+=['work/fresh-20260913/'+n for n in helpers]
assert all((r/n).is_file() for n in names)
git('switch','-c','codex/exploration-verification-nov18')
for n in names:
    dest=pub/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/n,dest)
m=read(pub/'SOURCE-MANIFEST.json'); files=set(m['sha256'])|set(names)
assert set(git('ls-files','--others','--exclude-standard').splitlines())<=set(names)
m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True);git('-c','core.whitespace=cr-at-eol','diff','--check')
changed=git('diff','--name-only').splitlines()+git('ls-files','--others','--exclude-standard').splitlines()
assert set(changed)==set(names)|{'SOURCE-MANIFEST.json'}
assert not git('diff','--','outputs/astronomica-cleanroom/engine','framework-overlay','SCUMMVM_BASE.json','framework-patch.json','tools','ports')
git('add','--',*changed);git('commit','-m','Verify exploration music and retain visible workspace startup errors')
git('push','-u','origin','codex/exploration-verification-nov18');commit=git('rev-parse','HEAD')
assert git('ls-remote','origin','refs/heads/main').split()[0]==parent['published_commit']
git('switch','main');git('merge','--ff-only','codex/exploration-verification-nov18');git('push','origin','main')
assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
for folder in(o/'engine/astronomica',w/'scummvm/engines/astronomica',pub/'outputs/astronomica-cleanroom/engine/astronomica'):
    assert {n:sha(folder/n)for n in engine['engine_sha256']}==engine['engine_sha256']
receipt=dict(status='VERIFIED_EXPLORATION_SOURCE_EXTENSION_PASS',at=datetime.now(timezone.utc).isoformat(),published_commit=commit,parent_published_commit=parent['published_commit'],parent_extension_sha256=sha(w/'custom-dispatch-source-extension-seal-nov17.json'),engine_release_commit=engine['published_commit'],exe_sha256=engine['exe_sha256'],engine_unchanged=True,framework_unchanged=True,observer_deployed=False,export_manifest_sha256=sha(pub/'SOURCE-MANIFEST.json'),whole_game_completion_percent=None,user_installation_ignored=True)
(w/'exploration-source-extension-seal-nov18.json').write_text(json.dumps(receipt,indent=2)+'\n')
current=read(o/'CURRENT-LOCAL-BUILD.json');current.update(published_commit=commit,last_published_commit=commit,publication_extension_context='work/fresh-20260913/exploration-source-extension-seal-nov18.json',parent_publication_extension_context='work/fresh-20260913/custom-dispatch-source-extension-seal-nov17.json',source_publication_pending=False,publication_complete=True)
(o/'CURRENT-LOCAL-BUILD.json').write_text(json.dumps(current,indent=2)+'\n');print(receipt['status'],commit)
