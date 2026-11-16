"""Inventory exact reuse of the four shared feedback clips; retain unknown roles."""
from pathlib import Path
import hashlib,json,wave
from datetime import datetime,timezone
w=Path(__file__).resolve().parent;root=Path('D:/astro');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
references={sha(root/('PLACES/P517/S%d.WAV'%n)):n for n in (2,3,4,5)}
rows=[]
for p in sorted((root/'PLACES').glob('P*/S*.WAV')):
 h=sha(p);name=p.relative_to(root).as_posix()
 with wave.open(str(p))as stream:duration=stream.getnframes()/stream.getframerate()
 rows.append(dict(path=name,sha256=h,bytes=p.stat().st_size,duration_seconds=duration,role='SHARED_FEEDBACK'if h in references else'UNCLASSIFIED',shared_reference=references.get(h)))
j=dict(status='SHARED_FEEDBACK_REUSE_INVENTORY_COMPLETE',created_at=datetime.now(timezone.utc).isoformat(),references=references,files=rows,feedback_files=sum(r['role']=='SHARED_FEEDBACK'for r in rows),unclassified_files=sum(r['role']=='UNCLASSIFIED'for r in rows),limits=['Exact clip identity, not a complete speech/effect catalogue','Unclassified clips retain foreground behavior; no role guessed from duration'])
(w/'feedback-audio-inventory-nov16.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'],j['feedback_files'],'shared feedback files',j['unclassified_files'],'unclassified')
