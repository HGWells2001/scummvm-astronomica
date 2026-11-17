"""Check complete unchanged save/load methods and the precise new decoder validation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
parent=read(w/'exploration-music-seal-nov17.json');s=w/'scene-music-candidate-nov17-stage';build=read(s/'proof.json');src=s/'source/engines/astronomica'
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
baseline=read(w/'scene-music-baseline-native-nov17/proof.json');fixed=read(w/'scene-music-final-native-nov17/proof.json');original=read(w/'exploration-music-original-nov17.json')
assert baseline['matched']==6 and fixed['matched']==18 and fixed['candidate_exe_sha256']==build['candidate_exe_sha256']
assert original['status']=='ORIGINAL_EXPLORATION_MUSIC_SELECTOR_PASS' and original['cases']==45192
assert fixed['current_and_legacy_menu_music_recipients'] and fixed['narration_rejected_without_mutation']
j=dict(status='SCENE_MUSIC_PAYLOAD_AND_REGRESSION_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=parent['exe_sha256'],payload_methods=rows,header_byte_identical=True,serialized_methods_byte_identical=60,original_cases=45192,baseline_entries=6,fixed_entries=18,user_installation_ignored=True,limits=['Complete original selector for modes0,1,3; actual native sample covers nine scenes at two state values','Old local P1 music recipient remains accepted alongside original shared901; narration still refused'])
(w/'scene-music-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
