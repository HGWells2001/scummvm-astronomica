from pathlib import Path
import shutil, subprocess, sys, zipfile, hashlib, json
base=Path('work/fresh-20260913').resolve()
out=Path('outputs/astronomica-cleanroom').resolve()
subprocess.run([sys.executable, str(base/'package.py')], check=True)
shutil.copytree(base/'interpreter',out/'evidence/interpreter',dirs_exist_ok=True)
probe=(base/'interpreter_probe.py').read_text()
probe=probe.replace("sys.path.insert(0,str(Path('work/fresh-20260913/deps-verified').resolve()))", "import argparse\nap=argparse.ArgumentParser(); ap.add_argument('exe',type=Path); ap.add_argument('--symbols',type=Path,default=Path(__file__).parent/'evidence/debug/symbols.json'); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()")
probe=probe.replace("Path(r'D:\\astro\\SETUP\\ASTRO.EXE').read_bytes()", "args.exe.read_bytes()")
probe=probe.replace("Path('outputs/astronomica-cleanroom/evidence/debug/symbols.json').read_text()", "args.symbols.read_text()")
probe=probe.replace("out=Path('work/fresh-20260913/interpreter');out.mkdir(exist_ok=True)", "import hashlib\nassert hashlib.sha256(b).hexdigest()=='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e', 'Unknown executable'\nout=args.out;out.mkdir(parents=True,exist_ok=True)")
(out/'probe_interpreter.py').write_text(probe)
cfg=out/'bin/astronomica.ini'
cfg.write_text(cfg.read_text()+'\n[astronomica-hotspots]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=103\n')
(out/'bin/Prova-collegamento.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-hotspots\r\n')
cfg.write_text(cfg.read_text()+'\n[astronomica-entry]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=505\nastronomica_entry_scripts=true\n')
(out/'bin/Prova-script.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-entry\r\n')
cfg.write_text(cfg.read_text()+'\n[astronomica-sprites]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=29\n')
(out/'bin/Prova-sprite.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-sprites\r\n')
cfg.write_text(cfg.read_text()+'\n[astronomica-movement]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=517\n')
(out/'bin/Prova-movimento.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-movement\r\n')
cfg.write_text(cfg.read_text()+'\n[astronomica-offset]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=510\n')
(out/'bin/Prova-spostamento-relativo.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-offset\r\n')
(out/'bin/Prova-fotogrammi.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-offset\r\n')
cfg.write_text(cfg.read_text()+'\n[astronomica-blink]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=29\nastronomica_entry_scripts=true\n')
(out/'bin/Prova-lampeggio.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-blink\r\n')
cfg.write_text(cfg.read_text()+'\n[astronomica-buttons]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=510\nastronomica_sprite_input=true\n')
(out/'bin/Prova-pulsanti.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-buttons\r\n')
cfg.write_text(cfg.read_text()+'\n[astronomica-animation]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=510\nastronomica_sprite_input=true\nastronomica_animation=true\n')
(out/'bin/Prova-animazione.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-animation\r\n')
cfg.write_text(cfg.read_text()+'\n[astronomica-audio]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\nastronomica_start_place=510\nastronomica_sprite_input=true\nastronomica_animation=true\nastronomica_audio=true\n')
(out/'bin/Prova-audio.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-audio\r\n')
(out/'bin/Prova-uscite.cmd').write_bytes(b'@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-audio\r\n')
# Verify the distributable probe independently against the same original.
sys.path.insert(0,str(base/'deps-verified'))
import runpy
sys.argv=[str(out/'probe_interpreter.py'),r'D:\astro\SETUP\ASTRO.EXE','--out',str(base/'interpreter-check')]
runpy.run_path(str(out/'probe_interpreter.py'),run_name='__main__')
for f in (base/'interpreter-check').iterdir():
 assert f.read_bytes()==(out/'evidence/interpreter'/f.name).read_bytes(), f.name
for f in (out/'engine/astronomica').iterdir():
 assert f.read_bytes()==(base/'scummvm/engines/astronomica'/f.name).read_bytes(), f.name
assert (out/'bin/scummvm.exe').read_bytes()==(base/'build/Releasex64/scummvm.exe').read_bytes()
assert 'script verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'conditions verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'lifecycle verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'sprite verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'visibility verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'movement verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'offset verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'variant bag verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'random verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'bit verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'transition verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'range verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'stop verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'audio verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'animation verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'mouse verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'timer verification: PASS' in (out/'evidence/runtime.log').read_text()
assert 'frame verification: PASS' in (out/'evidence/runtime.log').read_text()
p=subprocess.run([str(out/'bin/scummvm.exe'),'--path=D:\\astro','--detect'],capture_output=True,text=True)
assert p.returncode==0 and 'astronomica:astronomica' in p.stdout
(out/'evidence/detection.txt').write_text(p.stdout+p.stderr)
archive=out.parent/'Astronomica-prototipo-2026-09-16-v20.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(out.rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts:
   z.write(f,'astronomica/'+f.relative_to(out).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert z.read('astronomica/bin/scummvm.exe')==(out/'bin/scummvm.exe').read_bytes()
print('Verified v20 archive:',archive,archive.stat().st_size)








