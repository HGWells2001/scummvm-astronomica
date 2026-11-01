"""Explicit P281-only descendant of sealed P512, no historical gate bypass."""
from pathlib import Path
import hashlib,json

def validated_p281_integration(root,work,expected):
    root,work=Path(root),Path(work);d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    p=json.loads((work/'p281-integration.json').read_text())
    assert p['status']=='P281_SOURCE_PROMOTED_AWAITING_MAIN_CLOSURE'
    assert p['base_exe']=='932d7f5822152b41edeaddc6f0bdefdcbad1a334f439507c82497a6471b8932b' and p['base_commit']=='5000da749a05de7604fd6dc9f0d9313a4aa901bb'
    assert p['main_exe_sha256']==expected and expected!=p['base_exe']
    stage=work/'p281-sealed29-rebase-v2-stage';review=stage/'root-source-review.json'
    assert d(review)==p['root_source_review_sha256']
    checked=json.loads(review.read_text());assert checked['status']=='ROOT_P281_SEALED29_SOURCE_REVIEW_PASS' and checked['parent_source_preserved']
    assert checked['stage_sha256']==p['stage_sha256']=={n:d(stage/n) for n in p['stage_sha256']}
    native=stage/'candidate-build/proof.json';proof=json.loads(native.read_text())
    assert p['isolated_native_proof_sha256']==d(native) and proof['status']=='ISOLATED_P281_SEALED29_GATEWAY_UNSOLVED_RETURNS'
    assert proof['stage_sha256']==p['stage_sha256'] and proof['candidate_exe_sha256']==d(stage/'candidate-build/scummvm.exe')
    snapshot=work/'verified-checkpoints/p512-932d7f582215'
    seal=json.loads((snapshot/'p512-seal-status.json').read_text())
    assert seal['status']=='PASS' and seal['exe_sha256']==p['base_exe'] and seal['published_commit']==p['base_commit'] and seal['native_save_scenes']==33
    assert seal['engine_sha256']==checked['baseline23_sha256'] and len(seal['engine_sha256'])==23 and d(snapshot/'scummvm.exe')==p['base_exe']
    current=dict(seal['engine_sha256']);current.update(p['stage_sha256'])
    if 'clock_revision' in p:
        # This is a separately reviewed correction, never an overwrite of the
        # original gateway candidate or its frozen P512 ancestry.
        revision=p['clock_revision'];clock=work/'p281-stopclock-nov1-stage'
        review_path=clock/'root-source-review.json'
        assert set(revision)=={'root_review_sha256','isolated_native_sha256'}
        assert d(review_path)==revision['root_review_sha256']
        review=json.loads(review_path.read_text())
        assert review['status']=='ROOT_P281_STOPCLOCK_SOURCE_NATIVE_REVIEW_PASS'
        assert review['baseline23_sha256']==current and review['parent_source_preserved']
        assert review['format_version']==29 and not review['format_changed']
        assert review['stage_sha256']=={n:d(clock/n) for n in review['stage_sha256']}
        assert set(review['stage_sha256'])==set(p['stage_sha256'])
        native_path=clock/'native-proof.json';native=json.loads(native_path.read_text())
        assert d(native_path)==revision['isolated_native_sha256']==review['native_proof_sha256']
        assert native['status']=='PASS_P281_STOPCLOCK_NATIVE' and native['stage_sha256']==review['stage_sha256']
        assert native['candidate_exe_sha256']==d(clock/'candidate-build/scummvm.exe')==review['candidate_exe_sha256']
        current.update(review['stage_sha256'])
    for folder in (root/'outputs/astronomica-cleanroom/engine/astronomica',work/'scummvm/engines/astronomica'):
        assert current=={f.name:d(f) for f in folder.iterdir() if f.is_file()},('Unreviewed source change',str(folder))
    return p,current
