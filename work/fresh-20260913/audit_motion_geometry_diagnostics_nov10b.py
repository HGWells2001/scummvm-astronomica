"""Bind graph/menu observations to the exact shipping production sources and fresh archives."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
from motion_geometry_cache_source_nov10b import production,trace
w=Path(__file__).resolve().parent;r=w.parents[1];canonical=r/'outputs/astronomica-cleanroom/engine/astronomica'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
base=read(w/'hit-geometry-cache-seal-nov10b-status.json');shipping=read(w/'motion-geometry-cache-nov10b-stage/proof.json')
cpp=(canonical/'astronomica.cpp').read_text();header=(canonical/'astronomica.h').read_text();script=(canonical/'script.cpp').read_text()
rows=[]
for name,expected_cpp,expected_header,expected_script in [('motion-geometry-baseline-probe-nov10b-stage',trace(cpp),header,script),('motion-geometry-cached-probe-nov10b-stage',trace(production(cpp)),header,script)]:
 stage=w/name;b=read(stage/'proof.json');src=stage/'source/engines/astronomica';assert sha(stage/'bin/scummvm.exe')==b['candidate_exe_sha256']
 assert(src/'astronomica.cpp').read_text()==expected_cpp and(src/'astronomica.h').read_text()==expected_header and(src/'script.cpp').read_text()==expected_script
 for n,h in b['candidate_engine_sha256'].items():
  assert sha(src/n)==h
  if n not in('astronomica.cpp','astronomica.h','script.cpp'):assert h==base['engine_sha256'][n]
 expected={str(Path(n)).casefold():sha(Path(n))for n in re.findall(r'"([^"]+\.obj)"',(stage/'lib.rsp').read_text(),re.I)};assert len(expected)==7
 for n in expected:assert Path(n).resolve().parent==stage.resolve()
 data=(stage/'bin/astronomica.lib').read_bytes();assert data[:8]==b'!<arch>\n';at=8;long=None;members={}
 while at<len(data):
  h=data[at:at+60];assert h[58:]==b'`\n';n=h[:16].decode().strip();size=int(h[48:58]);payload=data[at+60:at+60+size]
  if n=='//':long=payload
  elif n!='/':
   assert long is not None and n.startswith('/');start=int(n[1:]);n=long[start:long.index(0,start)].decode().casefold();assert n not in members;members[n]=hashlib.sha256(payload).hexdigest()
  at+=60+size+(size%2)
 assert at==len(data)and members==expected
 for unit in('astronomica','conditions_test','metaengine','resource','help','script','sprites'):
  rsp=(stage/('cl-'+unit+'.rsp')).read_text().casefold();assert str(src/(unit+'.cpp')).casefold()in rsp and str(stage/(unit+'.obj')).casefold()in rsp
 assert str(stage/'bin/astronomica.lib').casefold()in(stage/'link.rsp').read_text().casefold()
 rows.append(dict(stage=name,exe_sha256=b['candidate_exe_sha256'],engine_sha256=b['candidate_engine_sha256'],library_sha256=sha(stage/'bin/astronomica.lib'),archive_members=7,exact_production_and_instrumentation_source=True))
for n,h in read(w/'p523-recipients-nov5-stage/complete-build/proof.json')['object_sha256'].items():assert sha(Path(n))==h
j=dict(status='MOTION_GEOMETRY_DIAGNOSTIC_SOURCE_PAIRS_PASS',verified_at=datetime.now(timezone.utc).isoformat(),shipping_exe_sha256=shipping['candidate_exe_sha256'],source_transform_sha256=sha(w/'motion_geometry_cache_source_nov10b.py'),diagnostics=rows,limits=['Diagnostic-only flags add observation code; shipping binary itself is validated by its separate native/general/physical-file gates','All seven engine units fresh in each diagnostic archive; framework source pair unchanged'])
(w/'motion-geometry-cache-diagnostic-source-review-nov10b.json').write_text(json.dumps(j,indent=2)+'\n');print('Two motion diagnostic archives share exact expected production/instrumentation sources')
