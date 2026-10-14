"""Execute original custom28 save/restore instructions and check opcode35."""
import json,hashlib,struct
import probe_p526_motion as p
ins={i.address:i for i in p.md.disasm(p.exe[p.base(4)+0x6804:p.base(4)+0x688c],0x6804)}
def run(m,mode):
 pc=0x6804 if mode==0 else 0x6841;m.reg={'ebp':0x9000};compare=0
 for _ in range(500):
  if pc==0x6889:return
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,a) for a in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='inc':m.put(i,o[0],v[0]+1)
  elif op=='shl':m.put(i,o[0],v[0]<<v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[1].size)
  elif op in ('jmp','jne','jle'):
   if {'jmp':True,'jne':compare!=0,'jle':compare<=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('did not return')
rows=[]
for mode in (0,1):
 for previous in (0,117,408,524):
  for seed in (0,1,9,-1):
   m=p.Machine();m.write(0xc88,0x2000);m.write(0x7a8,0x4000);m.write(0xc94,previous)
   local=[seed+i*31 for i in range(100)];glob=[seed-i*7 for i in range(100)]
   for i in range(100):m.write(0x23f8+4*i,local[i]);m.write(0x400a+4*i,glob[i])
   run(m,mode)
   if mode==0:glob[10:20]=local[:10]
   elif previous==408:local[:10]=glob[10:20]
   actualL=[p.signed(m.read(0x23f8+4*i),4) for i in range(100)];actualG=[p.signed(m.read(0x400a+4*i),4) for i in range(100)]
   assert actualL==local and actualG==glob
   rows.append(dict(mode=mode,previous=previous,seed=seed,local=actualL[:10],globals10_19=actualG[10:20]))
symbols=json.loads((p.Path(__file__).parent/'evidence/debug/symbols.json').read_text());execute=next(x for x in symbols if x['name']=='_execute_command');base=execute['file_offset']-execute['offset']
assert p.exe[base+0x2ee:base+0x2f4]==bytes.fromhex('c706d1010000')
p.args.out.write_text(json.dumps(dict(status='Original evidence; native checks separate',cases=len(rows),case_sha256=hashlib.sha256(json.dumps(rows).encode()).hexdigest(),rows=rows,opcode35='Writes zero to DS:01d1, _restrict_cursor; no other effect'),indent=2))
print('Original P524 state: PASS',len(rows),'save/restore cases, 100 locals/globals checked each; opcode35 verified')
