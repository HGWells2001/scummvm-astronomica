from pathlib import Path
import json,hashlib,collections,re,struct
w=Path('work/fresh-20260913');root=Path('D:/astro');rows=json.loads((w/'audio-acoustic-survey-nov19/results.json').read_text());inv=json.loads((w/'original-branches-nov6/inventory.json').read_text());modes={x['scene']:x['mode']for x in inv['scenes']}
voices={'PLACES/P408/S1.WAV','PLACES/P501/S11.WAV','PLACES/P501/S12.WAV','PLACES/P505/S12.WAV','PLACES/P505/S13.WAV','PLACES/P505/S14.WAV','PLACES/P512/S11.WAV','PLACES/P521/S12.WAV','PLACES/P521/S14.WAV'}
def background(path):
 if path in [f'SOUNDS/S{n}.WAV'for n in(0,1,2,3,8)]:return True
 m=re.fullmatch(r'PLACES/P(\d+)/S0.WAV',path)
 return m and modes[int(m[1])]==0 and int(m[1])not in(1,422)
def fnv(b):
 h=2166136261
 for v in b:h=((h^v)*16777619)&0xffffffff
 return h
catalogue=[]
for x in rows:
 role='speech' if x['speech_score']>=.5 or any(p in voices for p in x['paths']) else ('music' if any(background(p)for p in x['paths'])else'effect')
 b=(root/x['paths'][0]).read_bytes();catalogue.append(dict(sha256=x['sha256'],bytes=len(b),fnv1a=fnv(b),paths=x['paths'],role=role,evidence='acoustic models plus original scene/loop metadata; ambiguous vocal clips retain foreground',speech_score=x['speech_score'],top_acoustic_labels=x['top_labels'][:3]))
known=[(int(size),int(h,16)) for size,h in re.findall(r'universeFileIdentity\(path,(\d+)U,0x([0-9a-f]+)U\)',Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp').read_text())]+[(4860,0xc3345983),(5878,0xb1c8c30b)]
effects={(x['bytes'],x['fnv1a'])for x in catalogue if x['role']=='effect'};assert set(known)<=effects,(set(known)-effects)
proof=dict(status='ORIGINAL_AUDIO_ROLE_CATALOGUE_REVIEWED',files=sum(len(x['paths'])for x in catalogue),unique=len(catalogue),counts=dict(collections.Counter(x['role']for x in catalogue)),clips=catalogue,models=json.loads((w/'audio-acoustic-survey-nov19/models.json').read_text()),limits=['Machine-assisted acoustic classification plus source/resource review,not a human listening review of every clip','No inference models run in the engine;exact original file identities only','Ambiguous speech/vocalizations remain foreground;music is separated using original ambient selectors','Whisper first-token no-speech survey rejected:English tokenizer special token was not validated;not used','No original audio or private transcriptions are distributed'])
(w/'audio-role-catalogue-nov19.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['counts'])
# One fixture row for every original file, including aliases in different scene contexts.
fixture=bytearray(struct.pack('<I',sum(len(x['paths'])for x in catalogue)))
for x in catalogue:
 for path in x['paths']:
  match=re.fullmatch(r'PLACES/P(\d+)/S(\d+).WAV',path)
  place,id=(int(match[1]),int(match[2]))if match else(27,900+int(Path(path).stem[1:]))
  expected=x['role']=='effect';fixture+=struct.pack('<iii',place,id,int(expected))
(w/'audio-role-fixture-nov19.bin').write_bytes(fixture)
