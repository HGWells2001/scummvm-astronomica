"""Check every COFF archive member against actual verified engine build objects."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());digest=lambda b:hashlib.sha256(b).hexdigest();sha=lambda p:digest(p.read_bytes())
stage=w/'builder-mask-guard-nov9-stage';foundation=w/'p523-recipients-nov5-stage/complete-build'
build=read(stage/'proof.json');base=read(foundation/'proof.json');seal=read(w/'builder-mask-guard-seal-nov9-status.json');positive=read(w/'original-scalar-queue-native-nov9b/proof.json')
assert build['candidate_exe_sha256']==seal['exe_sha256']==positive['installed_main_exe_sha256']==sha(w/'build/Releasex64/scummvm.exe')
assert build['candidate_engine_sha256']==seal['engine_sha256']
expected={};rsp=stage/'lib.rsp'
for name in re.findall(r'"([^"]+\.obj)"',rsp.read_text(),re.I):
 p=Path(name);h=sha(p);expected[str(p).casefold()]=h
 if p.resolve().is_relative_to(foundation):
  assert h==next(v for n,v in base['object_sha256'].items() if str(Path(n)).casefold()==str(p).casefold())
 else:assert p.resolve()==(stage/'astronomica.obj').resolve()
assert len(expected)==7
library=stage/'bin/astronomica.lib';b=library.read_bytes();assert b[:8]==b'!<arch>\n';at=8;long=None;members={}
while at<len(b):
 header=b[at:at+60];assert len(header)==60 and header[58:]==b'`\n';name=header[:16].decode('ascii').strip();size=int(header[48:58]);data=b[at+60:at+60+size];assert len(data)==size
 if name=='//':assert long is None;long=data
 elif name=='/':pass
 else:
  assert name.startswith('/') and name[1:].isdigit() and long is not None
  offset=int(name[1:]);end=long.index(0,offset);name=long[offset:end].decode('ascii').casefold();assert name not in members
  members[name]=digest(data)
 at+=60+size+(size%2)
assert at==len(b) and members==expected
assert base['engine_sha256']['script.cpp']==seal['engine_sha256']['script.cpp']
assert sha(w/'scummvm/engines/astronomica/script.cpp')==base['engine_sha256']['script.cpp']
link=w/'original-scalar-queue-native-nov9b/link.rsp';text=link.read_text();assert str(library).casefold() in text.casefold()
j=dict(status='SCALAR_QUEUE_REAL_ENGINE_LIBRARY_OBJECT_CLOSURE_PASS',verified_at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),engine_build_proof_sha256=sha(stage/'proof.json'),foundation_proof_sha256=sha(foundation/'proof.json'),native_proof_sha256=sha(w/'original-scalar-queue-native-nov9b/proof.json'),library_sha256=sha(library),library_rsp_sha256=sha(rsp),helper_link_rsp_sha256=sha(link),archive_members_checked=len(members),fresh_astronomica_object_sha256=sha(stage/'astronomica.obj'),script_runner_source_sha256=base['engine_sha256']['script.cpp'],members={Path(n).name:h for n,h in members.items()},installed_main_sha256=seal['exe_sha256'],limits=['Exact archive contents and current link response, not a new full compiler rebuild','Foundation build provenance retained in its original input manifest'])
(w/'scalar-queue-library-audit-nov9.json').write_text(json.dumps(j,indent=2)+'\n');print('Scalar queue native engine library closure PASS:',len(members),'exact build objects')
