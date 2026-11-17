"""Record two exact original numeric selector effects without original image/text payloads."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
w=Path(__file__).resolve().parent;root=Path('D:/astro');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();data=json.loads((w/'additional-control-sounds-nov17.json').read_text());rows=[]
for pin,sprite,clip,size,step in [('1cc78cf15ee6af07862b53720fc75dd891d01a08d661cf5ba9d49d7d6405a74f',7,8,3306,1),('c34e45b86f1a6d5a2b5137b3f95cf2385f51073392fc82e001197c80d414ba53',8,9,3310,-1)]:
 item=next(x for x in data['candidates']if x['audio_sha256']==pin);r=next(r for r in item['occurrences']if r['place']==513 and r['sprite']==sprite);audio=root/r['audio_path'];raw=audio.read_bytes()
 assert sha(audio)==pin and len(raw)==size and sha(root/'PLACES/P513/MEGAFILE.HYP')==r['hyp_sha256'];commands=r['commands'];assert len(commands)==55 and commands[1]['args']==[clip+1] and commands[2]['args']==[1,0,step] and commands[-1]['delay']==200
 fnv=2166136261
 for byte in raw:fnv=((fnv^byte)*16777619)&0xffffffff
 rows.append(dict(place=513,sprite=sprite,sound_id=clip,hyp_sha256=r['hyp_sha256'],audio_sha256=pin,bytes=size,fnv1a=fnv,first_command_offset=commands[0]['offset'],last_command_offset=commands[-1]['offset'],command_count=55,opcodes=[c['opcode']for c in commands],numeric_prefix=commands[:7],local_slot=0,numeric_step=step,input_release_delay_ms=200,image_load_commands=sum(c['opcode']==20 for c in commands),image_present_commands=sum(c['opcode']==49 for c in commands)))
receipt=dict(status='ORIGINAL_P513_NUMERIC_CONTROL_EFFECT_EVIDENCE_PASS',at=datetime.now(timezone.utc).isoformat(),controls=rows,role_basis='Original locked numeric increment/decrement,explicit boundary stores,eight branches with two image presentations each,and200ms input release; not duration-only classification',remaining_unclassified_candidate_clips=23,user_installation_ignored=True,limits=['Two exact clips only; no general unknown sound-role classifier','Actual original control execution and Music overlap checked separately by native before/after probes'])
(w/'p513-control-original-nov17.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
