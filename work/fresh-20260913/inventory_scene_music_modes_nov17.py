"""Tie original audio selector rules to every readable original scene without changing assets."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,re,sys,wave
w=Path(__file__).resolve().parent;root=Path('D:/astro');sys.path.insert(0,str(w.parents[1]/'outputs/astronomica-cleanroom'))
from astro_reader import parse,FormatError
sha=lambda b:hashlib.sha256(b).hexdigest();rows=[];unknown=[];counts=collections.Counter()
for p in sorted((root/'PLACES').glob('P*/MEGAFILE.HYP'),key=lambda p:int(p.parent.name[1:])):
 raw=p.read_bytes();tail=0
 try:scene=parse(raw)
 except FormatError as error:
  m=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(error))
  if not m:unknown.append(dict(place=int(p.parent.name[1:]),sha256=sha(raw),error=str(error)));continue
  tail=int(m[1]);stop=int(m[2],16);assert stop+tail==len(raw);scene=parse(raw[:stop])
 place=int(p.parent.name[1:]);mode=scene['mode'];counts[mode]+=1
 def selected(flag):
  result=901 if place==1 else 902 if place==422 else 0
  if mode==3 or place==402:result=900
  if mode==1:result=908 if flag==1 else 901 if 219<=place<=251 or place in(1,410)else 903 if 361<=place<=389 or place==420 else 902
  return result
 rows.append(dict(place=place,mode=mode,sha256=sha(raw),opaque_tail_bytes=tail,intro=scene.get('intro_sound_id'),movies=scene['movies'],normal_loop=selected(0),countdown_loop=selected(1),local_s0_present=(p.parent/'S0.WAV').exists()))
shared={}
for id in(900,901,902,903,908):
 p=root/'SOUNDS'/('S%d.WAV'%(id-900));data=p.read_bytes();fnv=2166136261
 for byte in data:fnv=((fnv^byte)*16777619)&0xffffffff
 with wave.open(str(p))as f:shared[str(id)]=dict(bytes=len(data),sha256=sha(data),fnv1a=fnv,frames=f.getnframes(),rate=f.getframerate(),sample_width=f.getsampwidth(),channels=f.getnchannels())
j=dict(status='ORIGINAL_SCENE_AUDIO_MODE_INVENTORY_COMPLETE',at=datetime.now(timezone.utc).isoformat(),scenes=len(rows),mode_counts=dict(counts),shared_audio=shared,rows=rows,unreadable=unknown,limits=['Selections derived from the independently checked original45192case selector; not additional original runtime execution','Opaque tails retained by full-file hash; unsupported/truncated scene remains explicit','Does not establish native menu/interlude sound admission,playback timing or whole-game audiovisual fidelity'])
(w/'scene-audio-mode-inventory-nov17.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'],dict(counts));print([r for r in rows if r['place']in(0,1,402,422)or r['mode']==3])
