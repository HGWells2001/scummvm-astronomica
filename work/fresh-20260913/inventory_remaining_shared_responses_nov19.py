"""Recheck unresolved shared response sites without guessing their audio roles."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,struct
w=Path(__file__).resolve().parent;root=Path('D:/astro');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inv=json.loads((w/'original-branches-nov6/inventory.json').read_text());rows=[];clips=[]
for sound in(904,906):
    p=root/f'SOUNDS/S{sound-900}.WAV';clips.append(dict(sound=sound,bytes=p.stat().st_size,sha256=sha(p),role='UNCLASSIFIED',music_overlap_enabled=False))
    for c in inv['commands']:
        if c['opcode']!=9 or c['args']!=[sound+1]:continue
        scene=root/f"PLACES/P{c['scene']}/MEGAFILE.HYP";raw=scene.read_bytes();assert sha(scene)==next(x['sha256']for x in inv['scenes']if x['scene']==c['scene'])
        assert struct.unpack_from('<2i',raw,c['file_offset'])==(9,sound+1)
        script=[x for x in inv['commands']if x['scene']==c['scene']and x['trigger']==c['trigger']]
        rows.append(dict(command_id=c['id'],scene=c['scene'],trigger=c['trigger'],offset=c['file_offset'],sound=sound,original_scene_sha256=sha(scene),original_script_opcodes=[x['opcode']for x in script],natural_reachability='UNCLASSIFIED',audio_role='UNCLASSIFIED'))
assert len(rows)==23 and sum(x['sound']==904 for x in rows)==2
proof=dict(status='ORIGINAL_UNCLASSIFIED_SHARED_RESPONSES_INVENTORY_PASS',at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),syntax_inventory_sha256=sha(w/'original-branches-nov6/inventory.json'),clips=clips,resource_command_sites=23,rows=rows,production_engine_changed=False,limits=['Two shared clips at23 original resource-command sites,additional to the reviewed905/907 door effects','Trigger structure is evidence of where playback occurs,not an acoustic speech/effect classification','No duration or consecutive-ID heuristic;these clips remain foreground until their roles are reviewed','Native callbacks and a complete sound catalogue are outside this inventory'])
(w/'remaining-shared-responses-nov19.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(proof['status'],len(rows))
