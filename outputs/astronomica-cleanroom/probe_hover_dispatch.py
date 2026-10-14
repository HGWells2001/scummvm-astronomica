"""Original hover-event dispatch, independent of the native click implementation."""
import hashlib,json
import probe_world_interactions as w
p=w.p
regions=[(0x857,0xa03),(0xcba,0xe10)]
def instructions(start,end):return list(p.md.disasm(p.exe[p.base(9)+start:p.base(9)+end],start))
def has(start,end,mnemonic,operands):
    assert any(i.mnemonic==mnemonic and i.op_str==operands for i in instructions(start,end))
for address in (0x960,0x9ea,0xd36,0xdb6):assert w.target(9,address)['name']=='_pend_command'
for address in (0x910,0x99a):assert w.target(9,address)['name']=='_SWIsPointInSprite'
has(0x91b,0x967,'mov','word ptr es:[bx + 0x387], 1')
has(0x9a5,0x9f1,'mov','word ptr es:[bx + 0x387], 0')
has(0xcf9,0xd3f,'mov','word ptr es:[bx + 0xb70], 1')
has(0xd79,0xdbd,'mov','word ptr es:[bx + 0xb70], 0')
has(0x857,0x899,'call','0x3d50') # read current pointer each place-loop pass
dispatch={i.address:i for i in instructions(0x896,0xa03)}
dispatch.update({i.address:i for i in instructions(0xcba,0xe10)})
def execute_sprite_hover(states,hits,rectangles=False):
    m=p.Machine();m.reg={'ebp':0x9000,'esp':0x8d00}
    m.write(0xc88,0x2000);m.write(0x2004,len(states))
    m.write(0x4914,len(states))
    for index,state in enumerate(states):
        sprite=0x3000+0x400*index
        m.write(0x2024+4*index,sprite)
        m.write(sprite+0x23d,1);m.write(sprite+0x285,1)
        m.write(sprite+0x387,state,2)
        rect=0x2000+0x13c*index
        m.write(rect+0xad0,1);m.write(rect+0xb18,1);m.write(rect+0xb70,state,2)
    pc=0xcba if rectangles else 0x896;compare=0;queued=[]
    for _ in range(1000):
        if pc==(0xe10 if rectangles else 0xa03):
            return [m.read(0x2b70+0x13c*j if rectangles else 0x3387+0x400*j,2) for j in range(len(states))],queued
        i=dispatch[pc];pc+=i.size;op=i.mnemonic;o=i.operands;v=[m.value(i,t) for t in o]
        if op=='mov':m.put(i,o[0],v[1])
        elif op=='movsx':m.put(i,o[0],p.signed(v[1],o[1].size))
        elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
        elif op=='nop':pass
        elif op=='imul':m.put(i,o[0],p.signed(v[-2],o[-2].size)*p.signed(v[-1],o[-1].size))
        elif op=='call':
            assert v[0]==0x3d8a
            m.pop(2);m.setreg('ax',hits[m.getreg('si')])
        elif op=='inc':m.put(i,o[0],v[0]+1)
        elif op=='shl':m.put(i,o[0],v[0]<<v[1])
        elif op=='add':m.put(i,o[0],v[0]+v[1])
        elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[1].size)
        elif op=='xor':m.put(i,o[0],v[0]^v[1]);compare=p.signed(v[0]^v[1],o[0].size)
        elif op=='or':
            m.put(i,o[0],v[0]|v[1]);compare=p.signed(v[0]|v[1],o[0].size)
        elif op=='push':m.push(v[0],o[0].size)
        elif op=='lcall':
            index=m.getreg('si')-(0 if rectangles else 1)
            if i.address in (0x8cb,0x90f,0x999):m.setreg('ax',hits[index])
            else:
                assert i.address in (0x95f,0x9e9,0xd35,0xdb5)
                pointer=m.read(m.getreg('sp'))
                entering=i.address in (0x95f,0xd35)
                expected=0x2000+0x13c*index+(0xad0 if entering else 0xb18) if rectangles else 0x3000+0x400*index+(0x23d if entering else 0x285)
                assert pointer==expected
                queued.append((index,'in' if entering else 'out'))
        elif op in ('jmp','je','jne','jle','jl'):
            if {'jmp':True,'je':compare==0,'jne':compare!=0,'jle':compare<=0,'jl':compare<0}[op]:pc=v[0]
        else:raise AssertionError((hex(i.address),op))
    raise AssertionError('hover loop did not finish')
cases=0
for before in range(8):
    for inside in range(8):
        states=[(before>>j)&1 for j in range(3)];hits=[(inside>>j)&1 for j in range(3)]
        after,queued=execute_sprite_hover(states,hits)
        assert after==hits
        assert queued==[(j,'in' if hits[j] else 'out') for j in range(3) if states[j]!=hits[j]]
        again,events=execute_sprite_hover(after,hits)
        assert again==hits and not events
        rect_after,rect_events=execute_sprite_hover(states,hits,True)
        assert rect_after==after and rect_events==queued
        assert execute_sprite_hover(rect_after,hits,True)==(hits,[])
        cases+=1
result=dict(status='Original hover dispatch research; native validation is recorded separately',
    original_sprite_transition_cases=cases,original_rectangle_transition_cases=cases,repeated_stationary_cases=2*cases,hit_predicates="Modeled; original event state and dispatch instructions execute",
    findings=[
        'The place loop processes pending commands first, then reads pointer coordinates.',
        'Sprites have an independent entered flag at+0x387; mouse rectangles have one at+0xb70.',
        'Entering queues the mouse-in script and sets the flag. Remaining inside does not requeue it.',
        'Leaving queues mouse-out and clears the flag. Remaining outside does not requeue it.',
        'The sprite loop advances after each ordinary hover target, rather than selecting one global hover target.',
        'Cursor-bearing sprite branch at9:08ab can end the sprite scan early; account for it before broad support.',
        'No input-lock check appears in the ordinary sprite/rectangle hover branches.',
        'Inventory:32 paired targets in places1,505,519,526; P505 includes sound commands.'
    ],regions={f'9:{a:04x}-{b:04x}':dict(sha256=hashlib.sha256(p.exe[p.base(9)+a:p.base(9)+b]).hexdigest(),
        instructions=[f'{i.address:04x} {i.mnemonic} {i.op_str}' for i in instructions(a,b)]) for a,b in regions})
p.args.out.write_text(json.dumps(result,indent=2))
print('Original hover enter/leave flags and queued dispatch: PASS (research)')
