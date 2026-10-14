"""Execute P526 orbit callbacks from ASTRO.EXE with a narrow x86 interpreter.

SpriteWorld calls are modeled as their observed rectangle/timer setters. The
ellipse arithmetic, quadrant branches, visibility and stop decisions run from
original machine instructions, independently of the C++ engine implementation.
"""
import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('root', type=Path)
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--deps', type=Path, default=Path('work/fresh-20260913/deps-verified'))
args = ap.parse_args()
sys.path.insert(0, str(args.deps.resolve()))
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
from capstone.x86_const import X86_OP_REG, X86_OP_IMM, X86_OP_MEM

exe = (args.root/'SETUP/ASTRO.EXE').read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
ne = struct.unpack_from('<I', exe, 0x3c)[0]
table = ne + struct.unpack_from('<H', exe, ne+0x22)[0]
shift = struct.unpack_from('<H', exe, ne+0x32)[0]
def base(segment):
    return struct.unpack_from('<H', exe, table+8*(segment-1))[0] << shift
md = Cs(CS_ARCH_X86, CS_MODE_16)
md.detail = True
ins = {i.address:i for i in md.disasm(exe[base(3)+0x1199:base(3)+0x33e5],0x1199)}
conversion = list(md.disasm(exe[base(1)+0x15c3:base(1)+0x15ef],0x15c3))
assert any(i.mnemonic == 'or' and i.op_str == 'byte ptr [bp - 1], 0xc' for i in conversion)
assert any(i.mnemonic == 'fistp' and i.op_str == 'qword ptr [bp - 0xa]' for i in conversion)

