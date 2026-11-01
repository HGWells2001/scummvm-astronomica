"""Require exact-main gateway and genuine v29 proofs before public P281 claims."""
from pathlib import Path
import hashlib,json,re
def validated_p281(root,work):
    root,work=Path(root),Path(work);path=root/'evidence/p281-gateway-validation.json'
    if not path.exists():return None
    d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=json.loads(path.read_text());p=json.loads((root/'evidence/p281-native/gateway-proof.json').read_text())
    expected=d(work/'build/Releasex64/scummvm.exe')
    assert v['status']==p['status']=='PASS' and v['full_suite'] and v['exe_sha256']==p['exe_sha256']==expected
    assert v['source_context_sha256']==d(root/'evidence/p281-source-integration.json')
    p512=json.loads((root/'evidence/p512-saves-validation.json').read_text());assert p512['exe_sha256']==expected and p512['descendant_context_sha256']==v['source_context_sha256']
    context=json.loads((root/'evidence/p281-source-integration.json').read_text())
    if 'clock_revision' in context:
        from p512_clock_revision import validate_native
        validate_native(root/'evidence/p512-save-proof.json',root/'evidence/p512-native',expected)
        clock_review=root/'evidence/p281-stopclock-source-review.json'
        assert d(clock_review)==context['clock_revision']['root_review_sha256']
        reviewed=json.loads(clock_review.read_text())
        assert reviewed['status']=='ROOT_P281_STOPCLOCK_SOURCE_NATIVE_REVIEW_PASS' and reviewed['parent_source_preserved']
    for key,value in dict(solved_routes=2,unsolved_routes=2,unsolved_exits=6,zero_byte_save_refusals=14,idle_v2_roundtrips=2,original_delay_ms=5000).items():assert v[key]==p[key]==value
    for key in ('ordinary_entry','first_repeated_completion','unrelated_custom25_excluded','original_round3_exit_completion_preserved','loop_statics_not_manually_reset'):assert v[key] and p[key]
    assert not p['manual_startup_enqueue'] and not p['new_save_format'] and p['actual_audio_driver']=='wasapi'
    log=root/'evidence/p281-native/gateway.log';text=log.read_text();assert d(log)==p['log_sha256']
    assert 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.') and re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
    for marker,count in [('P281 unsolved return: PASS',6),('P281 save refusal: PASS',14),('P281 full gateway route: PASS',2),('P281 unsolved full route: PASS',2),('P281 idle v2 roundtrip: PASS',2),('P281 original blocking voice: S912',2),('P281 original blocking voice: S922',4)]:assert text.count(marker)==count
    for route in (0,1):
        assert f'P281 full gateway route: PASS (route{route},P519,first/repeated count1,' in text
        assert f'P281 unsolved full route: PASS (route{route},P519,first/repeated count2,' in text
        for round_ in (1,2,3):assert re.search(r'P281 unsolved return: PASS \(route%d,round%d,P(?:506|53[1-5]) -> P281,mask\d+ retained\)'%(route,round_),text)
    assert text.count('zero bytes,unchanged runner')==14 and text.count('424 bytes,restored original gateway,custom25 excluded')==2
    assert text.count('Astronomica P519 introduction: S300.WAV')==4 and text.count('P519 entry scripts: 3 queued, 0 skipped')==4
    old=root/'evidence/p281-frozen-v29';proof=json.loads((old/'frozen-v29-proof.json').read_text())
    assert proof['status']=='PASS' and proof['exe_sha256']==expected and proof['origin_commit']=='5000da749a05de7604fd6dc9f0d9313a4aa901bb'
    assert set(proof['cases'])=={'slot%d-%s'%(slot,entry) for slot in (28,29,30) for entry in ('true','false')}
    assert v['genuine_v29_proof_sha256']==d(old/'frozen-v29-proof.json') and proof['actual_audio_driver']=='wasapi'
    hashes={28:'593ba739a24a429cf574bdbd1c2e55a9263d4674ce3305184809c7c7adbf6a75',29:'0fe72555055d995b6f4b89de95cf666286ed0227e0a90cf3915e43928ccee4ce',30:'4ce119a412bf51ac99a952e8e2568b6a72bb921317ed1089861a0407a5a5535d'}
    for label,case in proof['cases'].items():
        assert case['slot']==int(label.split('-')[0][4:])
        assert case['slot_sha256']==hashes[case['slot']] and case['unchanged'] and case['entry_scripts']==label.endswith('-true')
        text=(old/(label+'.log')).read_text();assert d(old/(label+'.log'))==case['log_sha256'] and 'FAIL' not in text and 'introduction:' not in text
        assert 'P512 ASVM29 fresh physical continuation: PASS' in text and text.rstrip().endswith('--- Log closed successfully.') and re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
        if case['slot']!=28:assert ('P512 ordinary final continuation: PASS (priorGlobal%d,P157,count1,'%(case['slot']-29)) in text
    return v,p
