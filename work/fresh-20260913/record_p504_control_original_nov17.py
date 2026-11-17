"""Record only the reviewed original numeric-control evidence, excluding other unknown roles."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
w=Path(__file__).resolve().parent;root=Path('D:/astro');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inventory=json.loads((w/'additional-control-sounds-nov17.json').read_text());clip=next(x for x in inventory['candidates']if x['audio_sha256']=='10913e35074e459685caeda03486bc96c92a9202292b6dfa589b54391df429e3');assert len(clip['occurrences'])==1
row=clip['occurrences'][0];assert row['place']==504 and row['sprite']==10 and row['sound_id']==10
assert sha(root/row['audio_path'])==clip['audio_sha256'] and sha(root/'PLACES/P504/MEGAFILE.HYP')==row['hyp_sha256']
assert [c['opcode']for c in row['commands']]==[28,9,46,31,32,42,23,41,29]
data=(root/row['audio_path']).read_bytes();fnv=2166136261
for byte in data:fnv=((fnv^byte)*16777619)&0xffffffff
receipt=dict(status='ORIGINAL_P504_SPEED_CONTROL_EFFECT_EVIDENCE_PASS',at=datetime.now(timezone.utc).isoformat(),audio_sha256=clip['audio_sha256'],bytes=len(data),fnv1a=fnv,control=row,unclassified_candidates_not_adopted=25,role_basis='Exact original locked speed increment,local1 capped15,custom8 frame refresh,150ms input release; not duration-only inference',user_installation_ignored=True,limits=['One exact clip/control only; not a complete speech/effect catalogue','Original asset identities and control semantics only; actual overlap checked by native baseline/candidate'])
(w/'p504-control-original-nov17.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
