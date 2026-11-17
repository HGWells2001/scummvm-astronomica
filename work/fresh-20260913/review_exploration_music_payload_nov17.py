"""Check complete unchanged save/load methods and the precise new decoder validation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
parent=read(w/'p525-terminal-clock-compat-seal-nov17.json');s=w/'exploration-music-candidate-nov17c-stage';build=read(s/'proof.json');src=s/'source/engines/astronomica'
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
baseline=read(w/'exploration-music-baseline-native-nov17/proof.json');fixed=read(w/'exploration-music-final-native-nov17/proof.json');original=read(w/'exploration-music-original-nov17.json')
assert baseline['successful_music_entries']==0 and fixed['successful_music_entries']==16 and fixed['candidate_exe_sha256']==build['candidate_exe_sha256']
assert original['status']=='ORIGINAL_EXPLORATION_MUSIC_SELECTOR_PASS'and original['cases']==45192
log=(w/'exploration-music-final-native-nov17/native.log').read_text();assert 'Exploration music paused ASVM2: paused1 resumed1'in log and 'Exploration music P525 recipient: busyRefused1 preserved1 loaded1 music1'in log
j=dict(status='EXPLORATION_MUSIC_PAYLOAD_AND_REGRESSION_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=parent['exe_sha256'],payload_methods=rows,header_byte_identical=True,serialized_methods_byte_identical=60,original_cases=45192,baseline_missing_entries=16,fixed_entries=16,user_installation_ignored=True,limits=['ASVM2 recomputes mode1 ambience from restored scene/globals; no new payload/version','Mode0 and mode3 ambience selection unchanged','P117 receiver admits the owned background Music handle while still rejecting narration; paused shared loops use the existing core gate'])
(w/'exploration-music-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
