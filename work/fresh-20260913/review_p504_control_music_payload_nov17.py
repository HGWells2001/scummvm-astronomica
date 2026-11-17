"""Check complete unchanged save/load methods and the precise new decoder validation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
parent=read(w/'scene-music-seal-nov17.json');s=w/'p504-control-music-candidate-nov17b-stage';build=read(s/'proof.json');src=s/'source/engines/astronomica'
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
baseline=read(w/'p504-control-music-baseline-native-nov17b/proof.json');fixed=read(w/'p504-control-music-final-native-nov17b/proof.json')
assert baseline['values']['music']==0 and fixed['values']['music']==1 and fixed['candidate_exe_sha256']==build['candidate_exe_sha256']
assert baseline['values']['setting']==fixed['values']['setting']==1 and baseline['values']['starts']==fixed['values']['starts']==1
signature='static int originalSceneAmbient(int mode,int place,int32 state){'
assert function(before,signature)==function(after,signature)
start=after.index('bool AstronomicaEngine::isFeedbackEffect(int id) const {');end=after.index('void AstronomicaEngine::synchronizeMusicHandle()',start)
assert after[start:end].count('if(universeFileIdentity(')==9
j=dict(status='P504_CONTROL_MUSIC_PAYLOAD_AND_REGRESSION_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=parent['exe_sha256'],payload_methods=rows,header_byte_identical=True,serialized_methods_byte_identical=60,scene_selector_byte_identical=True,exact_effect_clip_identities=9,user_installation_ignored=True,limits=['Only exact original P504 speed-step clip added; other unclassified roles remain foreground','Actual original control preserves same Music handle; no change to save schemas or scene-music selector'])
(w/'p504-control-music-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
