"""Run original P514 ellipse and region instructions; no C++ engine dependency."""
import json,struct,hashlib
import probe_p526_motion as p
from astro_reader import parse

region_ins={i.address:i for i in p.md.disasm(p.exe[p.base(3)+0x3755:p.base(3)+0x39a8],0x3755)}
constants={off:struct.unpack_from('<d',p.exe,p.base(20)+off)[0] for off in (0x10c,0x114,0x11c,0x124)}
assert list(constants.values())==[1.732,0.577,-1.732,-0.577]

class Machine(p.Machine):
    def custom_call(self,address,sp):
        target=self.read(sp)
        if address==0x3752:self.locate(target,p.signed(self.read(sp+4,2),2),p.signed(self.read(sp+6,2),2))
        elif address in (0x3773,0x379a,0x37bf,0x37e4,0x3809):
            x=p.signed(self.read(sp+4,2),2);y=p.signed(self.read(sp+6,2),2)
            r=[p.signed(self.read(target+o,2),2) for o in (0x17,0x19,0x1b,0x1d)]
            self.setreg('ax',int(r[0]<=x<=r[2] and r[1]<=y<=r[3]))
        elif address==0x3815:self.cancelled=True
        elif address in (0x3837,0x384e):self.write(target+0x202,self.read(sp+4),4)
        else:raise AssertionError(('custom call',hex(address)))
    def call_region(self,cx,cy,outer,inner,x,y):
        m=p.Machine(); bp=0x9000; m.setreg('bp',bp)
        for j,v in enumerate((cx,cy,outer,inner,x,y)):m.write(bp+6+4*j,v)
        pc=0x3755; compare=0; fp=[]
        for _ in range(150):
            if pc==0x39a7:return m.getreg('ax')|(m.getreg('dx')<<16)
            i=region_ins[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[m.value(i,t) for t in o]
            if op=='mov':m.put(i,o[0],v[1])
            elif op in ('add','sub','xor'):
                r=v[0]+v[1] if op=='add' else v[0]-v[1] if op=='sub' else v[0]^v[1]
                m.put(i,o[0],r);compare=p.signed(r,o[0].size)
            elif op=='imul':m.put(i,o[0],p.signed(v[0],4)*p.signed(v[1],4))
            elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
            elif op=='fild':fp.append(p.signed(v[0],4))
            elif op=='fmul':fp[-1]*=constants[m.address(i,o[0])]
            elif op=='fcompp':a=fp.pop();b=fp.pop();compare=a-b
            elif op in ('wait','nop','fnstsw','sahf'):pass
            elif op in ('jmp','jl','jle','jae','jbe'):
                if {'jmp':True,'jl':compare<0,'jle':compare<=0,'jae':compare>=0,'jbe':compare<=0}[op]:pc=v[0]
            else:raise AssertionError((hex(i.address),op))
        raise AssertionError('region did not return')

def region(x,y):
    dx=x-295;dy=140-y
    if dx*dx+dy*dy>256*256:return 0
    if dx>=0 and dy>=0:return 1 if dx*1.732<dy else 2 if dx*.577<dy else 3
    if dx>=0:return 6 if dx*-1.732>dy else 5 if dx*-.577>dy else 4
    if dy>=0:return 12 if dx*-1.732<dy else 11 if dx*-.577<dy else 10
    return 7 if dx*1.732>dy else 8 if dx*.577>dy else 9

if __name__ == '__main__':
    m=Machine();region_hash=2166136261
    for y in range(-120,401,4):
        for x in range(35,556,4):
            result=m.call_region(295,140,256,0,x,y);assert result==region(x,y),(x,y,result,region(x,y))
            region_hash=((region_hash^result)*16777619)&0xffffffff

    scene=parse((p.args.root/'PLACES/P514/MEGAFILE.HYP').read_bytes())
    traces=[]
    for id in (17,19):
        m=Machine();place=0x1000;s=0x3000;point=0x8000
        m.write(0xc88,place);m.write(0xc8c,514);m.write(place+0x20+4*id,s)
        frame=scene['sprites'][id-1]['frames'][0]
        width,height=frame[0]['width'],frame[0]['height']
        assert all(f[0]['width']==width and f[0]['height']==height for f in scene['sprites'][id-1]['frames'])
        m.write(s+0x1b,width,2);m.write(s+0x1d,height,2)
        m.locate(s,*scene['sprites'][id-1]['xy']);m.write(s+0x10,1,2)
        for off,value in ((0xa5,295),(0xa9,140),(0xb1,145),(0xb5,145)):m.write(s+off,value)
        m.write(s+0x7d,2,2);h=2166136261;first=[]
        for tick in range(1000):
            m.write(point,m.read(s+0x17,2)+p.signed(m.read(s+0x7d,2),2),2)
            m.write(point+2,m.read(s+0x19,2)+p.signed(m.read(s+0x7f,2),2),2)
            m.callback(s,point,ellipse=True)
            m.locate(s,p.signed(m.read(point,2),2),p.signed(m.read(point+2,2),2))
            row=[p.signed(m.read(s+off,size),size) for off,size in ((0x17,2),(0x19,2),(0x7d,2),(0x7f,2),(0x5b,4))]
            for value in row:
                for b in struct.pack('<i',value):h=((h^b)*16777619)&0xffffffff
            if tick<4:first.append(row)
        traces.append(dict(sprite=id,width=width,height=height,ticks=1000,fnv1a32=hex(h),first=first,last=row,instructions=m.steps))
    saved_ins=p.ins
    p.ins={i.address:i for i in p.md.disasm(p.exe[p.base(4)+0x366e:p.base(4)+0x385b],0x366e)}
    collision_hash=2166136261;cases=0;hits=0
    for shipx in (150,200,295,400):
     for dx in (-53,-52,-37,-26,-1,0,56,57):
      for dy in (-55,-54,-27,-1,0,56,57):
       m=Machine();m.cancelled=False;place=0x1000;m.write(0xc88,place)
       for id,w,h in ((14,18,9),(17,52,54),(19,56,56),(20,15,28)):
        s=0x2000+id*0x300;m.write(place+0x20+4*id,s);m.write(s+0x1b,w,2);m.write(s+0x1d,h,2)
       target=m.read(place+0x64);ship=m.read(place+0x6c)
       tx=shipx+dx;ty=50+dy;m.locate(target,tx,ty);m.locate(ship,shipx,50)
       m.callback(0,0,entry=0x366e)
       pts=((tx,ty),(tx+52,ty),(tx,ty+54),(tx+52,ty+54),(tx+26,ty+27))
       expected=any(shipx<=x<=shipx+56 and 50<=y<=106 for x,y in pts)
       hit=m.read(place+0x410)
       assert hit==expected and m.cancelled==expected,(shipx,dx,dy,hit,expected,m.cancelled)
       assert (m.read(ship+0x202)==0xffffffff)==expected
       collision_hash=((collision_hash^hit)*16777619)&0xffffffff;cases+=1;hits+=hit
    p.ins=saved_ins
    p.args.out.write_text(json.dumps(dict(scene=514,region_grid_cases=131*131,region_hash=hex(region_hash),traces=traces,constants=constants,
     collision=dict(cases=cases,hits=hits,fnv1a32=hex(collision_hash),probe_y='ship.right; moved sprite20 is not the tested sprite19',code_sha256=hashlib.sha256(p.exe[p.base(4)+0x366e:p.base(4)+0x385b]).hexdigest())),indent=2))
    print('Original P514 motion: PASS',traces)

