from pathlib import Path
import sys,json,importlib.util,zipfile,hashlib,subprocess
out=Path('outputs/astronomica-cleanroom').resolve();base=Path('work/fresh-20260913').resolve()
sys.path.insert(0,str(base/'deps-verified'))
spec=importlib.util.spec_from_file_location('fresh_debug',out/'extract_debug.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.extract(Path(r'D:\astro\SETUP\ASTRO.EXE'),out/'evidence/debug')
assert json.loads((out/'opcode-layout.json').read_text())==json.loads((out/'evidence/debug/opcode-layout.json').read_text())
# Package verification checks shipped executable and exact source correspondence.
p=subprocess.run([str(out/'bin/scummvm.exe'),'--path=D:\\astro','--detect'],capture_output=True,text=True);assert p.returncode==0 and 'astronomica:astronomica' in p.stdout
(out/'evidence/detection.txt').write_text(p.stdout+p.stderr)
for f in (out/'engine/astronomica').iterdir():assert f.read_bytes()==(base/'scummvm/engines/astronomica'/f.name).read_bytes()
assert hashlib.sha256((out/'bin/scummvm.exe').read_bytes()).digest()==hashlib.sha256((base/'build/Releasex64/scummvm.exe').read_bytes()).digest()
archive=out.parent/'Astronomica-prototipo-2026-09-14.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(out.rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts:z.write(f,'astronomica/'+f.relative_to(out).as_posix())
print('Verified opcode extraction, packaged detection, binary/source correspondence. Archive:',archive,archive.stat().st_size)

