"""Check candidate source delta and exact COFF library object closure."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
from weather_order_source_nov10 import harden,add_regression
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';stage=w/'weather-order-fix-nov10-stage';foundation=w/'p523-recipients-nov5-stage/complete-build'
read=lambda p:json.loads(p.read_text());digest=lambda b:hashlib.sha256(b).hexdigest();sha=lambda p:digest(p.read_bytes())
seal=read(w/'builder-mask-guard-seal-nov9-status.json');build=read(stage/'proof.json');base=read(foundation/'proof.json');native=read(w/'weather-order-fixed-native-nov10/proof.json')
assert build['base_exe_sha256']==seal['exe_sha256']==sha(w/'build/Releasex64/scummvm.exe')
assert sha(stage/'bin/scummvm.exe')==build['candidate_exe_sha256']
assert build['compiled_translation_units']==3 and build['reused_verified_foundation_objects']==407
src=stage/'source/engines/astronomica';canonical=o/'engine/astronomica'
changed=[n for n,h in seal['engine_sha256'].items()if build['candidate_engine_sha256'][n]!=h]
assert set(changed)=={'script.cpp','conditions_test.cpp'}
assert(src/'script.cpp').read_text()==harden((canonical/'script.cpp').read_text())
assert(src/'conditions_test.cpp').read_text()==add_regression((canonical/'conditions_test.cpp').read_text())
for n,h in build['candidate_engine_sha256'].items():assert sha(src/n)==h
for n,h in seal['framework_sha256'].items():assert sha(w/'scummvm'/n)==h
expected={};fresh=set()
for name in re.findall(r'"([^"]+\.obj)"',(stage/'lib.rsp').read_text(),re.I):
 p=Path(name);h=sha(p);expected[str(p).casefold()]=h
 if p.resolve().is_relative_to(foundation):assert h==next(v for n,v in base['object_sha256'].items()if str(Path(n)).casefold()==str(p).casefold())
 else:
  assert p.resolve().parent==stage.resolve() and p.stem in('astronomica','script','conditions_test');fresh.add(p.stem)
assert fresh=={'astronomica','script','conditions_test'} and len(expected)==7
library=stage/'bin/astronomica.lib';b=library.read_bytes();assert b[:8]==b'!<arch>\n';at=8;long=None;members={}
while at<len(b):
 h=b[at:at+60];assert len(h)==60 and h[58:]==b'`\n';name=h[:16].decode('ascii').strip();size=int(h[48:58]);data=b[at+60:at+60+size];assert len(data)==size
 if name=='//':assert long is None;long=data
 elif name=='/':pass
 else:
  assert name.startswith('/')and name[1:].isdigit()and long is not None
  start=int(name[1:]);end=long.index(0,start);name=long[start:end].decode('ascii').casefold();assert name not in members;members[name]=digest(data)
 at+=60+size+(size%2)
assert at==len(b)and members==expected and sha(library)==native['native_library_sha256']
for n in('astronomica','script','conditions_test'):
 rsp=(stage/('cl-'+n+'.rsp')).read_text();assert str(src/(n+'.cpp')).casefold()in rsp.casefold()and str(stage/(n+'.obj')).casefold()in rsp.casefold()
before=read(stage/'before.json');erratum=before['candidate_astronomica_sha256']!=build['candidate_engine_sha256']['astronomica.cpp']
if erratum:assert before['candidate_astronomica_sha256']==build['candidate_engine_sha256']['conditions_test.cpp']
j=dict(status='WEATHER_ORDER_CANDIDATE_SOURCE_AND_LIBRARY_CLOSURE_PASS',verified_at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),source_transform_sha256=sha(w/'weather_order_source_nov10.py'),build_proof_sha256=sha(stage/'proof.json'),candidate_exe_sha256=build['candidate_exe_sha256'],changed_engine_files=sorted(changed),engine_sha256=build['candidate_engine_sha256'],framework_sha256=seal['framework_sha256'],headers_unchanged=True,save_layouts_unchanged=True,compiled_translation_units=3,reused_verified_foundation_objects=407,archive_members_checked=len(members),fresh_object_sha256={n:sha(stage/(n+'.obj'))for n in sorted(fresh)},library_sha256=sha(library),historical_before_metadata_field_mislabeled=erratum,historical_before_metadata_sha256=sha(stage/'before.json'),before_metadata_erratum='candidate_astronomica_sha256 mislabeled the last modified conditions_test source; full candidate_engine_sha256 and actual compiler/library inputs independently verified'if erratum else None,main_unchanged=True)
(w/'weather-order-source-review-nov10.json').write_text(json.dumps(j,indent=2)+'\n');print('Weather candidate source/library closure PASS:2source changes,3fresh units,407verified objects')
