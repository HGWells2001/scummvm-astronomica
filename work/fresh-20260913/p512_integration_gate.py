"""Explicit reviewed ASVM29 descendant context; never relax historical v28 gates."""
from pathlib import Path
import hashlib,json,os

def active_context_path(work):
    context=os.environ.get('ASTRONOMICA_REVIEWED_DESCENDANT','')
    assert context in ('','p281-sealed29'),'Unknown reviewed descendant context'
    return Path(work)/('p281-integration.json' if context else 'p512-integration.json')

def validated_integration(root,work,expected):
    context=os.environ.get('ASTRONOMICA_REVIEWED_DESCENDANT','')
    assert context in ('','p281-sealed29'),'Unknown reviewed descendant context'
    if context:
        from p281_integration_gate import validated_p281_integration
        return validated_p281_integration(root,work,expected)
    root,work=Path(root),Path(work);d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    p=json.loads((work/'p512-integration.json').read_text())
    assert p['status']=='SOURCE_PROMOTED_AWAITING_MAIN_CLOSURE' and p['base_exe']=='6dd09d6494b2c115579f46718b6c924b6f37c13307343e045e5bb38c87ba0f81'
    assert p['main_exe_sha256']==expected and expected!=p['base_exe']
    stage=work/'p512-sealed28-rebase-stage';review=stage/'root-source-review.json'
    assert d(review)==p['root_source_review_sha256']
    r=json.loads(review.read_text());assert r['status']=='ROOT_INDEPENDENT_P512_SEALED28_SOURCE_REVIEW_PASS' and r['p510_and_all_upstream_source_preserved']
    assert r['stage_sha256']==p['stage_sha256']=={n:d(stage/n) for n in p['stage_sha256']}
    assert p['isolated_normal_proof_sha256']==d(stage/'normal-routes-proof.json')
    native=json.loads((stage/'normal-routes-proof.json').read_text())
    assert native['status']=='PASS_ISOLATED_P512_ALL_NORMAL_MUSIC_FILE' and native['stage_sha256']==r['stage_sha256']
    assert native['candidate_exe_sha256']==d(stage/'candidate-build/scummvm.exe')
    baseline=r['baseline23_sha256'];assert len(baseline)==23
    current=dict(baseline);current.update(r['stage_sha256'])
    for folder in [root/'outputs/astronomica-cleanroom/engine/astronomica',work/'scummvm/engines/astronomica']:
        assert current=={f.name:d(f) for f in folder.iterdir() if f.is_file()},('source changed',str(folder))
    snapshot=work/'verified-checkpoints/p510-6dd09d6494b2'
    frozen=json.loads((snapshot/'checkpoint.json').read_text())
    published=json.loads((snapshot/'p510-completion-status.json').read_text())
    assert frozen['engine_sha256']==baseline and frozen['exe_sha256']==p['base_exe']
    assert published['status']=='PASS' and published['published_commit']=='a56d2fd646ac440cf01139db32edc3483f0f25f7' and published['exe_sha256']==p['base_exe']
    assert published['clean_clone'] and published['remote_verified'] and d(snapshot/'scummvm.exe')==p['base_exe']
    return p,current
