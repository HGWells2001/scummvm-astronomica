"""Original executable evidence for first-command template timer semantics."""
import argparse,hashlib,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('exe',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
b=args.exe.read_bytes();assert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols=json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
checks=[('_read_command_mem',0x341b,'6626894730','Store timeGetTime result at command +0x30 during reading'),('_copy_command',0x1ad4,'c45e0666268b4730c45e0a6626894730','Copy timestamp unchanged'),('_execute_command',0x118b,'c45e06268b5f04c1e302ffb7da0cffb7d80c900ee8f80783c404','Opcode 41 queues the original template without replacing its timestamp'),('_handle_pending',0x1b89,'c45ef2668b46e666262b4730c45ef266263b4734','Compare elapsed time against command delay')]
rows=[]
for name,off,expected,meaning in checks:
 s=next(s for s in symbols if s['name']==name);pos=s['file_offset']-s['offset']+off
 assert b[pos:pos+len(bytes.fromhex(expected))]==bytes.fromhex(expected)
 rows.append(dict(symbol=name,address=f"{s['segment']}:{off:04x}",bytes=expected,meaning=meaning))
args.out.write_text(json.dumps(dict(checks=rows,implementation='Scene template registration epoch is captured before entry audio. Delayed heads use that epoch; continuation timers remain relative to execution.'),indent=2))
print('Original template timing evidence: PASS')
