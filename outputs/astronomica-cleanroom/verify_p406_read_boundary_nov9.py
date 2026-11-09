"""Verify the original loader's embedded-bitmap read boundary for unchanged P406.

This is a hash-pinned static instruction/data-flow check, not Windows execution
or a claim that the scene is selected by ordinary gameplay.
"""
from pathlib import Path
import argparse,hashlib,json,struct,sys
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
x=(a.root/'SETUP/ASTRO.EXE').read_bytes();p=a.root/'PLACES/P406/MEGAFILE.HYP';data=p.read_bytes()
assert sha(x)=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'
assert sha(data)=='fcd48d6c1f370a53f62870fb81f0532aeacb5dded8d5a81342538883b5f87cd8'
assert len(data)==24 and struct.unpack('<6i',data)==(1,86,0,87,1,1)
ne=struct.unpack_from('<I',x,60)[0];table=ne+struct.unpack_from('<H',x,ne+0x22)[0];shift=struct.unpack_from('<H',x,ne+0x32)[0]
base=struct.unpack_from('<H',x,table+8*8)[0]<<shift
sys.path.insert(0,str(Path('work/fresh-20260913/deps-verified').resolve()))
import capstone
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
assert capstone.__version__=='5.0.7'
md=Cs(CS_ARCH_X86,CS_MODE_16)
def block(lo,hi):return [(i.address,i.mnemonic,i.op_str)for i in md.disasm(x[base+lo:base+hi],lo)]
def require(lo,hi,expected):
 actual=block(lo,hi);assert [(m,s)for _,m,s in actual]==expected,(hex(lo),actual)
require(0x15cd,0x15d6,[('cmp','dword ptr [bp - 0x24], 1'),('jne','0x1714')])
for call in (0x15f1,0x1608,0x161f,0x1723,0x1751,0x17f5):
 require(call,call+3,[('call','0x3d04')])
require(0x1737,0x1741,[('cmp','dword ptr [0x1c5], 1'),('jne','0x1916')])
require(0x1765,0x176c,[('cmp','dword ptr [bp - 0x24], 0'),('jne','0x17e5')])
require(0x17e5,0x17f8,[('push','ss'),('lea','ax, [bp - 0x32]'),('push','ax'),('push','ss'),('lea','ax, [bp - 0x46]'),('push','ax'),('push','word ptr [0xbc8]'),('nop',''),('push','cs'),('call','0x3d04')])
require(0x17f8,0x17fd,[('add','sp, 0xa'),('mov','di, ax')])
require(0x3d0e,0x3d26,[('push','word ptr [bp + 6]'),('push','word ptr [bp + 0xe]'),('push','word ptr [bp + 0xc]'),('les','bx, ptr [bp + 8]'),('push','word ptr es:[bx]'),('lcall','0, 0xffff'),('xor','dx, dx'),('jmp','0x3d26')])
length,flags=struct.unpack_from('<HH',x,table+8*8+2);assert flags&0x100;rel=base+(length or 65536)
modtable=ne+struct.unpack_from('<H',x,ne+0x28)[0];strings=ne+struct.unpack_from('<H',x,ne+0x2a)[0];found=[]
for i in range(struct.unpack_from('<H',x,rel)[0]):
 kind,flag,offset,target1,target2=struct.unpack_from('<BB3H',x,rel+2+8*i);seen=set()
 while offset!=65535:
  assert offset not in seen;seen.add(offset)
  if offset==0x3d1e:
   assert kind==3 and flag&3==1 and target2==82
   at=strings+struct.unpack_from('<H',x,modtable+(target1-1)*2)[0]
   module=x[at+1:at+1+x[at]].decode('ascii');assert module=='KERNEL';found.append(module+'.ordinal82')
  if flag&4:break
  offset=struct.unpack_from('<H',x,base+offset)[0]
assert found==['KERNEL.ordinal82']
proof=dict(status='ORIGINAL_P406_EMBEDDED_BITMAP_READ_BOUNDARY_PASS',author_sha256=sha(Path(__file__).read_bytes()),original_exe_sha256=sha(x),original_p406_sha256=sha(data),original_p406_bytes=len(data),original_loader='9:1404',mode=1,navigation_words=3,background_present=True,background_embedded=True,next_requested_field='embedded bitmap byte length',next_requested_file_offset=24,next_requested_bytes=4,available_bytes=0,read_wrapper='9:3d04',read_import=found[0],external_filename_branch_not_selected=True,original_windows_executed=False,limits=['Static instruction/data-flow check of this declared prefix; no original OS read or allocation executed','No file extension, substitute image or fallback content inferred','No whole-loader memory-safety, P406 gameplay reachability, or original-program crash claim'])
assert not a.out.exists();a.out.write_text(json.dumps(proof,indent=2)+'\n');print('Original P406 embedded bitmap read boundary verified:byte24 requires4bytes, available0')
