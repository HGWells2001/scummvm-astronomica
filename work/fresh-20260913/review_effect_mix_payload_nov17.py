"""Independently bind the eight audio identities and unchanged save payload methods."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
old=read(w/'startup-logo-seal-nov16.json');stage=w/'effect-mix-candidate-nov17-stage';build=read(stage/'proof.json');src=stage/'source/engines/astronomica'
before=(Path(old['snapshot'])/'engine/astronomica/astronomica.cpp').read_text();after=(src/'astronomica.cpp').read_text()
assert sha((src/'astronomica.cpp').read_bytes())==build['candidate_engine_sha256']['astronomica.cpp']
tokens=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{}]')
def function(text,signature):
 assert text.count(signature)==1
 start=text.index(signature);depth=1
 for m in tokens.finditer(text,start+len(signature)):
  if m[0]=='{':depth+=1
  elif m[0]=='}':
   depth-=1
   if depth==0:return text[start:m.end()]
 raise AssertionError('Unterminated method')
pattern=r'Common::Error\s+AstronomicaEngine::((?:save|load)\w+)\([^)]*\)\s*\{'
parents=list(re.finditer(pattern,before));candidates=list(re.finditer(pattern,after));assert len(parents)==len(candidates)>=30
rows=[]
for p in parents:
 signature=p[0];name=p[1];parent=function(before,signature);candidate=function(after,signature)
 if name in ('saveGameStream','loadGameStream'):
  guard='\n if(_mixer->isSoundHandleActive(_effectHandle)||(_mixer->isSoundHandleActive(_musicHandle)&&!_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle)))return Common::kReadingFailed;'
  assert candidate.startswith(signature+guard);candidate=candidate.replace(signature+guard,signature,1)
 assert parent==candidate,name
 rows.append(dict(method=name,parent_and_normalized_candidate_sha256=sha(parent.encode())))
roles={}
for n in (2,3,4,5):
 path=Path('D:/astro/PLACES/P517/S%d.WAV'%n);data=path.read_bytes();digest=sha(data)
 assert read(w/'feedback-audio-inventory-nov16.json')['references'][digest]==n
 roles[digest]=dict(path=str(path),bytes=len(data))
for row in read(w/'control-effects-inventory-nov17.json')['controls']:
 path=Path('D:/astro')/row['audio_path'];data=path.read_bytes();assert sha(data)==row['audio_sha256']
 assert sha((Path('D:/astro/PLACES/P%d/MEGAFILE.HYP'%row['scene'])).read_bytes())==row['megafile_sha256']
 roles[sha(data)]=dict(path=str(path),bytes=len(data))
assert len(roles)==8;expected=set()
for row in roles.values():
 h=2166136261
 for v in Path(row['path']).read_bytes():h=((h^v)*16777619)&0xffffffff
 expected.add((row['bytes'],h))
role_method=function(after,'bool AstronomicaEngine::isFeedbackEffect(int id) const {')
actual={(int(a),int(b,16))for a,b in re.findall(r'universeFileIdentity\(path,(\d+)U,0x([0-9a-f]+)U\)',role_method)};assert actual==expected
old_header=(Path(old['snapshot'])/'engine/astronomica/astronomica.h').read_text();new_header=(src/'astronomica.h').read_text()
handles=lambda text:set(re.findall(r'Audio::SoundHandle\s+(_\w+);',text))
assert handles(new_header)-handles(old_header)=={'_effectHandle','_musicHandle'}
j=dict(status='EFFECT_MIX_AUDIO_ROLES_AND_SAVE_PAYLOAD_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=old['exe_sha256'],stream_methods=rows,audio_roles=roles,additional_transient_handles=['_effectHandle','_musicHandle'],save_payload_methods_unchanged=True,limits=['Only two early stream guards removed for source comparison; all other complete save/load methods byte-identical','Class layout changes, so all engine units must be rebuilt','Role catalogue covers eight exact identities, not every effect or voice','Mixer ownership/timing behavior intentionally changes; native compatibility tests remain separate'])
(w/'effect-mix-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'],len(rows),'methods')
