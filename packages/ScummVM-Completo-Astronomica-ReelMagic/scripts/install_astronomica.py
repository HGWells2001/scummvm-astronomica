"""Install the pinned Astronomica engine/core pair after the ReelMagic stages.

Preflight every input and target before writing; refuse changed engine/core files.
Original shared core and all ReelMagic changes remain recoverable in Git.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / 'astronomica'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def install(target):
    target = target.resolve()
    pins = json.loads((ROOT / 'SOURCES.json').read_text())
    spec = json.loads((PAYLOAD / 'framework-patch.json').read_text())
    subprocess.run(['git', '-C', str(target), 'merge-base', '--is-ancestor',
                    pins['scummvm_base'], 'HEAD'], check=True)
    # These files prove that the full ReelMagic pipeline ran before integration.
    for name in ('RTZ_REELMAGIC_BUILD.txt', 'video/reelmagic_decoder.cpp',
                 'engines/made/mpegplayer.cpp'):
        if not (target / name).is_file():
            raise SystemExit('Preparazione ReelMagic incompleta: ' + name)
    source_files = {p.name for p in (PAYLOAD / 'engine').iterdir() if p.is_file()}
    if source_files != set(spec['engine_sha256']):
        raise SystemExit('Pacchetto Astronomica incompleto')
    destination = target / 'engines/astronomica'
    if destination.exists() and {p.name for p in destination.iterdir()} != source_files:
        raise SystemExit('Engine Astronomica preesistente diverso; usare un nuovo WorkRoot')
    updates = {}
    for name, expected in spec['engine_sha256'].items():
        data = (PAYLOAD / 'engine' / name).read_bytes()
        if digest(data) != expected:
            raise SystemExit('Sorgente Astronomica modificato: ' + name)
        path = destination / name
        if path.exists() and digest(path.read_bytes()) != expected:
            raise SystemExit('Engine destinazione modificato: ' + name)
        updates[path] = data
    for name, expected in spec['patched_sha256'].items():
        data = (PAYLOAD / 'framework-overlay' / name).read_bytes()
        if digest(data) != expected:
            raise SystemExit('Overlay modificato: ' + name)
        path = target / name
        old = digest(path.read_bytes()) if path.exists() else None
        if old not in (spec['original_sha256'][name], expected):
            raise SystemExit('Core condiviso incompatibile; nessun file modificato: ' + name)
        updates[path] = data
    previous = {p: p.read_bytes() if p.exists() else None for p in updates}
    changed = []
    try:
        for path, data in updates.items():
            if previous[path] == data:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_name(path.name + '.combined.tmp')
            if temp.exists():
                raise RuntimeError('File temporaneo preesistente: ' + str(temp))
            temp.write_bytes(data)
            os.replace(temp, path)
            changed.append(path)
        for path, data in updates.items():
            assert path.read_bytes() == data
    except Exception:
        for path in reversed(changed):
            if previous[path] is None:
                path.unlink()
            else:
                path.write_bytes(previous[path])
        raise
    record = dict(status='ASTRONOMICA_REELMAGIC_SOURCE_PAIR_PASS', sources=pins,
                  engine_sha256=spec['engine_sha256'], framework_sha256=spec['patched_sha256'])
    (target / 'ASTRONOMICA_COMBINED.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Astronomica integrato: engine e core esatti, ReelMagic conservato. Ricompilazione completa richiesta.')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python install_astronomica.py CARTELLA_SCUMMVM')
    install(Path(sys.argv[1]))
