"""Exercise the exported installation entry points against a clean pinned checkout."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica'
out=w/'all-effects-install-n19';out.mkdir(exist_ok=False)
tree=out/'scummvm';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(*args,ok=True):
    result=subprocess.run(list(map(str,args)),capture_output=True,text=True)
    with(out/'commands.log').open('a',encoding='utf-8')as f:f.write(repr(args)+'\n'+result.stdout+result.stderr)
    if ok:result.check_returncode()
    else:assert result.returncode!=0
    return result
def inventory():
    # Includes the exact source installation boundary and backup data, not Git internals.
    return {p.relative_to(tree).as_posix():sha(p)for root in ('video','engines/astronomica','.astronomica-core-backups')for p in(tree/root).rglob('*')if p.is_file()}
try:
    run('git','clone','--shared','--no-checkout',w/'scummvm',tree)
    run('git','-C',tree,'config','--local','core.longpaths','true')
    base=json.loads((pub/'SCUMMVM_BASE.json').read_text())
    run('git','-C',tree,'checkout','--detach',base['commit'])
    core=tree/'video/video_decoder.h';old=core.read_bytes()
    core.write_bytes(old+b'\n// incompatible-user-core-fixture\n')
    before=inventory()
    run(sys.executable,pub/'tools/install_engine.py',tree,ok=False)
    assert before==inventory()and not(tree/'engines/astronomica').exists()
    core.write_bytes(old)
    run(sys.executable,pub/'tools/prepare_scummvm.py','--destination',tree)
    for name,h in base['engine_sha256'].items():assert sha(tree/'engines/astronomica'/name)==h
    for name,h in base['framework_sha256'].items():assert sha(tree/name)==h
    backups=list((tree/'.astronomica-core-backups').iterdir());assert len(backups)==1
    spec=json.loads((pub/'framework-patch.json').read_text())
    for name,h in spec['original_sha256'].items():
        if h is not None:assert sha(backups[0]/name)==h
    before=inventory()
    run(sys.executable,pub/'tools/install_engine.py',tree)
    assert before==inventory()
    core.write_bytes(core.read_bytes()+b'\n// incompatible-partial-fixture\n')
    before=inventory()
    run(sys.executable,pub/'tools/prepare_scummvm.py','--destination',tree,ok=False)
    assert before==inventory()
    core.write_bytes((pub/'framework-overlay/video/video_decoder.h').read_bytes())
    engine=tree/'engines/astronomica/astronomica.h';old=engine.read_bytes();engine.write_bytes(old+b'\n// user-engine-change\n')
    before=inventory();run(sys.executable,pub/'tools/install_engine.py',tree,ok=False);assert before==inventory()
    engine.write_bytes(old)
    run(sys.executable,pub/'tools/apply_framework_patch.py','--root',tree)
    proof=dict(status='ALL_EFFECTS_EXPORTED_INSTALLER_INTEGRATION_PASS',completed_at=datetime.now(timezone.utc).isoformat(),upstream_commit=base['commit'],engine_sha256=base['engine_sha256'],framework_sha256=base['framework_sha256'],export_manifest_sha256=sha(pub/'SOURCE-MANIFEST.json'),clean_pinned_checkout=True,stock_install=True,original_core_backups=True,idempotent_no_write=True,incompatible_core_before_engine_copy_refused_no_write=True,partial_patch_refused_no_write=True,modified_engine_refused_no_write=True,full_rebuild_required=True,gameplay_rerun=False)
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(proof['status'])
except Exception as e:
    (out/'failure.json').write_text(json.dumps(dict(status='FAIL',error=str(e)),indent=2)+'\n');raise
