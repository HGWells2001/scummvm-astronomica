"""Execute original custom32. Only the imported clock return is supplied."""
import json,hashlib
import probe_p526_motion as p
code=p.exe[p.base(4):p.base(4)+0x6a10]
ins={i.address:i for i in p.md.disasm(code[0x69c8:0x6a01],0x69c8)}
def run(solved,previous,flag,now):
 m=p.Machine();m.reg={'ebp':0x9000,'esp':0x8d00};m.write(0x7a8,0x7000)
 m.write(0x70be,solved);m.write(0x702a,previous);m.write(0x70fa,flag)
 pc=0x69c8;compare=0;calls=0
 for _ in range(50):
  if pc==0x6a01:return [m.read(0x702a),m.read(0x70fa),calls]
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='cmp':compare=v[0]-v[1]
  elif op=='jne':
   if compare:pc=v[0]
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='pop':m.put(i,o[0],m.pop(o[0].size))
  elif op=='lcall':
   assert i.address==0x69ef
   m.setreg('ax',now&65535);m.setreg('dx',now>>16);calls+=1
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('custom32 did not finish')
if __name__=='__main__':
 rows=[];h=2166136261
 for solved in (0,1,2):
  for previous in (0,1,0xffffffff):
   for flag in (0,1,2):
    for now in (0,1,0x12345678,0xffffffff):
     result=run(solved,previous,flag,now)
     rows.append(dict(solved=solved,previous=previous,flag=flag,now=now,result=result))
     for value in result:h=((h^value)*16777619)&0xffffffff
 p.args.out.write_text(json.dumps(dict(status='Original custom32 research only; not integrated',
  cases=len(rows),fnv1a=f'{h:08x}',clock='MMSYSTEM ordinal607 (timeGetTime)',
  code_sha256=hashlib.sha256(code[0x69c8:0x6a01]).hexdigest(),rows=rows),indent=2))
 print(f'Original custom32: {len(rows)} cases, FNV {h:08x}')
