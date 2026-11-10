"""Independently predict fresh variant selections from each serialized original RNG state.

The bounded mathematical model follows pinned original custom17/range instructions.
It is not original Windows execution and does not claim unvisited game coverage.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,struct
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';fresh=w/'p281-persistent-fresh-nov10';producer=w/'p281-persistent-native-nov10e'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
exe=Path('D:/astro/SETUP/ASTRO.EXE').read_bytes();assert sha(exe)=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
ne=struct.unpack_from('<I',exe,60)[0];table=ne+struct.unpack_from('<H',exe,ne+0x22)[0];shift=struct.unpack_from('<H',exe,ne+0x32)[0]
base=lambda n:struct.unpack_from('<H',exe,table+8*(n-1))[0]<<shift
handler=exe[base(4)+0x385b:base(4)+0x3a3c];reference=read(o/'evidence/variants.json');assert sha(handler)==reference['handler_sha256']
assert exe[base(4)+0x38f8:base(4)+0x3902]==bytes.fromhex('b8 06 00 2b 06 4b 01 50 6a 01')
assert exe[base(1)+0xb75]==0xba and exe[base(1)+0xb78]==0xb8
multiplier=(struct.unpack_from('<H',exe,base(1)+0xb76)[0]<<16)|struct.unpack_from('<H',exe,base(1)+0xb79)[0];assert multiplier==0x15a4e35
f=read(fresh/'proof.json');p=read(producer/'proof.json');assert f['status']=='P281_ASVM32_FRESH_PROCESS_CONTINUATION_PASS';rows=[]
for case in f['cases']:
 slot=case['slot'];data=(producer/'saves'/f'astro-verify.{slot:03}').read_bytes();assert sha(data)==case['physical_save_sha256'];words=struct.unpack_from('<661I',data,8)
 state=words[39+600];round_=words[39+603];mask=words[39+604];expected=[];draws=[]
 for current in range(round_,3):
  available=[bit for bit in range(6)if not(mask&(1<<bit))];assert len(available)==6-current
  state=(state*multiplier+1)&0xffffffff;draw=(state>>16)&32767;selected=available[draw*len(available)//32768];mask|=1<<selected
  expected.append(506 if selected==0 else 530+selected);draws.append(draw)
 log=fresh/f"slot{slot}-entry{int(case['initial_entry_scripts'])}"/'native.log';text=log.read_text()
 actual=[int(place)for place in re.findall(r'resource explorer: P(\d+);',text)if int(place)in(506,531,532,533,534,535)]
 assert actual==expected,(slot,expected,actual)
 assert 'resource explorer: P519;'in text
 rows.append(dict(slot=slot,initial_entry_scripts=case['initial_entry_scripts'],serialized_rng_state=words[639],initial_round=round_,initial_mask=words[643],predicted_original_range_draws=draws,predicted_selected_scenes=expected,actual_selected_scenes=actual,log_sha256=sha(log.read_bytes())))
assert len(rows)==12
proof=dict(status='P281_RETAINED_SERIALIZED_RNG_FUTURES_PASS',verified_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=f['candidate_exe_sha256'],original_executable_sha256=sha(exe),original_custom17_handler_sha256=sha(handler),original_rng_multiplier=multiplier,fresh_proof_sha256=sha((fresh/'proof.json').read_bytes()),cases=rows,limits=['Independent bounded selection model from original custom17/RNG instructions; not original Windows execution','Only six physical saved states/twelve continuations; no whole-game coverage claim'])
(w/'p281-retained-rng-future-nov10.json').write_text(json.dumps(proof,indent=2)+'\n');print('Independent serialized RNG predictions match12 fresh continuations')
