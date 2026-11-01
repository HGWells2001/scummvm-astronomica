"""Validate deterministic stopped-clock regressions without changing ASVM29."""
from pathlib import Path
import hashlib,json,re

ENDS=(150,354,1456,1642,1831,1919)

def validate_log(text,scenarios):
    rows=re.findall(r'P512 stopped clock domain: PASS \(scenario(\d+),clock(\d+),current(\d+),presented(\d+),end(\d+),literal prepare/install/recapture\)',text)
    expected={(s,c) for s in scenarios for c in (0,ENDS[s-1]*1000//30-1)}
    if 3 in scenarios:expected.add((3,48529))
    assert len(rows)==len(expected) and {(int(s),int(c)) for s,c,*_ in rows}==expected
    for scenario,clock,current,presented,end in rows:
        assert int(end)==ENDS[int(scenario)-1] and int(current)<643
        assert int(presented)<643 or int(presented)==0xffffffff
    invalid=re.findall(r'P512 stopped clock invalid domain: PASS \(scenario(\d+),upper/range/current/presented refusals5,source restored\)',text)
    assert len(invalid)==len(scenarios) and set(map(int,invalid))==set(scenarios)
    assert 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.')
    assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']

def validate_native(proof_path,logs,expected):
    proof_path,logs=Path(proof_path),Path(logs)
    p=json.loads(proof_path.read_text())
    assert p['status']=='PASS' and p['exe_sha256']==expected and p['format_version']==29
    assert p['actual_audio_driver']=='wasapi'
    for name,scenarios in [('ordinary.log',{3}),('legacy.log',set(range(1,7))),('all-normal.log',set(range(1,7)))]:
        path=logs/name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==p['log_sha256'][name]
        validate_log(path.read_text(),scenarios)
    return p
