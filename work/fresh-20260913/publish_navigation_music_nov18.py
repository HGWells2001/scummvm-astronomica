"""Publish completed route qualification without changing the verified production engine."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';pub=r/'publish/scummvm-astronomica'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
parent=read(w/'exploration-source-extension-seal-nov18.json');engine=read(w/'p513-control-music-seal-nov17.json')
native=read(w/'navigation-music-native-nov18b/proof.json');mapped=read(w/'navigation-music-requirements-nov18b/proof.json');p419=read(w/'p419-foreground-native-nov18b/proof.json')
assert native['status']=='ORIGINAL_NAVIGATION_ACTIVE_MUSIC_PASS' and mapped['status']=='CURRENT_NAVIGATION_MUSIC_REQUIREMENT_MAP_PASS' and p419['status']=='ORIGINAL_P419_REPEATED_FOREGROUND_NAVIGATION_PASS'
assert mapped['native_proof_sha256']==sha(w/'navigation-music-native-nov18b/proof.json')
assert git('branch','--show-current')=='main' and not git('status','--porcelain') and git('rev-parse','HEAD')==git('ls-remote','origin','refs/heads/main').split()[0]==parent['published_commit']
assert sha(w/'build/Releasex64/scummvm.exe')==engine['exe_sha256']==native['canonical_exe_sha256']==p419['canonical_exe_sha256']
helpers=['prepare_navigation_music_cases_nov18.py','navigation_music_source_nov18.py','navigation_music_source_nov18b.py','build_navigation_music_observer_nov18b.py','check_navigation_music_nov18b.py','p419_foreground_source_nov18.py','build_p419_foreground_observer_nov18.py','check_p419_foreground_nov18.py','check_p419_foreground_nov18b.py','publish_navigation_music_nov18.py','SESSION-20261118.md','navigation-music-observer-nov18b-stage/proof.json','navigation-music-native-nov18b/proof.json','navigation-music-requirements-nov18b/proof.json','p419-foreground-observer-nov18-stage/proof.json','p419-foreground-native-nov18b/proof.json']
names=['work/fresh-20260913/'+n for n in helpers]+['outputs/astronomica-cleanroom/map_navigation_music_requirements_nov18.py','outputs/astronomica-cleanroom/BEHAVIOR-REQUIREMENTS.md','outputs/astronomica-cleanroom/EXPLORATION-VERIFICATION-NOV18.md','outputs/astronomica-cleanroom/NEXT-STEPS.md']
names+=['work/fresh-20260913/verify_completed_navigation_music_nov18.py','work/fresh-20260913/document_navigation_music_nov18.py']
git('switch','-c','codex/navigation-music-verification-nov18')
for n in names:
    dest=pub/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/n,dest)
m=read(pub/'SOURCE-MANIFEST.json');files=set(m['sha256'])|set(names);assert set(git('ls-files','--others','--exclude-standard').splitlines())<=set(names)
m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True);git('-c','core.whitespace=cr-at-eol','diff','--check')
changed=git('diff','--name-only').splitlines()+git('ls-files','--others','--exclude-standard').splitlines();assert set(changed)<=set(names)|{'SOURCE-MANIFEST.json'}
assert not git('diff','--','outputs/astronomica-cleanroom/engine','framework-overlay','SCUMMVM_BASE.json','framework-patch.json','tools','ports')
git('add','--',*changed);git('commit','-m','Qualify original exploration routes with active music and P419 foreground cleanup');git('push','-u','origin','codex/navigation-music-verification-nov18');commit=git('rev-parse','HEAD')
assert git('ls-remote','origin','refs/heads/main').split()[0]==parent['published_commit'];git('switch','main');git('merge','--ff-only','codex/navigation-music-verification-nov18');git('push','origin','main')
assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
for folder in(o/'engine/astronomica',w/'scummvm/engines/astronomica',pub/'outputs/astronomica-cleanroom/engine/astronomica'):
    assert {n:sha(folder/n)for n in engine['engine_sha256']}==engine['engine_sha256']
receipt=dict(status='VERIFIED_NAVIGATION_MUSIC_SOURCE_EXTENSION_PASS',at=datetime.now(timezone.utc).isoformat(),published_commit=commit,parent_published_commit=parent['published_commit'],parent_extension_sha256=sha(w/'exploration-source-extension-seal-nov18.json'),engine_release_commit=engine['published_commit'],exe_sha256=engine['exe_sha256'],engine_unchanged=True,framework_unchanged=True,observer_deployed=False,native_proof_sha256=sha(w/'navigation-music-native-nov18b/proof.json'),requirement_map_sha256=sha(w/'navigation-music-requirements-nov18b/proof.json'),p419_proof_sha256=sha(w/'p419-foreground-native-nov18b/proof.json'),export_manifest_sha256=sha(pub/'SOURCE-MANIFEST.json'),whole_game_completion_percent=None,user_installation_ignored=True)
(w/'navigation-music-source-extension-seal-nov18.json').write_text(json.dumps(receipt,indent=2)+'\n')
current=read(o/'CURRENT-LOCAL-BUILD.json');current.update(published_commit=commit,last_published_commit=commit,publication_extension_context='work/fresh-20260913/navigation-music-source-extension-seal-nov18.json',parent_publication_extension_context='work/fresh-20260913/exploration-source-extension-seal-nov18.json',source_publication_pending=False,publication_complete=True);(o/'CURRENT-LOCAL-BUILD.json').write_text(json.dumps(current,indent=2)+'\n');print(receipt['status'],commit)
