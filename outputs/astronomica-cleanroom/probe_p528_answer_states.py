"""Derive the answer-state table by stepping the original Win16 instructions.

This is an analysis tool for one immutable handler, not a game runtime.
Unknown instructions fail closed; the far audio call is recorded, not run.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,re,sys
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True)
ap.add_argument('--deps',type=Path,default=Path('work/fresh-20260913/deps-verified'));a=ap.parse_args()
sys.path.insert(0,str(a.deps.resolve()))
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
from astro_reader import parse
exe=(a.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
symbols=json.loads((Path(__file__).parent/'evidence/debug/symbols.json').read_text())
symbol=next(x for x in symbols if x['name']=='_do_custom');base=symbol['file_offset']-symbol['offset']
start,end=0x444c,0x4523;raw=exe[base+start:base+end]
instructions={i.address:i for i in Cs(CS_ARCH_X86,CS_MODE_16).disasm(raw,start)}
assert sum(i.size for i in instructions.values())==len(raw)
resource=(a.root/'PLACES/P528/MEGAFILE.HYP').read_bytes();scene=parse(resource)
assert scene['conditions']==[[1,0,13,11,0,13],[1,1,4,0,0,4],[1,2,4,0,0,4],[1,3,1,0,0,1],[1,4,1,0,0,1]]
quiz=scene['sprites'][6]['click']
assert any(c['opcode']==23 and c['args']==[18,1,0,0,0,0] for c in quiz)
assert any(c['opcode']==31 and c['args']==[1,2,1,0,0,0] and c['delay']==400 for c in quiz)
assert any(c['opcode']==5 and c['args']==[526] and c['delay']==4500 for c in quiz)
coverage=set()
def run(phase,quadrant,first,second):
 memory={0x3f8:phase,0x3fc:quadrant,0x400:0,0x404:first,0x408:second}
 pc=start;equal=None;stack=[];sounds=[];trace=[]
 for step in range(80):
  if pc==0x6a10:break
  ins=instructions[pc];coverage.add(pc);trace.append(pc);next_pc=pc+ins.size
  if ins.mnemonic=='les':assert ins.op_str=='bx, ptr [0xc88]'
  elif ins.mnemonic in ('cmp','mov'):
   match=re.fullmatch(r'dword ptr es:\[bx \+ (0x[0-9a-f]+)\], (0x[0-9a-f]+|\d+)',ins.op_str)
   assert match,(ins.mnemonic,ins.op_str)
   address,value=int(match[1],0),int(match[2],0);assert address in memory
   if ins.mnemonic=='cmp':equal=memory[address]==value
   else:memory[address]=value
  elif ins.mnemonic in ('je','jne','jmp'):
   if ins.mnemonic=='jmp' or (equal if ins.mnemonic=='je' else not equal):next_pc=int(ins.op_str,0)
  elif ins.mnemonic=='push':stack.append(int(ins.op_str,0))
  elif ins.mnemonic=='lcall':
   assert ins.op_str=='0, 0xffff' and len(stack)==1
   sounds.append(stack[-1])
  elif ins.mnemonic=='pop':assert ins.op_str=='cx';stack.pop()
  else:raise AssertionError((hex(pc),ins.mnemonic,ins.op_str))
  pc=next_pc
 else:raise AssertionError('handler did not leave its bounded span')
 assert not stack and len(sounds)==1 and memory[0x3f8]==phase and memory[0x3fc]==quadrant
 return dict(phase=phase,quadrant=quadrant,before=[first,second],after=[memory[0x404],memory[0x408]],result=memory[0x400],sound=sounds[0],trace=[f'{p:04x}' for p in trace])
cases=[run(*x) for x in itertools.product(range(12),range(4),range(2),range(2))]
assert len(cases)==192 and coverage==set(instructions)
for row in cases:
 first,second=row['after'];assert row['result']==int(bool(first and second))
 assert all(after>=before for before,after in zip(row['before'],row['after']))
 assert row['sound'] in (8,9,10)
settled=[r for r in cases if r['before']!=[1,1]]
assert len(settled)==144 and sum(r['result'] for r in settled)==4
first_pairs=sorted({(r['phase'],r['quadrant']) for r in cases if r['sound']==8})
second_pairs=sorted({(r['phase'],r['quadrant']) for r in cases if r['sound']==9})
assert first_pairs==[(0,1),(6,3)] and second_pairs==[(0,3),(6,1)]
report=dict(date='2026-10-18',status='PASS',scope='Static original Win16 handler instruction stepping; no native save/load coverage claim',
 executable_sha256=hashlib.sha256(exe).hexdigest(),resource_sha256=hashlib.sha256(resource).hexdigest(),
 handler_segment=4,handler_span=['444c','4523'],handler_sha256=hashlib.sha256(raw).hexdigest(),instruction_count=len(instructions),instructions_covered=len(coverage),
 cases=cases,case_count=len(cases),settled_input_combinations=len(settled),completion_edges_from_settled_inputs=4,
 first_flag_pairs=first_pairs,second_flag_pairs=second_pairs,
 original_completion_condition_delay_ms=400,original_completion_destination_delay_ms=4500,original_completion_destination=526,
 settled_state_inference='local2=0 and not(local3=1 and local4=1); completion enqueues departure, so an idle save must not admit both flags',
 audio_call_policy='Record the pushed file ID; do not execute a far call or emulate WAV playback',
 instructions=[dict(address=f'{i.address:04x}',bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in instructions.values()])
a.out.write_text(json.dumps(report,indent=2))
print(f'P528 original answer states PASS: {len(cases)} cases, {len(coverage)} instructions, 144 settled inputs, four completion edges')
