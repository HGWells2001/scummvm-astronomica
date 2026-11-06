# SPDX-License-Identifier: GPL-3.0-or-later
"""Install the reviewed engine/core pair into the pinned upstream checkout."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def install(destination):
    destination=destination.resolve()
    info=json.loads((ROOT/'SCUMMVM_BASE.json').read_text())
    head=subprocess.check_output(['git','-C',str(destination),'rev-parse','HEAD'],text=True).strip()
    if head!=info['commit']:raise SystemExit('Checkout revision differs from SCUMMVM_BASE.json; no files changed.')
    spec=json.loads((ROOT/info['framework_patch']).read_text())
    if spec['engine_sha256']!=info['engine_sha256']or spec['patched_sha256']!=info['framework_sha256']:
        raise SystemExit('Core/engine manifest pair differs; no files changed.')
    source=ROOT/info['engine_directory'];target=destination/'engines/astronomica'
    for name,h in info['engine_sha256'].items():
        if Path(name).name!=name or digest(source/name)!=h:raise SystemExit('Invalid engine export: '+name)
    if target.exists():
        actual={p.name:digest(p)for p in target.iterdir()if p.is_file()}
        if actual!=info['engine_sha256']or any(p.is_dir()for p in target.iterdir()):
            raise SystemExit('Existing engine directory differs; no files overwritten.')
    # Preflight the complete core before creating the engine directory.
    names={'video/video_decoder.cpp','video/video_decoder.h','video/paused_audio_gate.h'}
    if set(spec['original_sha256'])!=names or set(spec['patched_sha256'])!=names:
        raise SystemExit('Unexpected core file list; no files changed.')
    actual={}
    for name in names:
        path=(destination/name).resolve()
        if not path.is_relative_to(destination):raise SystemExit('Core path leaves checkout; no files changed.')
        actual[name]=digest(path)if path.is_file()else None
        if digest(ROOT/'framework-overlay'/name)!=spec['patched_sha256'][name]:
            raise SystemExit('Core overlay differs; no files changed.')
    if actual not in (spec['original_sha256'],spec['patched_sha256']):
        raise SystemExit('Incompatible or partially modified core; no files changed.')
    if not target.exists():
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(source,target)
    subprocess.run([sys.executable,str(ROOT/'tools/apply_framework_patch.py'),'--root',str(destination),'--manifest',str(ROOT/info['framework_patch']),'--apply'],check=True)
    print('Verified engine/core pair installed. Full clean rebuild required; discard old build objects and libraries.')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('checkout',type=Path)
    install(ap.parse_args().checkout)
