"""Independently verify inventoried command operands against original file bytes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,struct
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('inventory',type=Path);ap.add_argument('--proof',type=Path,required=True);a=ap.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
here=Path(__file__).resolve().parent;j=json.loads(a.inventory.read_text())
assert j['status']=='ORIGINAL_HYP_SYNTACTIC_BRANCH_INVENTORY_ONLY'
layout=json.loads((here/'opcode-layout.json').read_text());widths={r['opcode']:r['reads']for r in layout}
assert j['opcode_layout_sha256']==sha((here/'opcode-layout.json').read_bytes())
files={}
for row in j['scenes']+j['failures']:
    b=(a.root/row['path']).read_bytes();assert sha(b)==row['sha256'];files[row['path']]=b
commands={c['id']:c for c in j['commands']};assert len(commands)==len(j['commands'])
for c in commands.values():
    b=files['PLACES/P%d/MEGAFILE.HYP'%c['scene']];pos=c['file_offset']
    assert struct.unpack_from('<i',b,pos)[0]==c['opcode'];pos+=4
    assert len(c['args'])==len(widths[c['opcode']])
    for expected,width in zip(c['args'],widths[c['opcode']]):
        if width==4:assert struct.unpack_from('<i',b,pos)[0]==expected
        else:
            assert width==255
            text=b[pos:pos+width].split(b'\0')[0].decode('cp1252',errors='replace')
            assert len(text)==expected['text_length']and sha(text.encode('cp1252',errors='replace'))==expected['text_sha256']
        pos+=width
    assert struct.unpack_from('<i',b,pos)[0]==c['delay_ms']
referenced=[];terminators=0
for scene in j['scenes']:
    for script in scene['scripts']:
        body=[j['commands'][index]for index in script['command_indices']]
        referenced.extend(c['id']for c in body)
        for previous,current in zip(body,body[1:]):assert previous['file_offset']+8+sum(widths[previous['opcode']])==current['file_offset']
        if body:
            last=body[-1];end=last['file_offset']+8+sum(widths[last['opcode']]);assert struct.unpack_from('<i',files[scene['path']],end)[0]==0;terminators+=1
        assert script['condition_link_semantics_verified']is False
assert len(referenced)==len(set(referenced))==len(commands)
assert j['summary']['commands']==len(commands)==10316
assert j['summary']['original_files']==len(files)==421
assert j['summary']['parsed_scenes']==420 and len(j['failures'])==1
for tail in j['opaque_tails']:
    b=files[tail['path']][tail['offset']:];assert len(b)==tail['bytes']and sha(b)==tail['sha256']
proof=dict(status='ORIGINAL_HYP_SYNTAX_BYTE_VERIFICATION_PASS',verified_at=datetime.now(timezone.utc).isoformat(),inventory_sha256=sha(a.inventory.read_bytes()),verifier_sha256=sha(Path(__file__).read_bytes()),original_files=421,parsed_scenes=420,commands_verified=10316,nonempty_script_terminators=terminators,raw_opcode_operands_delay_verified=True,original_inputs_match_september_inventory=True,original_execution_observed=False,condition_semantics_verified=False,acceptance_A03_complete=False,whole_game_completion_percent=None,limits=j['limits'])
a.proof.parent.mkdir(parents=True,exist_ok=True);a.proof.write_text(json.dumps(proof,indent=2)+'\n');print('Original-file byte checks PASS:421files,420parsed scenes,10316command records; semantic coverage still open')
