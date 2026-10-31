"""Count P512 only after complete exact-main native evidence exists."""
from pathlib import Path
import hashlib,json,re

def validated_p512(root,work):
    root,work=Path(root),Path(work);path=root/'evidence/p512-saves-validation.json'
    if not path.is_file():return None
    d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    v=json.loads(path.read_text());p=json.loads((root/'evidence/p512-save-proof.json').read_text())
    expected=d(work/'build/Releasex64/scummvm.exe')
    assert v['status']==p['status']=='PASS' and v['full_suite'] and not v['diagnostic'] and not p['diagnostic']
    assert v['exe_sha256']==p['exe_sha256']==expected and v['actual_audio_driver']==p['actual_audio_driver']=='wasapi'
    for item in (v,p):
        assert item['scope']=='stopped_ready_p512' and item['format_version']==29 and item['slot']==28
        assert item['payload_bytes']==item['truncations']==item['corruptions']==9932 and item['packet_words']==2481
        assert item['invalid_states']==27 and item['malformed_runs']==3
        assert item['ordinary_byte_roundtrips']==2 and item['legacy_byte_roundtrips']==item['normal_byte_roundtrips']==12
        assert item['normal_scenarios_per_route']==6 and item['normal_routes']==2 and item['legacy_actual_pause_cells']==48
        for key in ('active_music','paired_engine_pause','recipient_music_effects_preferences','metadata_listed','fresh_entry_true_false','no_intro_replay','final_mask127_first_repeated_fresh','fixtures_unchanged'):assert item[key]
    names={'ordinary.log','fresh-true.log','fresh-false.log','listed.log','legacy.log','all-normal.log'}
    names.update('fresh-final-%d-%s.log'%(slot,entry) for slot in (29,30) for entry in ('true','false'))
    assert v['log_sha256']==p['log_sha256'] and set(p['log_sha256'])==names
    logs=root/'evidence/p512-native'
    for name,sha in p['log_sha256'].items():
        f=logs/name;assert d(f)==sha;text=f.read_text()
        if name=='listed.log':assert 'P512 native stopped continuation' in text
        else:
            assert 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
            assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
            if name.startswith('fresh-'):assert 'P512 ASVM29 fresh physical continuation: PASS' in text and 'introduction:' not in text
    assert (logs/'ordinary.log').read_text().count('Astronomica P512 introduction: S302.WAV')==1
    for name in ('ordinary.log','legacy.log','all-normal.log'):
        assert 'P512 ASVM29 malformed atomic: PASS (9932 truncations,9932 byte flips,27 checksummed fields,' in (logs/name).read_text()
    legacy=(logs/'legacy.log').read_text()
    assert 'P512 pause boundary matrix: PASS (boundaries12,cells48,' in legacy
    assert 'P512 natural boundary audit: PASS (123 rows,12 natural ends,12 settled stopped,' in legacy
    text=(logs/'all-normal.log').read_text()
    assert 'P512 all-normal Music/file verification: PASS' in text and text.count('P512 all-normal Music boundary: PASS')==12
    assert text.count('P512 all-normal original route: PASS')==2
    points=re.findall(r'P512 all-normal Music boundary: PASS \(route(\d+),question(\d+),scenario(\d+),',text)
    assert len(points)==12 and text.count('Astronomica P512 introduction: S302.WAV')==2
    for route in (0,1):
        rows=[(int(q),int(sc)) for rt,q,sc in points if int(rt)==route]
        assert sorted(q for q,sc in rows)==list(range(6)) and sorted(sc for q,sc in rows)==list(range(1,7))
    assert v['final_slots']==p['final_slots'] and set(p['final_slots'])=={'29','30'}
    for slot,prior in [(29,0),(30,1)]:
        final=p['final_slots'][str(slot)]
        assert final['prior_global28']==final['puzzles_completed']==prior and final['mask']==127 and final['active_music']
        assert d(work/('p512-save-regression/normal/astro-verify.%03d'%slot))==final['sha256']
        for entry in ('true','false'):
            text=(logs/('fresh-final-%d-%s.log'%(slot,entry))).read_text()
            assert ('P512 ordinary final continuation: PASS (priorGlobal%d,P157,count1,'%prior) in text
    assert v['slot_sha256']==p['slot_sha256']==d(work/'p512-save-regression/astro-verify.028')
    oldpath=root/'evidence/p512-frozen-v28';old=json.loads((oldpath/'frozen-v28-proof.json').read_text())
    assert d(oldpath/'frozen-v28-proof.json')==v['genuine_v28_proof_sha256']
    assert old['status']=='PASS' and old['exe_sha256']==expected and old['actual_audio_driver']=='wasapi'
    assert old['origin_commit']=='a56d2fd646ac440cf01139db32edc3483f0f25f7' and old['producing_exe_sha256']=='6dd09d6494b2c115579f46718b6c924b6f37c13307343e045e5bb38c87ba0f81'
    assert set(old['cases'])=={kind+'-'+entry for kind in ('frozen-slot27','frozen-ordinary-slot27') for entry in ('true','false')}
    for name,case in old['cases'].items():
        ordinary=name.startswith('frozen-ordinary-')
        assert case['loop_id']==(0 if ordinary else -1) and case['entry_scripts']==name.endswith('-true')
        assert case['slot_sha256']==('4866b333e816f36ec6ce6e80d640d2b2260ec0d52a1a984d31c8f2f35dacbb5f' if ordinary else '3af0c600dba212763a1c8fd26856604f9fab84e72deeafa52904733e8176d6d2')
        assert case['unchanged'] and d(oldpath/(name+'.log'))==case['log_sha256']
        text=(oldpath/(name+'.log')).read_text();assert 'P510 ASVM28 fresh physical continuation: PASS' in text and 'FAIL' not in text and 'introduction:' not in text
        assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi'] and text.rstrip().endswith('--- Log closed successfully.')
    return v,p
