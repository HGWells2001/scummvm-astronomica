"""Back up the complete release procedure before the requested quota reserve."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'));git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
assert git('branch','--show-current')=='codex/shared-door-music-nov18'and not git('status','--porcelain')
assert git('ls-remote','origin','refs/heads/main').split()[0]==read(w/'source-download-launcher-seal-nov18.json')['published_commit']
items=['promote_door_music_nov18.py','prepare_door_music_publication_nov18.py','check_door_music_publication_install_nov18.py','publish_door_music_nov18.py','seal_door_music_nov18.py','finish_door_music_release_nov18.py','update_downloaded_door_runtime_nov18.py','open_corrected_p27_player_nov18.py','checkpoint_door_release_helpers_nov18.py']
names=[]
for n in items:
    name='work/fresh-20260913/'+n;dest=pub/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(w/n,dest);names.append(name)
m=read(pub/'SOURCE-MANIFEST.json');files=set(m['sha256'])|set(names);m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True);git('-c','core.whitespace=cr-at-eol','diff','--check');git('add','--',*names,'SOURCE-MANIFEST.json');git('commit','-m','Back up gated door release and isolated runtime delivery');git('push','origin','codex/shared-door-music-nov18');commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/codex/shared-door-music-nov18').split()[0]==commit
(w/'door-music-pre-release-backup-nov18.json').write_text(json.dumps(dict(status='DOOR_MUSIC_RELEASE_HELPERS_BACKUP_PASS',at=datetime.now(timezone.utc).isoformat(),commit=commit,main_engine_unchanged=True),indent=2)+'\n',encoding='utf-8');print('DOOR_MUSIC_RELEASE_HELPERS_BACKUP_PASS',commit)
