"""Verify the versioned source package before downloads or compilation."""
from pathlib import Path, PurePosixPath
import hashlib
import json

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
for name, expected in manifest['sha256'].items():
    path = (root / name).resolve()
    if PurePosixPath(name).as_posix() != name or not path.is_relative_to(root):
        raise SystemExit('Percorso non valido nel manifesto: ' + name)
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit('Pacchetto incompleto o modificato: ' + name)
print('Integrita pacchetto verificata:', len(manifest['sha256']), 'file')
