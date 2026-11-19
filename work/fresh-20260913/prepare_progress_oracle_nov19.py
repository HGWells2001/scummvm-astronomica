"""Build independent drawing fixtures by executing the original score instructions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,runpy,struct,sys
w=Path(__file__).resolve().parent;r=w.parents[1];out=w/'progress-render-oracle-nov19';out.mkdir(exist_ok=True);assert not(out/'proof.json').exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(r/'outputs/astronomica-cleanroom'))
script=r/'outputs/astronomica-cleanroom/probe_progress_indicator_nov19.py';sys.argv=[str(script),'D:/astro','--workspace',str(w),'--out',str(out/'original-instructions')];ns=runpy.run_path(str(script))
cases=[dict(kind=0,scene=103,counter=0,globals=v,rectangles=ns['run'](v))for v in ns['cases']]
old=w/'verified-checkpoints/windows-cursor-loop-523b2d1f0816/native/new-room-only/saves/astro-verify.060';assert sha(old)=='7c06575ed063cba735f55689834ed6d5da4d24c6eaa3c5763a9a4467fdca003a'
data=old.read_bytes();assert data[:8]==b'ASVM\x02\0\0\0';words=struct.unpack_from('<103I',data,8);assert words[0]==103
values=[v if v<0x80000000 else v-0x100000000 for v in words[2:102]]
cases.append(dict(kind=1,scene=103,counter=words[1],globals=values,rectangles=ns['run'](values)))
raw=bytearray(b'PSCR0001'+struct.pack('<I',len(cases)))
for c in cases:
    raw+=struct.pack('<3I',c['kind'],c['scene'],c['counter'])+struct.pack('<100i',*c['globals'])+struct.pack('<I',len(c['rectangles']))
    for rect in c['rectangles']:raw+=struct.pack('<4h',*rect)
fixture=out/'fixture.bin';fixture.write_bytes(raw)
proof=dict(status='ORIGINAL_PROGRESS_RENDER_FIXTURE_PASS',at=datetime.now(timezone.utc).isoformat(),author_sha256=sha(Path(__file__)),original_probe_sha256=sha(script),original_instruction_proof_sha256=sha(out/'original-instructions/proof.json'),fixture_sha256=sha(fixture),controlled_cases=len(cases)-1,genuine_old_world_cases=1,old_world_slot_sha256=sha(old),old_world_slot_path=str(old),cases=len(cases),limits=['Original score instructions are the drawing oracle;GDI calls modeled','The final case is a physical earlier-engine ASVM2 file,not an original Windows save'])
(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(proof['status'],len(cases))
