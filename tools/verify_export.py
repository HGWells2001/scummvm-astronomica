"""Verify this exported source snapshot; no original game data is required."""
from pathlib import Path
import hashlib,json

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'SOURCE-MANIFEST.json').read_text())
for name,expected in manifest['sha256'].items():
 path=(root/name).resolve()
 if not path.is_relative_to(root):raise SystemExit('Invalid manifest path')
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
  raise SystemExit('Export hash mismatch: '+name)
base=json.loads((root/'SCUMMVM_BASE.json').read_text())
for name,expected in base['engine_sha256'].items():
 path=root/base['engine_directory']/name
 if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise SystemExit('Engine hash mismatch: '+name)
print('Export integrity PASS:',len(manifest['sha256']),'files;',len(base['engine_sha256']),'native engine files.')
