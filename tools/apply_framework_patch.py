# SPDX-License-Identifier: GPL-3.0-or-later
"""Install the exact reviewed core/engine pair into a compatible ScummVM tree.

Default is read-only checking. Copy the 23 candidate engine files first, then
use --apply. A full clean rebuild is mandatory after this ABI-changing patch.
"""
from pathlib import Path
import argparse,hashlib,json,os,tempfile
parser=argparse.ArgumentParser();parser.add_argument('--root',required=True,type=Path);parser.add_argument('--manifest',type=Path,default=Path(__file__).resolve().parent.parent/'framework-patch.json');parser.add_argument('--apply',action='store_true');args=parser.parse_args()
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
root=args.root.resolve();manifest=args.manifest.resolve();spec=json.loads(manifest.read_text());overlay=manifest.parent/'framework-overlay'
names={'video/video_decoder.cpp','video/video_decoder.h','video/paused_audio_gate.h'}
assert set(spec['patched_sha256'])==set(spec['original_sha256'])==names
assert root.is_dir()
for name,expected in spec['engine_sha256'].items():
 assert Path(name).name==name
 path=(root/'engines/astronomica'/name).resolve();assert path.is_relative_to(root)and path.is_file()and d(path)==expected,'Copy the complete reviewed engine first: '+name
targets={};old={}
for name in sorted(names):
 target=(root/name).resolve();assert target.is_relative_to(root)
 source=overlay/name;assert source.is_file()and d(source)==spec['patched_sha256'][name]
 targets[name]=target;old[name]=target.read_bytes()if target.exists()else None
if all(targets[name].is_file()and d(targets[name])==spec['patched_sha256'][name]for name in names):
 print('Already installed: exact reviewed engine/core pair. Use a clean build.');raise SystemExit(0)
for name in names:
 expected=spec['original_sha256'][name]
 assert (old[name]is None if expected is None else old[name]is not None and hashlib.sha256(old[name]).hexdigest()==expected),'Incompatible or partially modified core; no files changed: '+name
if not args.apply:
 print('Compatible stock core and exact engine confirmed; --apply installs with backups.');raise SystemExit(0)
backup=root/'.astronomica-core-backups'/d(manifest)[:16];backup.mkdir(parents=True,exist_ok=False)
for name,data in old.items():
 if data is not None:
  p=backup/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
(backup/'framework-patch.json').write_bytes(manifest.read_bytes())
def replace(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 handle,temp=tempfile.mkstemp(prefix='.astronomica-',dir=path.parent)
 try:
  with os.fdopen(handle,'wb')as stream:stream.write(data)
  os.replace(temp,path)
 finally:
  if Path(temp).exists():Path(temp).unlink()
changed=[]
try:
 for name in sorted(names):replace(targets[name],(overlay/name).read_bytes());changed.append(name)
 for name in names:assert d(targets[name])==spec['patched_sha256'][name]
except Exception:
 for name in reversed(changed):
  if old[name]is None:targets[name].unlink()
  else:replace(targets[name],old[name])
 raise
print('Installed exact reviewed engine/core pair. Original core backup:',backup)
print('Mandatory next step: clean rebuild every ScummVM project; do not reuse old objects/libraries.')
