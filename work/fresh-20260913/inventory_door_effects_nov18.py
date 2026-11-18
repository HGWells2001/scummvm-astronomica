"""Identify the two shared door responses through original commands and exact assets."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,struct
w=Path(__file__).resolve().parent;root=Path('D:/astro');read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
syntax=w/'original-branches-nov6/inventory.json';inv=read(syntax);rows=[];clips=[]
for sound,pin in [(905,'28b3263ccd09b8b0f11b1354e3ef46121cf5e64819edafadc9b6fb30aaab6910'),(907,'f62da4a43fb2664b4ff98723cb6d7449b1049c648666a66c358090355df7ae72')]:
    p=root/f'SOUNDS/S{sound-900}.WAV';data=p.read_bytes();assert sha(p)==pin;fnv=2166136261
    for b in data:fnv=((fnv^b)*16777619)&0xffffffff
    clips.append(dict(id=sound,bytes=len(data),sha256=pin,fnv1a=fnv))
    for c in inv['commands']:
        if c['opcode']!=9 or c['args']!=[sound+1]:continue
        scene=root/f"PLACES/P{c['scene']}/MEGAFILE.HYP";raw=scene.read_bytes()
        assert sha(scene)==next(x['sha256']for x in inv['scenes']if x['scene']==c['scene'])
        assert struct.unpack_from('<2i',raw,c['file_offset'])==(9,sound+1)
        rows.append(dict(command_id=c['id'],scene=c['scene'],offset=c['file_offset'],id=sound,scene_sha256=sha(scene)))
assert len(rows)==19 and sum(x['id']==905 for x in rows)==17
p27=[c for c in inv['commands']if c['scene']==27];assert [c['opcode']for c in p27]==[28,31,5,45,31,16,9,32,42,29]
assert p27[2]['args']==[32] and p27[5]['args']==[1] and p27[6]['args']==[906] and p27[7]['args']==[1,0,1] and p27[-1]['delay_ms']==500
out=dict(status='ORIGINAL_SHARED_DOOR_EFFECTS_EVIDENCE_PASS',at=datetime.now(timezone.utc).isoformat(),syntax_inventory_sha256=sha(syntax),clips=clips,references=rows,role_basis=['User identified P27 door as the audible effect that interrupts Music','Original P27 script shows the door,plays shared905,sets local0=1;next click enters P32','P85 door-control rectangle uses shared907 in its opening/state-transition branches'],limits=['Two exact shared door assets only; shared narration/music IDs remain excluded','Other unclassified local effects are not inferred from duration or file numbering'])
(w/'door-effects-original-nov18.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
