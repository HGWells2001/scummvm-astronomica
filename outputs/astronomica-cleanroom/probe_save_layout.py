"""Execute original successful save-writer path, recording its file writes.

Windows create/close calls are not emulated; the body after successful open is.
The original game files are read only. No player saves are created or changed.
"""
import json,struct,hashlib
import probe_p526_motion as p

code=p.exe[p.base(9):p.base(9)+0x47a0]
ins={i.address:i for i in p.md.disasm(code[0x41eb:0x4267],0x41eb)}
ins.update({i.address:i for i in p.md.disasm(code[0x4362:0x43c2],0x4362)})
def run(place,previous,completed,values,reading=None):
 m=p.Machine();m.reg={'ebp':0x9000,'esp':0x8d00,'esi':7}
 m.write(0xc8c,place);m.write(0xc94,previous);m.write(0x153,completed);m.write(0x7a8,0x2000)
 for index,value in enumerate(values):m.write(0x200a+4*index,value)
 pc=0x4362 if reading is not None else 0x41eb;compare=0;writes=[];position=0
 for _ in range(3000):
  if pc==0x4267:return b''.join(writes)
  if pc==0x43c2:return dict(place=m.read(0xc8c),completed=m.read(0x153),
   values=[m.read(0x200a+4*i) for i in range(100)],bytes_read=position)
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='inc':m.put(i,o[0],v[0]+1)
  elif op=='shl':m.put(i,o[0],v[0]<<v[1])
  elif op=='lea':m.put(i,o[0],m.address(i,o[1]))
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='call':
   assert v[0] in (0x3d2a,0x3d04);m.pop(2) # Compiler's explicit push CS before the near call.
   sp=m.getreg('sp');assert m.read(sp,2)==7
   length=m.read(m.read(sp+2));source=m.read(sp+6);assert length==4
   if v[0]==0x3d2a:writes.append(m.read(source,4).to_bytes(4,'little'))
   else:
    assert len(reading[position:position+4])==4
    m.write(source,int.from_bytes(reading[position:position+4],'little'));position+=4
  elif op in ('jmp','je','jne','jle'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jle':compare<=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('save writer did not finish')

if __name__=='__main__':
 rows=[]
 values=[(i*0x1020304)^0xa5a5a5a5 for i in range(100)]
 for place,previous,completed in ((117,523,12),(408,523,31),(409,524,40),(523,117,0),(1,408,0)):
  raw=run(place,previous,completed,values)
  expected=struct.pack('<102I',previous if place in (408,409) else place,completed,*values)
  assert raw==expected and len(raw)==408
  restored=run(999,999,999,[0]*100,raw)
  assert restored==dict(place=previous if place in (408,409) else place,
   completed=completed,values=values,bytes_read=408)
  rows.append(dict(place=place,previous=previous,completed=completed,bytes=len(raw),
   saved_place=struct.unpack_from('<I',raw)[0],sha256=hashlib.sha256(raw).hexdigest()))
 data_segment=struct.unpack_from('<H',p.exe,p.ne+0xe)[0]
 filenames=[p.exe[p.base(data_segment)+a:p.base(data_segment)+a+20].split(b'\0')[0].decode('ascii') for a in (0x52d,0x580)]
 assert filenames==['gamestat','gamestat']
 output=dict(status='Original save layout research only; native save support not implemented',
  filenames=filenames,original_reader_roundtrips=5,
  writer='9:41b3-4275',reader='9:433e-43d0',writer_body_sha256=hashlib.sha256(code[0x41eb:0x4267]).hexdigest(),
  reader_sha256=hashlib.sha256(code[0x433e:0x43d0]).hexdigest(),cases=rows,
  layout=['uint32le place (previous place for408/409)','uint32le completed puzzle count','100 uint32le global values'],
  omitted=['local conditions','sprite positions','movie time','pending script queue','process random state'])
 p.args.out.write_text(json.dumps(output,indent=2));print('Original save writer/reader:5 roundtrips PASS,102 DWORD/408 bytes each')
