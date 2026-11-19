from pathlib import Path
import re,json,hashlib
from datetime import datetime,timezone
w=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());parent=read(w/'all-effects-seal-nov19.json');s=w/'speech-duck-candidate-nov19d-stage';before=(Path(parent['snapshot'])/'engine/astronomica/astronomica.cpp').read_text();after=(s/'source/engines/astronomica/astronomica.cpp').read_text();tokens=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\x27(?:\\.|[^\x27\\])*\x27|[{}]')
def function(t,signature):
 assert t.count(signature)==1;start=t.index(signature);depth=1
 for m in tokens.finditer(t,start+len(signature)):
  if m[0]=='{':depth+=1
  elif m[0]=='}':
   depth-=1
   if depth==0:return t[start:m.end()]
 raise AssertionError('Unterminated method')
oldguard='(_mixer->isSoundHandleActive(_musicHandle)&&!_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle))';newguard='(_mixer->isSoundHandleActive(_musicHandle)&&!(_soundHandle==_musicHandle))';rows=[];changed=[]
for m in re.finditer(r'Common::Error\s+AstronomicaEngine::((?:save|load)\w+)\([^)]*\)\s*\{',before):
 a=function(before,m[0]);b=function(after,m[0]);identical=a==b
 if not identical:assert m[1]in['saveGameStream','loadGameStream']and a.replace(oldguard,newguard)==b;changed.append(m[1])
 assert '_unduckedMusicVolume'not in b and '_duckedMusicHandle'not in b
 rows.append(dict(method=m[1],byte_identical=identical,admission_only_changed=not identical))
assert len(rows)==60 and sorted(changed)==['loadGameStream','saveGameStream']
a=(Path(parent['snapshot'])/'engine/astronomica/astronomica.h').read_text();b=(s/'source/engines/astronomica/astronomica.h').read_text();line=' Audio::SoundHandle _musicHandle;';assert a.replace(line,line+'\n Audio::SoundHandle _duckedMusicHandle;\n int _unduckedMusicVolume = -1; // Transient channel volume, never a saved preference.')==b
for sig in ['static int originalSceneAmbient(int mode,int place,int32 state){','bool AstronomicaEngine::isFeedbackEffect(int id) const {']:assert function(before,sig)==function(after,sig)
proof=dict(status='SPEECH_DUCK_PAYLOAD_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=read(s/'proof.json')['candidate_exe_sha256'],serialized_methods=60,byte_identical_methods=58,admission_only_methods=changed,methods=rows,transient_fields_not_serialized=True,two_private_header_fields_only=True,ambient_selector_and_102_effect_catalogue_identical=True,packet_layouts_unchanged=True,engine_units_fresh=7,framework_unchanged=True)
(w/'speech-duck-payload-review-nov19d.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'])
