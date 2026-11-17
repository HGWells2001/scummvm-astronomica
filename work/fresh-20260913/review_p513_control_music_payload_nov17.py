"""Check complete unchanged save/load methods and the precise new decoder validation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
parent=read(w/'p504-control-music-seal-nov17.json');s=w/'p513-control-music-candidate-nov17-stage';build=read(s/'proof.json');src=s/'source/engines/astronomica'
before=(Path(parent['snapshot'])/'engine/astronomica/astronomica.cpp').read_text();after=(src/'astronomica.cpp').read_text()
tokens=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{}]')
def function(text,signature):
 assert text.count(signature)==1;start=text.index(signature);depth=1
 for m in tokens.finditer(text,start+len(signature)):
  if m[0]=='{':depth+=1
  elif m[0]=='}':
   depth-=1
   if not depth:return text[start:m.end()]
 raise AssertionError('Unterminated method')
rows=[]
for m in re.finditer(r'Common::Error\s+AstronomicaEngine::((?:save|load)\w+)\([^)]*\)\s*\{',before):
 old=function(before,m[0]);new=function(after,m[0]);assert old==new,m[1];rows.append(dict(method=m[1],unchanged_sha256=sha(old.encode())))
assert len(rows)==60 and (src/'astronomica.h').read_bytes()==(Path(parent['snapshot'])/'engine/astronomica/astronomica.h').read_bytes()
baseline=read(w/'p513-control-music-baseline-native-nov17/proof.json');fixed=read(w/'p513-control-music-final-native-nov17/proof.json')
assert [r['music']for r in baseline['cases']]==[0,0] and [r['music']for r in fixed['cases']]==[1,1] and fixed['candidate_exe_sha256']==build['candidate_exe_sha256']
assert [r['setting']for r in baseline['cases']]==[r['setting']for r in fixed['cases']]==[6,4]
signature='static int originalSceneAmbient(int mode,int place,int32 state){'
assert function(before,signature)==function(after,signature)
start=after.index('bool AstronomicaEngine::isFeedbackEffect(int id) const {');end=after.index('void AstronomicaEngine::synchronizeMusicHandle()',start)
assert after[start:end].count('if(universeFileIdentity(')==11
j=dict(status='P513_CONTROL_MUSIC_PAYLOAD_AND_REGRESSION_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=parent['exe_sha256'],payload_methods=rows,header_byte_identical=True,serialized_methods_byte_identical=60,scene_selector_byte_identical=True,exact_effect_clip_identities=11,user_installation_ignored=True,limits=['Two exact original P513 numeric-selector clips added; other unclassified roles remain foreground','Actual original controls retain Music; no save-schema or scene-selector change'])
(w/'p513-control-music-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
