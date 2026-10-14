"""Original menu help/resume calls and text gamestat I/O, from ASTRO.EXE.

The successful file-open branches and libc formatted I/O are modeled. The
original writer/reader loop instructions execute; no original files are changed.
"""
import hashlib,json,struct
import probe_p526_motion as p
from astro_reader import parse
names={(s['segment'],s['offset']):s['name'] for s in json.loads((p.Path(__file__).parent/'evidence/debug/symbols.json').read_text())}
def target(seg,address):
 size=struct.unpack_from('<H',p.exe,p.table+8*(seg-1)+2)[0]
 for j in range(struct.unpack_from('<H',p.exe,p.base(seg)+size)[0]):
  typ,flags,src,a,b=struct.unpack_from('<BBHHH',p.exe,p.base(seg)+size+2+8*j);seen=set()
  while src!=65535 and src not in seen and src+2<=size:
   seen.add(src)
   if src==address:return dict(flags=flags,segment=a,offset=b,name=names.get((a,b)))
   if flags&4:break
   src=struct.unpack_from('<H',p.exe,p.base(seg)+src)[0]
 raise AssertionError((seg,address))
def string(a):return p.exe[p.base(20)+a:p.base(20)+a+100].split(b'\0')[0].decode('ascii')
assert string(0x559)=='gamestat' and string(0x564)=='C:gamestat'
assert string(0x562)==string(0x56f)=='r'
assert string(0x501)=='gamestat' and string(0x50c)=='C:gamestat'
assert string(0x50a)==string(0x517)=='w'
assert all(string(a)=='%ld\n' for a in (0x519,0x51e,0x523,0x528,0x571,0x576,0x57b))
assert target(4,0x6a04)['name']=='_read_globals'
assert target(4,0x5159)['name']=='_process_help'
assert string(0x4ec)=='%s/HELP/ASTRONOM.HLP'
code=p.exe[p.base(9):p.base(9)+0x47a0]
ins={i.address:i for a,b in ((0x410f,0x41ac),(0x42ba,0x4337)) for i in p.md.disasm(code[a:b],a)}
def run(place,previous,completed,values,reading=None):
 m=p.Machine();m.reg={'ebp':0x9000,'esp':0x8d00}
 m.write(0xc8c,place);m.write(0xc94,previous);m.write(0x153,completed);m.write(0x7a8,0x2000)
 m.write(0x9000-0xe,0xbeef)
 for index,value in enumerate(values):m.write(0x200a+4*index,value)
 pc=0x42ba if reading is not None else 0x410f;compare=0;writes=[];position=0
 tokens=[] if reading is None else reading.split()
 for _ in range(3000):
  if pc==0x41ac:return ''.join(writes)
  if pc==0x4337:return dict(place=m.read(0xc8c),completed=m.read(0x153),values=[m.read(0x200a+4*i) for i in range(100)],tokens_read=position)
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='inc':m.put(i,o[0],v[0]+1)
  elif op=='shl':m.put(i,o[0],v[0]<<v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[1].size)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='lcall':
   sp=m.getreg('sp');assert m.read(sp)==0xbeef
   if i.address in (0x41a4,0x432f):continue # fclose; add sp follows in original.
   assert string(m.read(sp+4,2))=='%ld\n'
   if i.address in (0x4147,0x415e,0x418b):writes.append(str(p.signed(m.read(sp+8),4))+'\n')
   else:
    assert i.address in (0x42d0,0x42e6,0x4316)
    value=int(tokens[position]);assert -2147483648<=value<=2147483647
    m.write(m.read(sp+8,2),value&0xffffffff);position+=1
  elif op in ('jmp','je','jne','jle'):
   if {'jmp':True,'je':compare==0,'jne':compare!=0,'jle':compare<=0}[op]:pc=v[0]
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('text I/O loop did not finish')
rows=[]
for place,previous,completed in ((117,523,12),(408,523,31),(409,524,40),(523,117,0),(1,408,0)):
 values=[(i*0x1020304)^0xa5a5a5a5 for i in range(100)]
 raw=run(place,previous,completed,values)
 expected=[previous if place in (408,409) else place,completed,*values]
 assert raw==''.join(str(p.signed(v,4))+'\n' for v in expected)
 for whitespace in ('\n','\r\n',' \t'):
  text=whitespace.join(raw.split());restored=run(999,999,999,[0]*100,text)
  assert restored==dict(place=expected[0],completed=completed,values=values,tokens_read=102)
 rows.append(dict(place=place,saved_place=expected[0],completed=completed,sha256=hashlib.sha256(raw.encode()).hexdigest()))
