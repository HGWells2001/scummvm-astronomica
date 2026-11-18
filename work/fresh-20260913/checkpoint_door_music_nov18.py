"""Back up the reviewable fix while the qualified engine stays unchanged."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
parent=read(w/'source-download-launcher-seal-nov18.json');assert git('branch','--show-current')=='main' and not git('status','--porcelain') and git('rev-parse','HEAD')==git('ls-remote','origin','refs/heads/main').split()[0]==parent['published_commit']
assert read(w/'door-music-final-native-nov18/proof.json')['status']=='SHARED_DOOR_MUSIC_NATIVE_PASS'
items=['inventory_door_effects_nov18.py','door-effects-original-nov18.json','door_effect_source_nov18.py','door_effect_source_nov18b.py','build_door_music_baseline_nov18b.py','build_door_music_candidate_nov18b.py','check_door_music_nov18.py','check_door_music_general_nov18.py','check_door_music_genuine_nov18.py','audit_door_music_nov18.py','review_door_music_payload_nov18.py','checkpoint_door_music_nov18.py','door-music-candidate-nov18b-stage/proof.json','door-music-baseline-native-nov18b/proof.json','door-music-final-native-nov18/proof.json','door-music-windows-native-nov18/proof.json','door-music-source-review-nov18.json','door-music-payload-review-nov18.json']
git('switch','-c','codex/shared-door-music-nov18');names=[]
for n in items:
    name='work/fresh-20260913/'+n;dest=pub/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(w/n,dest);names.append(name)
name='outputs/astronomica-cleanroom/DOOR-MUSIC-WIP.md';(pub/name).write_text('''# Shared door effects — candidate qualification

Original P27 door playback uses shared905;P85 uses shared907. Exact assets occur in19 original command references. The candidate classifies those two reviewed identities as effects over Music, preserving its owner and elapsed position. Voice and unknown clips retain foreground handling.

Causal native P27/P85 clicks reproduce the restart before the fix and preserve Music afterwards. Windows/WASAPI and unchanged header/core/60serialized-method audits pass. General and previous-save qualification must finish naturally before production integration. The branch currently retains the previous qualified engine; helper source reconstructs the candidate from that pinned parent. Candidate executable is not distributed.

No complete sound-role catalogue or whole-game percentage is claimed. Fixed acceptance remains7/10. Personal installation excluded.
''',encoding='utf-8');names.append(name)
m=read(pub/'SOURCE-MANIFEST.json');files=set(m['sha256'])|set(names);m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True);git('-c','core.whitespace=cr-at-eol','diff','--check');git('add','--',*names,'SOURCE-MANIFEST.json');git('commit','-m','Back up reviewed shared door music fix pending full qualification');git('push','-u','origin','codex/shared-door-music-nov18');commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/codex/shared-door-music-nov18').split()[0]==commit
(w/'door-music-wip-backup-nov18.json').write_text(json.dumps(dict(status='DOOR_MUSIC_WIP_SOURCE_BACKUP_PASS',at=datetime.now(timezone.utc).isoformat(),commit=commit,parent_main=parent['published_commit'],main_engine_unchanged=True),indent=2)+'\n');print('DOOR_MUSIC_WIP_SOURCE_BACKUP_PASS',commit)
