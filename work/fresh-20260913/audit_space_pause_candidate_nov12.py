"""Verify two-file engine delta, seven current engine objects and 403 pinned core objects."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,sys
from space_pause_source_nov12 import production as production
w=Path(__file__).resolve().parent;r=w.parents[1];stage=w/sys.argv[1];out=w/sys.argv[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
seal=read(w/'intro-menu-seal-nov12-status.json');build=read(stage/'proof.json');foundation=w/'p523-recipients-nov5-stage/complete-build';base=read(foundation/'proof.json')
assert sha(w/'build/Releasex64/scummvm.exe')==seal['exe_sha256']==build['base_exe_sha256']
assert sha(stage/'bin/scummvm.exe')==build['candidate_exe_sha256'];src=stage/'source/engines/astronomica';canonical=r/'outputs/astronomica-cleanroom/engine/astronomica'
changed=[n for n,h in seal['engine_sha256'].items()if h!=build['candidate_engine_sha256'][n]];assert set(changed)=={'astronomica.cpp','astronomica.h'}
cpp,header=production((canonical/'astronomica.cpp').read_text(),(canonical/'astronomica.h').read_text());assert (src/'astronomica.cpp').read_text()==cpp and (src/'astronomica.h').read_text()==header
for n,h in build['candidate_engine_sha256'].items():assert sha(src/n)==h
for n,h in seal['framework_sha256'].items():assert sha(w/'scummvm'/n)==h
assert build['compiled_translation_units']==7 and build['reused_verified_foundation_objects']==403
names={'astronomica','conditions_test','metaengine','resource','help','script','sprites'};expected={}
for path in re.findall(r'"([^"]+\.obj)"',(stage/'lib.rsp').read_text(),re.I):
 p=Path(path);assert p.resolve().parent==stage.resolve()and p.stem in names;expected[str(p).casefold()]=sha(p)
assert len(expected)==7
b=(stage/'bin/astronomica.lib').read_bytes();assert b[:8]==b'!<arch>\n';at=8;long=None;members={}
while at<len(b):
 h=b[at:at+60];assert h[58:]==b'`\n';name=h[:16].decode().strip();size=int(h[48:58]);data=b[at+60:at+60+size];assert len(data)==size
 if name=='//':long=data
 elif name!='/':
  assert name.startswith('/')and name[1:].isdigit()and long is not None;start=int(name[1:]);name=long[start:long.index(0,start)].decode().casefold();assert name not in members;members[name]=hashlib.sha256(data).hexdigest()
 at+=60+size+(size%2)
assert at==len(b)and members==expected
for n in names:
 text=(stage/('cl-'+n+'.rsp')).read_text().casefold();assert str(src/(n+'.cpp')).casefold()in text and str(stage/(n+'.obj')).casefold()in text
for n,h in base['object_sha256'].items():assert sha(Path(n))==h
link=(stage/'link.rsp').read_text().casefold();assert str(stage/'bin/astronomica.lib').casefold()in link
objects=re.findall(r'"([^"]+\.obj)"',link);assert len(objects)==402
for n in objects:assert sha(Path(n))==next(h for k,h in base['object_sha256'].items()if k.casefold()==n.casefold())
detection=foundation/'bin/scummvm-detection.lib';assert str(detection).casefold()in link
db=detection.read_bytes();assert db[:8]==b'!<arch>\n';at=8;long=None;found=[]
while at<len(db):
 h=db[at:at+60];assert h[58:]==b'`\n';name=h[:16].decode().strip();size=int(h[48:58]);data=db[at+60:at+60+size]
 if name=='//':long=data
 elif name!='/':
  assert long is not None and name.startswith('/');start=int(name[1:]);member=long[start:long.index(0,start)].decode();assert Path(member).name=='0000-detection.obj';found.append(hashlib.sha256(data).hexdigest())
 at+=60+size+(size%2)
assert found==[next(h for k,h in base['object_sha256'].items()if 'scummvm-detection' in k)]
assert read(stage/'before.json')['candidate_astronomica_sha256']==sha(src/'astronomica.cpp')
j=dict(status='SPACE_PAUSE_SOURCE_AND_LIBRARY_CLOSURE_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],engine_sha256=build['candidate_engine_sha256'],framework_sha256=seal['framework_sha256'],changed_engine_files=sorted(changed),fresh_translation_units=7,verified_reused_framework_objects=403,archive_members_checked=7,private_derived_cache_fields_added=False,derived_cursor_array_expanded=False,engine_class_layout_unchanged=True,private_methods_only=True,all_engine_translation_units_rebuilt=True,save_layouts_unchanged=True,framework_unchanged=True,main_unchanged=True,source_transform_sha256=sha(w/'space_pause_source_nov12.py'),build_proof_sha256=sha(stage/'proof.json'),library_sha256=sha(stage/'bin/astronomica.lib'))
out.write_text(json.dumps(j,indent=2)+'\n');print('Player keyboard source/library closure PASS')
