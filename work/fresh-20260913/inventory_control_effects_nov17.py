"""Identify short numeric-adjustment feedback through original script structure and exact assets."""
from pathlib import Path
import hashlib,json,sys,re
from datetime import datetime,timezone
w=Path(__file__).resolve().parent;root=Path('D:/astro');sys.path.insert(0,str(w.parents[1]/'outputs/astronomica-cleanroom'))
from astro_reader import parse,FormatError
rows=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for place in range(501,538):
 p=root/('PLACES/P%d/MEGAFILE.HYP'%place)
 if not p.exists():continue
 data=p.read_bytes();tail=0
 try:scene=parse(data)
 except FormatError as error:
  match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(error));assert match
  tail=int(match[1]);end=int(match[2],16);assert end+tail==len(data);scene=parse(data[:end])
 for index,sprite in enumerate(scene['sprites']):
  script=sprite.get('click',[]);ops=[c['opcode']for c in script]
  if ops!=[28,9,46,31,32,42,41,29]:continue
  if script[2]['args'][0]!=1 or abs(script[2]['args'][2])!=1:continue
  if any(c['delay']not in (0,-1,200)for c in script):continue
  sound=script[1]['args'][0]-1;audio=root/('PLACES/P%d/S%d.WAV'%(place,sound))
  if not audio.exists():continue
  data=audio.read_bytes();h=2166136261
  for v in data:h=((h^v)*16777619)&0xffffffff
  rows.append(dict(scene=place,sprite=index+1,xy=sprite['xy'],original_script_offset=script[0]['offset'],megafile_sha256=sha(p),opaque_tail_bytes=tail,command_opcodes=ops,sound_id=sound,audio_path=audio.relative_to(root).as_posix(),audio_sha256=sha(audio),bytes=len(data),fnv1a=h,role_evidence='Original locked numeric increment/decrement control with frame update and200ms release; not duration-only classification'))
out=dict(status='ORIGINAL_NUMERIC_CONTROL_EFFECT_INVENTORY_COMPLETE',created_at=datetime.now(timezone.utc).isoformat(),controls=rows,unique_audio_sha256=sorted({r['audio_sha256']for r in rows}),limits=['Only exact reviewed eight-command numeric adjustment pattern','Does not classify other sounds or prove a complete speech/effect catalogue'])
(w/'control-effects-inventory-nov17.json').write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'controls',len(out['unique_audio_sha256']),'unique clips')
