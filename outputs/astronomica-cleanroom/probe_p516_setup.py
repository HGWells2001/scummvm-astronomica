"""Execute original custom9 setup/launch; do not infer playable support."""
import json,hashlib
import probe_comet_state as setup
p=setup.p
setup.ins={i.address:i for i in p.md.disasm(p.exe[p.base(4)+0x1c67:p.base(4)+0x203d],0x1c67)}
rows=[]
for mode in (0,1):
 for direction in range(1,5):
  for speed in range(16):
   m=setup.machine(direction,speed,0,0)
   setup.run(m,mode,entry=0x1c67 if mode==0 else 0x1f43,end=0x203a)
   rows.append(dict(input=[mode,direction,speed],**setup.snapshot(m)))
p.args.out.write_text(json.dumps(dict(status='Original custom9 execution; not native validation',cases=len(rows),rows=rows,
 code_sha256=hashlib.sha256(p.exe[p.base(4)+0x1c36:p.base(4)+0x203d]).hexdigest()),indent=2))
print('Original P516 setup:',len(rows),'cases PASS')
