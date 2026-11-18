"""Read original NAV bytes and execute original transition instructions as oracle."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, struct, sys
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(o));sys.argv=[str(__file__),'D:/astro','--out',str(w/'navigation-music-cases-nov18-unused.json'),'--deps',str(w/'deps-verified')]
import probe_transitions as original
inventory=json.loads((w/'original-branches-nov6/inventory.json').read_text())
audio=json.loads((w/'scene-audio-mode-inventory-nov17.json').read_text());rooms={x['place']:x for x in audio['rows']}
cases=[];files={};gates=0
for index,ref in enumerate(inventory['route_references']):
    if ref['kind']!='navigation':continue
    source=ref['source'];direction=['left','forward','right'].index(ref['direction']) if ref['direction']!='up' else 1
    path=Path('D:/astro/PLACES')/('P'+str(source))/'MEGAFILE.HYP';data=path.read_bytes()
    assert sha(path)==rooms[source]['sha256'] and rooms[source]['mode']==1
    assert struct.unpack_from('<i',data,4+4*direction)[0]==ref['destination']
    files[source]=sha(path)
    values=[0]*100;denied=original.run(source,ref['destination'],values)
    permits=[0,1] if denied[0]!=ref['destination'] else [0]
    gates+=len(permits)-1
    for permit in permits:
        values[57]=permit;result=original.run(source,ref['destination'],values)
        assert result[2:]==[0,0]
        for pad in (0,1):
            cases.append(dict(route_index=index,source=source,direction=direction,requested=ref['destination'],permit=permit,destination=result[0],permit_after=result[1],source_loop=rooms[source]['normal_loop'],destination_loop=rooms[result[0]]['normal_loop'],keypad=pad))
assert len(files)==305 and gates==9 and len(cases)==1538
out=dict(status='ORIGINAL_NAVIGATION_MUSIC_CASES_READY',at=datetime.now(timezone.utc).isoformat(),original_exe_sha256=sha(Path('D:/astro/SETUP/ASTRO.EXE')),original_transition_region_sha256=hashlib.sha256(original.code[0x289:0x790]).hexdigest(),oracle_sha256=sha(o/'probe_transitions.py'),interpreter_sha256=sha(o/'probe_p526_motion.py'),route_inventory_sha256=sha(w/'original-branches-nov6/inventory.json'),audio_inventory_sha256=sha(w/'scene-audio-mode-inventory-nov17.json'),original_scene_sha256=files,cases=cases,limits=['Controlled global57=0 and gated global57=1 fixtures, not every global state or click route','Literal route indices refer to the original November6 syntax inventory; no reachability claim'])
(w/'navigation-music-cases-nov18.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(cases))
