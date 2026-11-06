"""Execute the original bounded pending-delay predicate on controlled clock inputs."""
from pathlib import Path
import argparse,collections,hashlib,json,struct,sys
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('inventory',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sys.path.insert(0,str(Path('work/fresh-20260913/deps-verified').resolve()))
import capstone
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
from capstone.x86_const import X86_OP_IMM,X86_OP_REG
sha=lambda b:hashlib.sha256(b).hexdigest()
b=(a.root/'SETUP/ASTRO.EXE').read_bytes();assert sha(b)=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
ne=struct.unpack_from('<I',b,0x3c)[0];tab=ne+struct.unpack_from('<H',b,ne+0x22)[0];shift=struct.unpack_from('<H',b,ne+0x32)[0];base=struct.unpack_from('<H',b,tab+14*8)[0]<<shift
md=Cs(CS_ARCH_X86,CS_MODE_16);md.detail=True;raw=b[base+0x1b7e:base+0x1ba1];ins={i.address:i for i in md.disasm(raw,0x1b7e)}
assert ins[0x1b90].mnemonic=='sub'and ins[0x1b9d].mnemonic=='jl'
steps=0
def due(delay,since,now):
 global steps
 reg={'eax':0,'bx':0,'es':0};pc=0x1b7e;comparison=(0,0)
 def value(i,o):
  if o.type==X86_OP_IMM:return o.imm&0xffffffff
  if o.type==X86_OP_REG:return reg[i.reg_name(o.reg)]
  key=(i.reg_name(o.mem.base),o.mem.disp)
  return {('bp',-0xe):0x40000010,('bp',-0x1a):now,('bx',0x30):since,('bx',0x34):delay&0xffffffff}[key]
 signed=lambda v:(v&0xffffffff)-0x100000000 if(v&0xffffffff)&0x80000000 else(v&0xffffffff)
 while pc not in(0x1ba1,0x1c4d):
  i=ins[pc];o=i.operands;following=pc+i.size;steps+=1
  if i.mnemonic=='les':p=value(i,o[1]);reg['bx']=p&65535;reg['es']=p>>16
  elif i.mnemonic=='mov':reg[i.reg_name(o[0].reg)]=value(i,o[1])
  elif i.mnemonic=='sub':key=i.reg_name(o[0].reg);reg[key]=(reg[key]-value(i,o[1]))&0xffffffff
  elif i.mnemonic=='cmp':comparison=(signed(value(i,o[0])),signed(value(i,o[1])))
  elif i.mnemonic in('je','jl'):
   if(i.mnemonic=='je'and comparison[0]==comparison[1])or(i.mnemonic=='jl'and comparison[0]<comparison[1]):following=value(i,o[0])
  else:raise AssertionError((hex(pc),i.mnemonic))
  pc=following
 return int(pc==0x1ba1)
j=json.loads(a.inventory.read_text());counts=collections.Counter(c['delay_ms']for c in j['commands']);assert len(counts)==83 and sum(n for d,n in counts.items()if d>0)==1593
rows=[]
for delay in sorted(counts):
 diffs={0,1,0x7fffffff,0x80000000,0xffffffff}
 diffs.update((delay+delta)&0xffffffff for delta in(-1,0,1))
 for since in(0,1,0x7fffffff,0xffff0000,0xfffffff0):
  for delta in sorted(diffs):
   now=(since+delta)&0xffffffff;rows.append((delay,since,now,due(delay,since,now)))
data=bytearray(b'TDUE0001')+struct.pack('<I',len(rows))
for row in rows:data.extend(struct.pack('<iIII',*row))
a.out.mkdir(exist_ok=False,parents=True);(a.out/'fixture.bin').write_bytes(data)
proof=dict(status='ORIGINAL_PENDING_DELAY_INSTRUCTION_ORACLE_READY',instruction_oracle=True,original_exe_sha256=sha(b),inventory_sha256=sha(a.inventory.read_bytes()),author_sha256=sha(Path(__file__).read_bytes()),capstone_version=capstone.__version__,original_range='15:1b7e-1ba1',range_sha256=sha(raw),distinct_delays=83,positive_delay_occurrences=1593,cases=len(rows),instruction_steps=steps,fixture_sha256=sha(data),delay_occurrences=dict(sorted(counts.items())),snapshot_loop_observation='Original15:1b40copies initial pending count into local bp-0xa;15:1c65compares loop counter to that local, independently of global count changes',limits=['Only the due/not-due predicate is replayed; original Windows program not run','Clock and command-field values are controlled inputs; no real audio or complete timed-gameplay claim','Queue ownership/cancellation and actual native effects remain outside this predicate test','Half-range and wrap cases test the original signed32bit arithmetic policy, not reachable game states'])
(a.out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Original delay oracle:',len(rows),'cases across83delay values')