def signed(v, size):
    mask = (1 << (size*8))-1
    v &= mask
    return v-(mask+1) if v & ((mask+1)//2) else v

class Machine:
    def __init__(self):
        self.mem = bytearray(65536)
        self.reg = {}
        self.moves = []
        self.steps = 0
        self.roots = []
    def read(self, p, size=4):
        return int.from_bytes(self.mem[p:p+size], 'little')
    def write(self, p, v, size=4):
        self.mem[p:p+size] = (v & ((1 << (size*8))-1)).to_bytes(size,'little')
    def getreg(self, name):
        if name in ('ax','bx','cx','dx','bp','sp','si','di'):
            return self.reg.get('e'+name,0) & 65535
        return self.reg.get(name,0)
    def setreg(self, name, value):
        if name in ('ax','bx','cx','dx','bp','sp','si','di'):
            key = 'e'+name
            self.reg[key] = (self.reg.get(key,0) & 0xffff0000) | (value & 65535)
        else:
            self.reg[name] = value & 0xffffffff
    def address(self, i, o):
        assert o.type == X86_OP_MEM
        return (self.getreg(i.reg_name(o.mem.base)) + self.getreg(i.reg_name(o.mem.index))*o.mem.scale + o.mem.disp) & 65535
    def value(self, i, o):
        if o.type == X86_OP_IMM: return o.imm
        if o.type == X86_OP_REG: return self.getreg(i.reg_name(o.reg))
        return self.read(self.address(i,o),o.size)
    def put(self, i, o, value):
        if o.type == X86_OP_REG: self.setreg(i.reg_name(o.reg),value)
        else: self.write(self.address(i,o),value,o.size)
    def push(self, value, size=2):
        self.setreg('sp',self.getreg('sp')-size)
        self.write(self.getreg('sp'),value,size)
    def pop(self, size=2):
        p = self.getreg('sp'); v = self.read(p,size); self.setreg('sp',p+size); return v
    def callback(self, sprite, point, ellipse=False, entry=None):
        saved = self.reg.copy()
        bp = 0x9400 if ellipse else 0x9000
        self.reg = {'ebp':bp,'esp':bp-0x100}
        self.write(bp+6,sprite); self.write(bp+10,point); self.write(bp-10,sprite)
        pc = entry if entry is not None else 0x27a9 if ellipse else 0x11a7
        compare = 0
        for _ in range(3000):
            if pc in (0x33de,0x15f6,0x3858):
                self.reg = saved
                return
            i = ins[pc]; pc += i.size; self.steps += 1
            op, operands = i.mnemonic, i.operands
            v = [self.value(i,o) for o in operands]
            if op == 'mov': self.put(i,operands[0],v[1])
            elif op == 'movsx': self.put(i,operands[0],signed(v[1],operands[1].size))
            elif op in ('inc','dec'): self.put(i,operands[0],v[0]+(1 if op == 'inc' else -1))
            elif op == 'les': self.setreg(i.reg_name(operands[0].reg),v[1] & 65535)
            elif op == 'sar': self.put(i,operands[0],signed(v[0],operands[0].size) >> v[1])
            elif op in ('add','sub','xor','or','shl'):
                r = {'add':lambda:v[0]+v[1], 'sub':lambda:v[0]-v[1], 'xor':lambda:v[0]^v[1], 'or':lambda:v[0]|v[1], 'shl':lambda:v[0]<<v[1]}[op]()
                self.put(i,operands[0],r); compare = signed(r,operands[0].size)
            elif op == 'cmp': compare = signed(v[0],operands[0].size)-signed(v[1],operands[0].size)
            elif op == 'imul': self.put(i,operands[0],signed(v[-2],operands[-2].size)*signed(v[-1],operands[-1].size))
            elif op == 'cdq': self.setreg('edx',0xffffffff if self.getreg('eax') & 0x80000000 else 0)
            elif op == 'idiv':
                numerator = signed((self.getreg('edx') << 32)|self.getreg('eax'),8)
                denominator = signed(v[0],4)
                q = abs(numerator)//abs(denominator) * (-1 if (numerator < 0) != (denominator < 0) else 1)
                self.setreg('eax',q); self.setreg('edx',numerator-q*denominator)
            elif op == 'push': self.push(v[0],operands[0].size)
            elif op == 'pop': self.put(i,operands[0],self.pop(operands[0].size))
            elif op in ('jmp','je','jne','jg','jge','jl','jle'):
                if {'jmp':True,'je':compare==0,'jne':compare!=0,'jg':compare>0,'jge':compare>=0,'jl':compare<0,'jle':compare<=0}[op]: pc = v[0]
            elif op == 'fild': self.fp = signed(v[0],operands[0].size)
            elif op == 'fstp': pass # The following sqrt import consumes this value.
            elif op in ('nop','wait'): pass
            elif op == 'call':
                if i.address == 0x2ef6:
                    self.pop(); sp = self.getreg('sp')
                    val = self.call_region(*[signed(self.read(sp+4*j),4) for j in range(6)])
                    self.setreg('ax',val); self.setreg('dx',0); continue
                assert i.address == 0x11f1 and v[0] == 0x2733
                # Caller already pushed CS. The nested frame is separate.
                self.pop()
                sp = self.getreg('sp')
                self.callback(self.read(sp),self.read(sp+4),ellipse=True)
            elif op == 'lcall':
                sp = self.getreg('sp')
                if i.address in (0x2a52,0x2ae7):
                    assert self.fp >= 0
                    self.roots.append(self.fp); self.fp = math.sqrt(self.fp)
                elif i.address in (0x2a5a,0x2aef):
                    val = int(self.fp); self.setreg('ax',val); self.setreg('dx',val >> 16)
                elif i.address in (0x1218,0x1239,0x1262,0x1502,0x152b):
                    target = self.read(sp); x = self.read(sp+4,2); y = self.read(sp+6,2)
                    self.locate(target,signed(x,2),signed(y,2))
                elif i.address in (0x12b4,0x12ce,0x12e4,0x12fa): self.write(self.read(sp)+0x10,self.read(sp+4,2),2)
                elif i.address == 0x14e1: self.write(self.read(sp)+0x200,-1,2)
                elif i.address in (0x1542,0x1559,0x1570): self.write(self.read(sp)+0x202,-1,2)
                elif i.address in (0x15b6,0x15ee,0x2f21): self.write(self.read(sp)+0x5b,self.read(sp+4,2))
                elif entry is not None: self.custom_call(i.address,sp)
                else: raise AssertionError(('unknown call',hex(i.address)))
            else: raise AssertionError((hex(i.address),op,i.op_str))
        raise AssertionError('callback did not terminate')
    def locate(self, sprite, x, y):
        width = signed(self.read(sprite+0x1b,2),2)-signed(self.read(sprite+0x17,2),2)
        height = signed(self.read(sprite+0x1d,2),2)-signed(self.read(sprite+0x19,2),2)
        for off,value in ((0x17,x),(0x19,y),(0x1b,x+width),(0x1d,y+height)):
            self.write(sprite+off,value,2)

def orbit_trace(scenario, delay, phase):
    m = Machine(); place = 0x1000; point = 0x8000
    m.write(0xc88,place); m.write(0xc8c,526)
    for id in (18,20,21,22,23):
        s = 0x2000+id*0x300; m.write(place+0x20+4*id,s)
        m.write(s+0x1b,26,2); m.write(s+0x1d,26,2)
        m.locate(s,300 if id in (20,22) else 313,220 if id in (20,22) else 170)
        m.write(s+0x10,id in (20,23),2)
        for off,value in ((0xa5,313 if id==23 else 300),(0xa9,70 if id==23 else 120),(0xb1,200),(0xb5,100)):
            m.write(s+off,value)
        m.write(s+0x7d,2,2)
    phase_sprite = m.read(place+0x68); m.write(phase_sprite+0x5b,phase)
    h = 2166136261
    points = []
    for tick in range(1,2501):
        m.write(place+0x400,scenario if tick >= delay else 0)
        if tick % 10 == 0 and m.read(phase_sprite+0x200,2) != 65535:
            m.write(phase_sprite+0x5b,(m.read(phase_sprite+0x5b)+1)%12)
        for id in (20,22,23):
            s = m.read(place+0x20+4*id)
            if m.read(s+0x202,2) == 65535: continue
            m.write(point,m.read(s+0x17,2)+signed(m.read(s+0x7d,2),2),2)
            m.write(point+2,m.read(s+0x19,2)+signed(m.read(s+0x7f,2),2),2)
            m.callback(s,point)
            m.locate(s,signed(m.read(point,2),2),signed(m.read(point+2,2),2))
        row = []
        for id in (20,22,23):
            s=m.read(place+0x20+4*id)
            row += [signed(m.read(s+0x17,2),2),signed(m.read(s+0x19,2),2),m.read(s+0x10,2)]
        row += [m.read(phase_sprite+0x5b)]
        for value in row:
            for b in struct.pack('<i',value): h=((h^b)*16777619)&0xffffffff
        if tick <= 3: points.append(row)
        if m.read(m.read(place+0x70)+0x202,2) == 65535:
            return dict(scenario=scenario,delay_ticks=delay,initial_phase=phase,ticks=tick,last=row,first=points,fnv1a32=hex(h),instructions=m.steps,square_roots=len(m.roots))
    raise AssertionError(('orbit did not stop',scenario,delay))

if __name__ == '__main__':
    traces=[orbit_trace(s,d,p) for s in range(1,7) for d in (1,500) for p in (0,7)]
    result=dict(scene=526,source='original x86 instructions; SpriteWorld setters modeled',traces=traces,conversion=dict(address='1:15c3',rounding='truncate toward zero before radius scaling'),code_sha256=hashlib.sha256(exe[base(3)+0x1199:base(3)+0x33e5]).hexdigest())
    args.out.write_text(json.dumps(result,indent=2))
    print('Original P526 motion: PASS (%d traces, %d instructions)' % (len(traces),sum(t['instructions'] for t in traces)))
