"""Seal the installed runtime, paired source, native evidence and remote backup."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';pub=r/'publish/scummvm-astronomica';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
i=read(w/'door-music-integration-nov18.json');pin=i['candidate_exe_sha256'];commit=git('rev-parse','HEAD');assert git('branch','--show-current')=='main'and not git('status','--porcelain')and git('ls-remote','origin','refs/heads/main').split()[0]==commit
assert subprocess.check_output(['git','-C',str(r/'publish/verify-door-music-nov18'),'rev-parse','HEAD'],text=True).strip()==commit and sha(w/'build/Releasex64/scummvm.exe')==pin
for folder in(o/'engine/astronomica',w/'scummvm/engines/astronomica',pub/'outputs/astronomica-cleanroom/engine/astronomica'):assert {n:sha(folder/n)for n in i['engine_sha256']}==i['engine_sha256']
for n,h in i['framework_sha256'].items():assert sha(w/'scummvm'/n)==sha(pub/'framework-overlay'/n)==h
snapshot=Path(i['snapshot']);manifest=read(snapshot/'snapshot-manifest.json')
for n,h in manifest.items():assert sha(snapshot/n)==h
gates=dict(i['gates'])
for n,key in [('door-music-installed-native-nov18/proof.json','candidate_exe_sha256'),('door-music-main-genuine-nov18/proof.json','consumer_exe_sha256')]:assert read(w/n)['status'].endswith('PASS')and read(w/n)[key]==pin;gates[n]=sha(w/n)
p=read(w/'door-music-install-n18/proof.json');assert p['status'].endswith('PASS')and p['engine_sha256']==i['engine_sha256'];gates['door-music-install-n18/proof.json']=sha(w/'door-music-install-n18/proof.json')
profile=read(pub/'ports/legacy-gui/PROFILE.json');assert profile['historical']and not profile['compatible_with_current_canonical_engine']
j=dict(status='DOOR_MUSIC_PUBLISHED_WORKSPACE_SEAL_PASS',at=datetime.now(timezone.utc).isoformat(),published_commit=commit,exe_sha256=pin,engine_sha256=i['engine_sha256'],framework_sha256=i['framework_sha256'],snapshot=str(snapshot),snapshot_manifest_sha256=sha(snapshot/'snapshot-manifest.json'),gates=gates,independent_source_clone_verified=True,user_installation_ignored=True,whole_game_completion_percent=None,fixed_acceptance=dict(passed=7,total=10,percent=70),limits=['Two exact shared door clips905/907 added to eleven reviewed identities','Unknown audio roles remain foreground; no all-effect or whole-game audiovisual claim','Header/core/60serialized payloads and original scene selector unchanged'])
(w/'door-music-seal-nov18.json').write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
current=read(o/'CURRENT-LOCAL-BUILD.json');current.update(status='VERIFIED_PUBLISHED_SHARED_DOOR_MUSIC',exe_sha256=pin,main_exe_sha256=pin,engine_sha256=i['engine_sha256'],source_snapshot=str(snapshot),publication_complete=True,source_publication_pending=False,published_commit=commit,last_published_commit=commit,last_published_exe_sha256=pin,seal_context='work/fresh-20260913/door-music-seal-nov18.json',integration_context='work/fresh-20260913/door-music-integration-nov18.json',local_continuation='work/fresh-20260913/SESSION-20261118-DOORS.md')
for key in ('publication_extension_context','source_profile_seal_context'):
    if key in current:current['historical_'+key]=current.pop(key)
(o/'CURRENT-LOCAL-BUILD.json').write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8');print(j['status'],commit)
