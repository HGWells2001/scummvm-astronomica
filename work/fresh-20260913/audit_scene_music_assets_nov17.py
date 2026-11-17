"""Validate original selected music assets for all readable scene headers, without playback claims."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,struct,wave
w=Path(__file__).resolve().parent;root=Path('D:/astro');read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inventory=w/'scene-audio-mode-inventory-nov17.json';inv=read(inventory);assert inv['scenes']==420
rows=[];assets={};counts=collections.Counter()
for scene in inv['rows']:
 place=scene['place'];hyp=root/f'PLACES/P{place}/MEGAFILE.HYP';assert sha(hyp)==scene['sha256']
 for state,key in ((0,'normal_loop'),(1,'countdown_loop')):
  id=scene[key];relative=f'SOUNDS/S{id-900}.WAV' if id>=900 else f'PLACES/P{place}/S{id}.WAV';path=root/relative
  item=dict(place=place,mode=scene['mode'],global60=state,selected_id=id,relative_asset=relative,present=path.is_file())
  if path.is_file():
   if relative not in assets:
    data=path.read_bytes();assert data[:4]==b'RIFF' and data[8:12]==b'WAVE';at=12;formats=[];payloads=[]
    while at+8<=len(data):
     tag=data[at:at+4];size=struct.unpack_from('<I',data,at+4)[0];assert at+8+size<=len(data)
     if tag==b'fmt ':formats.append(struct.unpack_from('<HHIIHH',data,at+8))
     if tag==b'data':payloads.append(size)
     at+=8+size+(size%2)
    assert len(formats)==len(payloads)==1;encoding,channels,rate,byte_rate,align,bits=formats[0]
    assert encoding==1 and channels in (1,2) and bits in (8,16) and align==channels*bits//8 and byte_rate==rate*align
    with wave.open(str(path))as stream:
     assert stream.getnchannels()==channels and stream.getframerate()==rate and stream.getnframes()*align==payloads[0]
     assets[relative]=dict(sha256=sha(path),bytes=len(data),pcm_type=encoding,channels=channels,rate=rate,bits=bits,frames=stream.getnframes())
   item['asset_sha256']=assets[relative]['sha256'];counts['present_selected_cases']+=1
  else:
   assert id==0 and scene['mode']==0,'Missing original shared Music asset'
   counts['local_zero_absent_cases']+=1
  rows.append(item)
for id,meta in inv['shared_audio'].items():assert assets[f'SOUNDS/S{int(id)-900}.WAV']['sha256']==meta['sha256']
for scene in inv['unreadable']:assert sha(root/f"PLACES/P{scene['place']}/MEGAFILE.HYP")==scene['sha256']
out=dict(status='ORIGINAL_SCENE_SELECTED_MUSIC_ASSETS_PASS',at=datetime.now(timezone.utc).isoformat(),inventory_sha256=sha(inventory),readable_scene_headers=420,state_cases=len(rows),counts=dict(counts),unique_assets=len(assets),assets=assets,selection_rows=rows,unreadable_scene_headers=inv['unreadable'],user_installation_ignored=True,engine_modified=False,limits=['Original header selection and PCM asset integrity,not timing,perceptual or whole-game gameplay verification','Missing local0 retained explicitly as original asset absence; no replacement track invented','P406 remains truncated and excluded; four opaque tails retain original full-file hashes'])
(w/'scene-music-asset-review-nov17.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],dict(counts),'unique assets',len(assets),'absent places',sorted({r['place']for r in rows if not r['present']}))