# Startup's resume flag is based on the first TEXT value. The original
# permits27..422 and >437, without proving that the rest of the file is valid.
startup=p.exe[p.base(18):p.base(18)+0x412]
resume_ins={i.address:i for a,b in ((0x369,0x392),(0x3d3,0x3fc)) for i in p.md.disasm(startup[a:b],a)}
def resume_flag(place,fallback):
 m=p.Machine();m.reg={'ebp':0x9000};m.write(0x9000-0x18,place)
 pc=0x3d3 if fallback else 0x369;end=0x3fc if fallback else 0x392;compare=0
 for _ in range(20):
  if pc==end:return m.read(0x7a0,2)
  i=resume_ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o]
  if i.mnemonic=='cmp':compare=p.signed(v[0],4)-p.signed(v[1],4)
  elif i.mnemonic=='mov':m.put(i,o[0],v[1])
  elif {'jmp':True,'jl':compare<0,'jg':compare>0,'jle':compare<=0}[i.mnemonic]:pc=v[0]
 raise AssertionError('startup flag branch did not finish')
resume_cases=0
for place in [*range(-2,540),-2147483648,2147483647]:
 for fallback in (False,True):
  assert resume_flag(place,fallback)==int(27<=place<=422 or place>437);resume_cases+=1
assert string(0x82a)=='GAMESTAT' and string(0x83a)=='C:GAMESTAT'
regions={}
for seg,a,b in ((4,0x50e8,0x5163),(4,0x6a03,0x6a10),(9,0x4016,0x408c),(9,0x40c9,0x41b3),(9,0x4275,0x433e),(18,0x338,0x412)):
 regions[f'{seg}:{a:04x}-{b:04x}']=dict(sha256=hashlib.sha256(p.exe[p.base(seg)+a:p.base(seg)+b]).hexdigest(),instructions=[f'{i.address:04x} {i.mnemonic} {i.op_str}' for i in p.md.disasm(p.exe[p.base(seg)+a:p.base(seg)+b],a)])
result=dict(status='Original menu services research; native custom22/33 not yet implemented',
 correction='Custom33 calls text _read_globals at9:4275, NOT binary _read_globals_save at9:433e. Binary layout research remains valid for that separate function.',
 original_text_roundtrips=15,original_resume_flag_cases=resume_cases,
 startup_resume_flag="18:0369 and18:03d3; scene27..422 or >437; only first text value checked",format='102 signed decimal long values separated by whitespace: scene, completed count, 100 globals',
 original_paths=['gamestat','C:gamestat'],custom33=[target(4,0x6a04),'Sets scene-change flag DS:0c98 unconditionally after read'],
 custom22_calls=[target(4,a) for a in (0x5118,0x5129,0x513c,0x5147,0x5151,0x5159)],
 help='Builds %s/HELP/ASTRONOM.HLP; calls USER ordinal171 (WinHelp) command2 then command9; sets help-requested flag DS:079a',
 help_imports=[target(9,0x404a),target(9,0x4078)],cases=rows,regions=regions)
p.args.out.write_text(json.dumps(result,indent=2));print('Original text gamestat:15 roundtrips PASS; custom22/33 dispatch resolved')
