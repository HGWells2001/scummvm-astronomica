"""Locate still-unclassified locked control sounds; roles remain observations, not automatic classifications."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,re,sys,wave
w=Path(__file__).resolve().parent;root=Path('D:/astro');sys.path.insert(0,str(w.parents[1]/'outputs/astronomica-cleanroom'))
from astro_reader import parse,FormatError
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
known=set(read(w/'feedback-audio-inventory-nov16.json')['references'])|set(read(w/'control-effects-inventory-nov17.json')['unique_audio_sha256'])
groups={}
for hyp in sorted((root/'PLACES').glob('P*/MEGAFILE.HYP')):
 raw=hyp.read_bytes()
 try:scene=parse(raw)
 except FormatError as error:
  m=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(error))
  if not m:continue
  assert int(m[2],16)+int(m[1])==len(raw);scene=parse(raw[:int(m[2],16)])
 place=int(hyp.parent.name[1:])
 for index,sprite in enumerate(scene['sprites']):
  commands=sprite.get('click',[]);ops=[c['opcode']for c in commands]
  if not commands or 28 not in ops or 29 not in ops or not any(op in ops for op in(41,46)):continue
  for c in commands:
   if c['opcode']!=9:continue
   id=c['args'][0]-1;audio=root/(f'SOUNDS/S{id-900}.WAV'if id>=900 else f'PLACES/P{place}/S{id}.WAV')
   if not audio.is_file():continue
   pin=sha(audio)
   if pin in known:continue
   if pin not in groups:
    with wave.open(str(audio))as stream:duration=stream.getnframes()/stream.getframerate()
    groups[pin]=dict(audio_sha256=pin,bytes=audio.stat().st_size,duration_seconds=duration,occurrences=[])
   groups[pin]['occurrences'].append(dict(place=place,sprite=index+1,xy=sprite['xy'],hyp_sha256=sha(hyp),audio_path=audio.relative_to(root).as_posix(),sound_id=id,commands=[dict(opcode=x['opcode'],args=x['args'],delay=x['delay'],offset=x['offset'])for x in commands]))
j=dict(status='ADDITIONAL_CONTROL_SOUND_CANDIDATES_INVENTORIED',at=datetime.now(timezone.utc).isoformat(),known_clip_hashes=sorted(known),candidates=list(groups.values()),candidate_unique_clips=len(groups),engine_modified=False,limits=['Locked controls with frame/scalar operations only; no effect/speech classification inferred from duration','Original scripts and exact audio identities retained; no new production whitelist entries','Unknown roles remain foreground until independently justified'])
(w/'additional-control-sounds-nov17.json').write_text(json.dumps(j,indent=2)+'\n')
print('Additional control sound candidates',len(groups))
for item in groups.values():print(item['audio_sha256'][:12],round(item['duration_seconds'],3),'s',[(r['place'],r['sprite'],r['sound_id'])for r in item['occurrences'][:3]])
