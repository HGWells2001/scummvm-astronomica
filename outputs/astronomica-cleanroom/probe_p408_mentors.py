"""Execute custom21 from original ASTRO.EXE; record external movie calls.

No native-engine tables are inputs. Separate CS switch tables from DS state.
Untouched stack output is rejected instead of inventing a default movie range.
"""
import json, struct, hashlib
import probe_p526_motion as p
import probe_comet_state as setup

code=p.exe[p.base(4):p.base(4)+0x8f7e]
ins={i.address:i for i in p.md.disasm(code[0x4538:0x50e8],0x4538)}
class Machine(p.Machine):
 def value(self,i,o):
  if o.type==p.X86_OP_MEM and i.reg_name(o.mem.segment)=='cs':
   a=self.address(i,o);return int.from_bytes(code[a:a+o.size],'little')
  return super().value(i,o)

def run(mentor,previous,variant):
 m=Machine();m.reg={'ebp':0x9000,'esp':0x8d00}
 m.write(0x9006,0x2000);m.write(0x2008,mentor)
 m.write(0xc94,previous);m.write(0x7a8,0x7000);m.write(0x7032,variant)
 m.write(0xc88,0x1000);m.write(0x1368,0x6000)
 m.write(0x9000-0xe,0xdeadbeef);m.write(0x9000-0x12,0xdeadbeef)
 pc=0x4538;compare=0;calls=[]
 for _ in range(1000):
  if pc==0x6a10:
   return dict(mentor=mentor,previous=previous,variant=variant,
    unavailable=m.read(0x13f8),calls=calls)
  if pc==0x506f and (m.read(0x8ff2)==0xdeadbeef or m.read(0x8fee)==0xdeadbeef):
   return dict(mentor=mentor,previous=previous,variant=variant,undefined_stack=True)
  i=ins[pc];pc+=i.size;o=i.operands;v=[m.value(i,t) for t in o];op=i.mnemonic
  if op=='mov':m.put(i,o[0],v[1])
  elif op=='les':m.setreg(i.reg_name(o[0].reg),v[1]&65535)
  elif op=='add':m.put(i,o[0],v[0]+v[1])
  elif op=='sub':m.put(i,o[0],v[0]-v[1])
  elif op=='cmp':compare=p.signed(v[0],o[0].size)-p.signed(v[1],o[0].size)
  elif op=='push':m.push(v[0],o[0].size)
  elif op=='loop':
   m.setreg('cx',m.getreg('cx')-1)
   if m.getreg('cx'):pc=v[0]
  elif op in ('jmp','je','jne'):
   if op=='jmp' or (op=='je' and compare==0) or (op=='jne' and compare!=0):pc=v[0]
  elif op=='lcall':
   sp=m.getreg('sp');name=setup.relocs[i.address+1];assert m.read(sp)==0x6000
   if name=='_SetMovieActiveSegment':calls.append(dict(name=name,start=m.read(sp+4),duration=m.read(sp+8)))
   else:assert name=='_StopMovie';calls.append(dict(name=name))
  else:raise AssertionError((hex(i.address),op))
 raise AssertionError('custom21 did not return')

if __name__=='__main__':
 rows=[run(mentor,previous,variant) for mentor in range(1,6)
       for previous in range(500,538) for variant in range(10)]
 tables=[]
 for base in (0x7132,0x7060,0x6f8e,0x6ebc,0x6dea):
  tables.append([struct.unpack_from('<I',code,base+4*i)[0] for i in range(27)])
 result=dict(status='Original custom21 instruction execution, independent of native code',
  code_sha256=hashlib.sha256(code[0x4538:0x50e8]).hexdigest(),previous_scene_tables=tables,
  cases=len(rows),undefined_cases=sum('undefined_stack' in row for row in rows),rows=rows)
 p.args.out.write_text(json.dumps(result,indent=2))
 # Emit only numeric movie boundaries independently recovered above.
 entries=[]
 for previous in range(500,538):
  for variant in (range(1,9) if previous==524 else (0,)):
   selected=[next(r for r in rows if r['mentor']==n and r['previous']==previous and r['variant']==variant) for n in range(1,6)]
   if not any(r.get('calls') for r in selected):continue
   assert all(len(r['calls'])==2 and not r['unavailable'] for r in selected)
   clips=', '.join('{%d,%d}'%(r['calls'][0]['start'],r['calls'][0]['duration']) for r in selected)
   entries.append('  {%d,%d,{%s}},'%(previous,variant,clips))
 header='''// SPDX-License-Identifier: GPL-3.0-or-later
// Movie ranges recovered from ASTRO.EXE custom21, segment4:4538-50e8.
// Reproduce with probe_p408_mentors.py; no original executable code included.
#ifndef ASTRONOMICA_MENTORS_H
#define ASTRONOMICA_MENTORS_H
namespace Astronomica {
struct MentorClip { int start, duration; };
inline MentorClip mentorClip(int mentor, int previous, int variant) {
 struct Row { int place, variant; MentorClip clips[5]; };
 static const Row rows[] = {
'''+ '\n'.join(entries)+'''
 };
 if (mentor < 1 || mentor > 5) return {0,0};
 for (const Row &r : rows)
  if (r.place == previous && (previous != 524 || r.variant == variant)) return r.clips[mentor-1];
 // Original P524 variant0/9 leaves stack values undefined. Fail closed.
 return {0,0};
}
}
#endif
'''
 (p.Path(__file__).parent/'engine/astronomica/mentors.h').write_text(header)
 h=2166136261
 for row in rows:
  clip=row.get('calls',[{}])[0] if row.get('calls') else {}
  for value in (clip.get('start',0),clip.get('duration',0)):h=((h^value)*16777619)&0xffffffff
 result['native_comparison_fnv1a']=format(h,'08x')
 result['undefined_policy']='P524 variants0/9: return unavailable instead of emulating uninitialized stack data'
 p.args.out.write_text(json.dumps(result,indent=2))
 print('Native comparison hash, undefined stack cases fail closed:',hex(h))
 print('Mentors:',len(rows),'cases; undefined:',result['undefined_cases'])
 print('Previous scene tables:',tables)
 print('P523:',[row for row in rows if row['previous']==523 and row['variant']==0])
