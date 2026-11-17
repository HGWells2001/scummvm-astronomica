"""Verify unchanged payload code and the two direct restored-Music registrations."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
parent=read(w/'effect-mix-seal-nov17.json');stage=w/'audio-restore-candidate-nov17-stage';build=read(stage/'proof.json');src=stage/'source/engines/astronomica'
before=(Path(parent['snapshot'])/'engine/astronomica/astronomica.cpp').read_text();after=(src/'astronomica.cpp').read_text()
tokens=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{}]')
def function(text,signature):
 assert text.count(signature)==1
 start=text.index(signature);depth=1
 for m in tokens.finditer(text,start+len(signature)):
  if m[0]=='{':depth+=1
  elif m[0]=='}':
   depth-=1
   if not depth:return text[start:m.end()]
 raise AssertionError('Unterminated method')
rows=[]
pattern=r'Common::Error\s+AstronomicaEngine::((?:save|load)\w+)\([^)]*\)\s*\{'
for match in re.finditer(pattern,before):
 old=function(before,match[0]);new=function(after,match[0]);assert old==new,match[1]
 rows.append(dict(method=match[1],unchanged_sha256=sha(old.encode())))
assert len(rows)==60
assert (src/'astronomica.h').read_bytes()==(Path(parent['snapshot'])/'engine/astronomica/astronomica.h').read_bytes()
for owner in ('out','p'):
 text='_mixer->playStream(Audio::Mixer::kMusicSoundType,&_soundHandle,'+owner+'.ambient);_musicHandle=_soundHandle;'
 assert after.count(text)==1
assert after.count('_musicHandle=_soundHandle;')==2
regression=read(w/'restored-music-owner-native-nov17/proof.json');fixed=read(w/'restored-music-owner-fixed-native-nov17/proof.json')
assert regression['status']=='RESTORED_MUSIC_OWNER_AND_BOOT_REGRESSIONS_REPRODUCED'and fixed['status']=='RESTORED_MUSIC_OWNER_FIXED_NATIVE_PASS'
assert fixed['candidate_exe_sha256']==build['candidate_exe_sha256']and fixed['fixture_sha256']==regression['fixture_sha256']
j=dict(status='AUDIO_RESTORE_PAYLOAD_AND_REGISTRATION_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=parent['exe_sha256'],payload_methods=rows,header_byte_identical=True,two_direct_music_registrations=True,regression_proof_sha256=sha((w/'restored-music-owner-native-nov17/proof.json').read_bytes()),fixed_proof_sha256=sha((w/'restored-music-owner-fixed-native-nov17/proof.json').read_bytes()),limits=['No payload/schema change; boot source and restored audio ownership intentionally change','One physical ASVM30 regression fixture; other native compatibility/general checks are separate'])
(w/'audio-restore-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'])
