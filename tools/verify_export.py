# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify the exported source snapshot and mandatory engine/video-core pair."""
from pathlib import Path,PurePosixPath
import hashlib,json

root=Path(__file__).resolve().parents[1]
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((root/'SOURCE-MANIFEST.json').read_text())
for name,h in manifest['sha256'].items():
    path=(root/name).resolve()
    if not path.is_relative_to(root)or PurePosixPath(name).as_posix()!=name:
        raise SystemExit('Invalid manifest path')
    if not path.is_file()or digest(path)!=h:raise SystemExit('Export hash mismatch: '+name)
base=json.loads((root/'SCUMMVM_BASE.json').read_text())
engine=root/base['engine_directory']
if {p.name:digest(p)for p in engine.iterdir()if p.is_file()}!=base['engine_sha256']or any(p.is_dir()for p in engine.iterdir()):
    raise SystemExit('Engine file set differs')
spec=json.loads((root/base['framework_patch']).read_text())
if spec['engine_sha256']!=base['engine_sha256']or spec['patched_sha256']!=base['framework_sha256']:
    raise SystemExit('Engine/core pairing differs')
names={'video/video_decoder.cpp','video/video_decoder.h','video/paused_audio_gate.h'}
if set(spec['original_sha256'])!=names or set(spec['patched_sha256'])!=names:
    raise SystemExit('Core file set differs')
for name,h in spec['patched_sha256'].items():
    if digest(root/'framework-overlay'/name)!=h:raise SystemExit('Core hash mismatch: '+name)
print('Export integrity PASS:',len(manifest['sha256']),'files; engine23/core3 paired; clean rebuild required.')
