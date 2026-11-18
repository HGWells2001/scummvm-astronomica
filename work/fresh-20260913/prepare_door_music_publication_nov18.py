"""Prepare the qualified paired source export; publication follows clean installer validation."""
from pathlib import Path
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';pub=r/'publish/scummvm-astronomica';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
i=read(w/'door-music-integration-nov18.json');pin=i['candidate_exe_sha256'];assert sha(w/'build/Releasex64/scummvm.exe')==pin
assert git('branch','--show-current')=='codex/shared-door-music-nov18' and not git('status','--porcelain')
assert git('ls-remote','origin','refs/heads/main').split()[0]==read(w/'source-download-launcher-seal-nov18.json')['published_commit']
for n,key in [('door-music-installed-native-nov18/proof.json','candidate_exe_sha256'),('door-music-main-genuine-nov18/proof.json','consumer_exe_sha256')]:assert read(w/n)['status'].endswith('PASS') and read(w/n)[key]==pin
names=[]
def copy(source,name):
    dest=pub/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);names.append(name)
for n,h in i['engine_sha256'].items():assert sha(o/'engine/astronomica'/n)==h;copy(o/'engine/astronomica'/n,'outputs/astronomica-cleanroom/engine/astronomica/'+n)
copy(Path(i['snapshot'])/'framework-patch.json','framework-patch.json')
b=read(pub/'SCUMMVM_BASE.json');b.update(validated_executable_sha256=pin,engine_sha256=i['engine_sha256'],build_scope='Thirteen exact feedback identities, including shared door905/907. Actual P27/P85 clicks preserve Music owner and position; narration remains foreground. Header,three core files,sixty serialized save/load methods and scene selector unchanged. General,Windows,prior-save,regional,close-up and control regression gates pass.');(pub/'SCUMMVM_BASE.json').write_text(json.dumps(b,indent=2)+'\n',encoding='utf-8')
extras=['promote_door_music_nov18.py','prepare_door_music_publication_nov18.py','check_door_music_publication_install_nov18.py','publish_door_music_nov18.py','seal_door_music_nov18.py','finish_door_music_release_nov18.py','update_downloaded_door_runtime_nov18.py','door-music-installed-native-nov18/proof.json','door-music-main-genuine-nov18/proof.json']
for n in sorted(set(i['gates'])|set(extras)):copy(w/n,'work/fresh-20260913/'+n)
doc='''# Shared door effects preserve Music

The original P27 opening sound uses shared905; P85's door control uses shared907. Their exact files are referenced by19 original commands. Both are now reviewed effects over the existing Music stream. The first P27 click opens the door and the second enters P32 while retaining the same regional Music owner. Unknown recordings, explicit introductions and blocking/movie sounds retain foreground handling. Narration still suspends Music.

Causal before/after tests use the original hit-tested P27 sprite and P85 rectangle, controlled initial state and WASAPI. Before the fix each effect replaces Music and restarts it. Afterward the same Music handle advances through the effect, with exactly one sound start and guarded transient save/load. Windows checks and existing regional,close-up,ASVM2/pause,narration,P504 and P513 control regressions pass. The exact full general suite and genuine pre-fix ASVM29 continuations pass before integration.

All seven engine units were built freshly against403 verified unchanged core objects. Only astronomica.cpp changes; the engine header,three core files,sixty serialized save/load method bodies and original scene-music selector remain unchanged. Installed native and previous-save checks pass. Source installation and independent-clone validation are required before final publication.

This adds two exact identities to the eleven already reviewed; it is not an automatic classification of every sound. Original assets, executable binaries and physical save fixtures are not published. Personal installation is excluded. All qualification processes finish naturally. Fixed acceptance remains7/10; total project completion is unmeasured.
'''
(o/'DOOR-MUSIC.md').write_text(doc,encoding='utf-8');copy(o/'DOOR-MUSIC.md','outputs/astronomica-cleanroom/DOOR-MUSIC.md')
intro=b'# Current update: doors preserve music\n\nP27/P85 shared door effects now overlap the same advancing Music stream. Narration retains foreground handling. See outputs/astronomica-cleanroom/DOOR-MUSIC.md for the exact scope. All earlier checkpoints below are historical.\n\n---\n\n'
p=pub/'README.md';data=p.read_bytes();before,after=data.split(b'---\n\n',1);p.write_bytes(before+b'---\n\n'+intro+after)
p=pub/'outputs/astronomica-cleanroom/NEXT-STEPS.md';p.write_bytes(intro+p.read_bytes());shutil.copyfile(p,o/'NEXT-STEPS.md')
p=pub/'outputs/astronomica-cleanroom/DOOR-MUSIC-WIP.md';p.write_bytes(b'Historical candidate notes. See DOOR-MUSIC.md for the qualified engine.\n\n'+p.read_bytes())
session='''# 18 November — shared door effects

The physical candidate and installed engine use shared905/907 as reviewed effects over Music. Parent F is p513-control-music-seal-nov17.json; all later source-only extensions, including November18 navigation evidence, are retained. Continue from door-music-seal-nov18.json and CURRENT-LOCAL-BUILD.json after release completion. The exact full general suite,causal Windows door checks,old ASVM29 continuations,regional/close-up and P504/P513 regressions pass. No fields,core or save payload change.

Next work: other unclassified effects need explicit role evidence; do not mix every localS1 or every short file. A03 full behavioral reachability,A08 typography and A09 recorded full manual audiovisual playthrough remain open. Whole-project completion unmeasured; fixed acceptance7/10.

Latest user explicitly authorizes forced application closure and shutdown at the1percent quota reserve after saving/GitHub and natural suite completion. Use only the fresh November18 authorization; never reuse the executed November17 record. Ignore personal installation D:/00/_SCUMMVM_PORTATILE. The specifically identified downloaded source folder may receive the qualified runtime separately,preserving settings/saves. No reset credit redemption or purchases.
'''
(w/'SESSION-20261118-DOORS.md').write_text(session,encoding='utf-8');copy(w/'SESSION-20261118-DOORS.md','work/fresh-20260913/SESSION-20261118-DOORS.md')
m=read(pub/'SOURCE-MANIFEST.json');files=set(m['sha256'])|set(names);assert set(git('ls-files','--others','--exclude-standard').splitlines())<=files;m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True);git('-c','core.whitespace=cr-at-eol','diff','--check');print('DOOR_MUSIC_SOURCE_EXPORT_PREPARED')
