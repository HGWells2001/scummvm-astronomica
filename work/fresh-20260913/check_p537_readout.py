"""Compare actual renderer digits against original callback IDs and BMP masks."""
from pathlib import Path
import argparse,hashlib,io,json,os,re,subprocess,sys
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--exe',type=Path);ap.add_argument('--tag',default='');args=ap.parse_args()
assert not args.tag or re.fullmatch('[a-z0-9-]+',args.tag)
assert not args.exe or args.tag
work=Path('work/fresh-20260913').resolve();root=Path('outputs/astronomica-cleanroom').resolve();prefix=args.tag+'-' if args.tag else ''
folder=work/(prefix+'p537-readout-regression');folder.mkdir(exist_ok=True)
sys.path.insert(0,str(root));from astro_reader import parse
raw=Path('D:/astro/PLACES/P537/MEGAFILE.HYP').read_bytes();scene=parse(raw)
original=json.loads((root/'evidence/p537-motion-original.json').read_text())
config=folder/'verify.ini';log=folder/'runtime.log'
config.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=false\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_rocket_original=true\nastronomica_capture_rocket_readouts=true\nsavepath='+folder.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
exe=args.exe.resolve() if args.exe else work/'build/Releasex64/scummvm.exe'
p=subprocess.run([str(exe),'--config='+str(config),'--extrapath='+str(work/'fonts'),'--savepath='+str(folder),'--logfile='+str(log),'--debuglevel=1','astro-verify'],env=env,cwd=work,capture_output=True,text=True,timeout=180)
(folder/'console.log').write_text(p.stdout+p.stderr)
s=log.read_text();assert p.returncode==0 and 'FAIL' not in s and 'P537 readout captures: PASS' in s and '292dc3fd' in s and 'Log closed successfully' in s,s[-1800:]
m=re.search(r'P537 readout pixel format: (\d+) (\d+) (\d+) (\d+)',s);assert m
pixel_format=list(map(int,m.groups()));assert pixel_format[0] in (2,3,4) and all(1<=v<=8 for v in pixel_format[1:])
def quantized(rgb):
 result=[]
 for component,bits in zip(rgb,pixel_format[1:]):
  value=component>>(8-bits);expanded=value;width=bits
  while width<8:expanded=(expanded<<bits)|value;width+=bits
  result.append((expanded>>(width-8))&255)
 return tuple(result)
def bitmap(ref):
 data=raw[ref['offset']:ref['offset']+ref['size']];assert hashlib.sha256(data).hexdigest()==ref['sha256']
 return Image.open(io.BytesIO(data)).convert('RGB')
frames=[(bitmap(image),bitmap(mask)) for image,mask in scene['sprites'][8]['frames']]
captures=[];total=0;negative=0
for setting in (1,7,11,13):
 trace=next(t for t in original['traces'] if t['setting']==setting and t['already_solved']==0 and t['kind']==('slow' if setting<11 else 'orbit' if setting<13 else 'fast'))
 row=trace['last'];native=Image.open(folder/f'rocket-readout-{setting}.bmp').convert('RGB');assert native.size==(640,480)
 selected={id:row[4+(id-9)*6+3] for id in range(9,30)};checked=0;old_mismatch=0
 for id in range(9,30):
  sprite=scene['sprites'][id-1];x,y=sprite['xy'];image,mask=frames[selected[id]]
  for py in range(mask.height):
   for px in range(mask.width):
    if mask.getpixel((px,py))==(0,0,0):
     assert native.getpixel((x+px,y+py))==quantized(image.getpixel((px,py))),(setting,id,px,py,native.getpixel((x+px,y+py)),image.getpixel((px,py)))
     checked+=1
  # The previous +1 readout shift must actually be distinguishable in pixels.
  old_image,old_mask=frames[selected.get(id-1,0)]
  for py in range(old_mask.height):
   for px in range(old_mask.width):
    if old_mask.getpixel((px,py))==(0,0,0) and native.getpixel((x+px,y+py))!=quantized(old_image.getpixel((px,py))):old_mismatch+=1
 assert checked>100 and old_mismatch>0,(setting,checked,old_mismatch)
 png=folder/f'rocket-readout-{setting}.png';native.save(png)
 captures.append(dict(setting=setting,checked_pixels=checked,old_shift_mismatch_pixels=old_mismatch,png_sha256=hashlib.sha256(png.read_bytes()).hexdigest()))
 total+=checked;negative+=old_mismatch
proof=dict(date='2026-10-20',status='PASS',diagnostic=bool(args.tag),exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),original_resource_sha256=hashlib.sha256(raw).hexdigest(),
 original_callback_evidence_sha256=hashlib.sha256((root/'evidence/p537-motion-original.json').read_bytes()).hexdigest(),pixel_format=pixel_format,callback_fnv32='292dc3fd',checked_pixels=total,old_shift_mismatch_pixels=negative,captures=captures,
 scope='Actual production rendering of controlled final callback states; raw original BMP/mask pixel checks; not a Windows-runtime or full manual playthrough claim')
(work/(prefix+'p537-readout-proof.json')).write_text(json.dumps(proof,indent=2))
print(f'P537 production readout rendering PASS: {total} original pixels; old shift differs at {negative} pixels')
