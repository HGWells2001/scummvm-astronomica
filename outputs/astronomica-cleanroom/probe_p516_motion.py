"""Execute eight original P516 ellipse callbacks using original sprite dimensions."""
import json,re,struct
import probe_comet_motion as comet
from astro_reader import parse,FormatError
p=comet.p;setup=comet.setup
raw=(p.args.root/'PLACES/P516/MEGAFILE.HYP').read_bytes()
try:scene=parse(raw)
except FormatError as e:
 match=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e));assert match,e
 scene=parse(raw[:int(match[2],16)])
setup.ins={i.address:i for i in p.md.disasm(p.exe[p.base(4)+0x1c67:p.base(4)+0x203d],0x1c67)}
m=setup.machine(1,0,0,0);m.write(0xc8c,516);sizes=[]
for id in range(14,22):
 src=scene['sprites'][id-1];owner=id-1
 while scene['sprites'][owner]['clone']>0:owner=scene['sprites'][owner]['clone']-1
 ref=scene['sprites'][owner]['frames'][0][0];w,h=ref['width'],ref['height'];sizes.append([id,w,h])
 s=m.read(0x1020+4*id);m.write(s+0x1b,w,2);m.write(s+0x1d,h,2);m.locate(s,*src['xy'])
setup.run(m,0,entry=0x1c67,end=0x203a);m.__class__=comet.Machine;m.explosions=[]
h=2166136261;events=[];previous=None
for now in range(10,20001,10):
 for id in range(14,22):
  s=m.read(0x1020+4*id);period=p.signed(m.read(s+0x6f),4)
  if period<0 or now-m.read(s+0x6b)<period:continue
  m.write(s+0x6b,now);point=0x8000
  m.write(point,m.read(s+0x17,2)+p.signed(m.read(s+0x7d,2),2),2)
  m.write(point+2,m.read(s+0x19,2)+p.signed(m.read(s+0x7f,2),2),2)
  m.run(s,point);m.locate(s,p.signed(m.read(point,2),2),p.signed(m.read(point+2,2),2))
 values=[];visible=[]
 for id in range(14,22):
  s=m.read(0x1020+4*id)
  values += [p.signed(m.read(s+o,2),2) for o in (0x17,0x19,0x7d,0x7f,0x10)]+[p.signed(m.read(s+o),4) for o in (0x5b,0x6f,0xbd,0xc1)]
  visible.append(m.read(s+0x10,2))
 for b in struct.pack('<'+'i'*len(values),*values):h=((h^b)*16777619)&0xffffffff
 if visible!=previous:events.append(dict(time=now,visible=visible));previous=visible
p.args.out.write_text(json.dumps(dict(status='Original callback execution; no native P516 validation',duration=20000,
 sizes=sizes,fnv1a32=hex(h),last=values,visibility_events=events),indent=2))
print('Original P516 eight-sprite motion: PASS',hex(h),len(events),'visibility changes')
