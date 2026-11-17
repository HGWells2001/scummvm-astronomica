"""Find exact decoded PCM aliases of reviewed effects, without classifying unknown sounds by length."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,wave
w=Path(__file__).resolve().parent;root=Path('D:/astro');read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
reuse=read(w/'feedback-audio-inventory-nov16.json');controls=read(w/'control-effects-inventory-nov17.json');known=set(reuse['references'])|set(controls['unique_audio_sha256'])
paths={r['sha256']:root/r['path']for r in reuse['files']if r['sha256']in known}
for r in controls['controls']:paths[r['audio_sha256']]=root/r['audio_path']
assert set(paths)==known and len(known)==8
def pcm(path):
 with wave.open(str(path))as stream:
  rate,channels,width,frames=stream.getframerate(),stream.getnchannels(),stream.getsampwidth(),stream.getnframes()
  assert stream.getcomptype()=='NONE';data=stream.readframes(frames);assert len(data)==frames*channels*width
  return (rate,channels,width,frames,sha(data))
by_pcm=collections.defaultdict(list)
for pin,path in paths.items():assert sha(path.read_bytes())==pin;by_pcm[pcm(path)].append(pin)
aliases=[];examined=0;unreadable=[]
for path in sorted(list((root/'PLACES').glob('P*/S*.WAV'))+list((root/'SOUNDS').glob('S*.WAV'))):
 examined+=1;data=path.read_bytes();pin=sha(data)
 if pin in known:continue
 try:key=pcm(path)
 except (wave.Error,EOFError)as e:unreadable.append(dict(path=path.relative_to(root).as_posix(),sha256=pin,error=str(e)));continue
 if key not in by_pcm:continue
 fnv=2166136261
 for b in data:fnv=((fnv^b)*16777619)&0xffffffff
 aliases.append(dict(path=path.relative_to(root).as_posix(),file_sha256=pin,bytes=len(data),fnv1a=fnv,pcm_sha256=key[-1],rate=key[0],channels=key[1],sample_width=key[2],frames=key[3],identical_reviewed_effect_file_sha256=by_pcm[key]))
j=dict(status='REVIEWED_FEEDBACK_PCM_ALIAS_INVENTORY_COMPLETE',at=datetime.now(timezone.utc).isoformat(),examined_files=examined,reviewed_file_identities=len(known),reviewed_pcm_identities=len(by_pcm),aliases=aliases,unreadable=unreadable,engine_modified=False,user_installation_ignored=True,limits=['Only exact raw PCM equality with identical rate,channels,sample width and frame count qualifies','Container metadata may differ; unknown nonmatching clips retain unclassified roles','No waveform similarity,voice recognition,duration-only or subjective classification'])
(w/'feedback-pcm-aliases-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'],'files',examined,'aliases',len(aliases),'unreadable',len(unreadable));print([(r['path'],r['bytes'])for r in aliases[:20]])
