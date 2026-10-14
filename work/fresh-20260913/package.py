from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess,os
out=Path('outputs/astronomica-cleanroom').resolve();base=Path('work/fresh-20260913').resolve();root=Path(r'D:\astro')
s=json.loads((out/'corpus-summary.json').read_text());print('Python command total',sum(s['opcode_counts'].values()))
# Persist analysis evidence and build logs alongside the deliverable.
(out/'evidence').mkdir(exist_ok=True)
for name in ['build.log','runtime.log','runtime-console.log','configure.log']:
 shutil.copy2(base/name,out/'evidence'/name)
for name in ['_load_place.asm','_read_command_mem.asm','_execute_command.asm','_load_game.asm','_CreateFrameFromMegaFile.asm']:
 shutil.copy2(base/name,out/'evidence'/name)
# Keep the original inventory generator reproducible without importing probes.
rows=[]
for p in sorted(root.rglob('*')):
 if p.is_file():
  b=p.read_bytes();rows.append(dict(path=p.relative_to(root).as_posix(),size=len(b),sha256=hashlib.sha256(b).hexdigest()))
(out/'inventory.json').write_text(json.dumps(rows,indent=2))
(out/'bin').mkdir(exist_ok=True)
for name in ['scummvm.exe','SDL2.dll']:
 shutil.copy2(base/'build/Releasex64'/name,out/'bin'/name)
shutil.copy2(base/'scummvm/COPYING',out/'COPYING')
shutil.copy2(base/'SDL2-2.32.6/LICENSE.txt',out/'bin/SDL2-COPYING.txt')
(out/'bin/astronomica.ini').write_text('[scummvm]\nconfirm_exit=false\n\n[astronomica-explorer]\nengineid=astronomica\ngameid=astronomica\npath=D:\\astro\n')
(out/'bin/Avvia-Astronomica.cmd').write_text('@echo off\r\n"%~dp0scummvm.exe" --config="%~dp0astronomica.ini" --logfile="%~dp0astronomica.log" astronomica-explorer\r\n')
# Patch consists exclusively of the newly authored engine; no previous attempt was opened.
patch=[]
for p in sorted((out/'engine/astronomica').iterdir()):
 lines=p.read_text().splitlines();rel='engines/astronomica/'+p.name
 patch.extend([f'diff --git a/{rel} b/{rel}','new file mode 100644','--- /dev/null',f'+++ b/{rel}',f'@@ -0,0 +1,{len(lines)} @@']+['+'+l for l in lines])
(out/'astronomica-engine.patch').write_text('\n'.join(patch)+'\n')
(out/'build-provenance.json').write_text(json.dumps(dict(scummvm_commit='2085bcb368c19bc90f0190efcd56b9d58cd7fb5a',scummvm_source='https://github.com/scummvm/scummvm',SDL_version='2.32.6',SDL_source='https://libsdl.org/release/SDL2-devel-2.32.6-VC.zip',build='Visual Studio 2026 MSVC v145 x64 Release',exe_sha256=hashlib.sha256((out/'bin/scummvm.exe').read_bytes()).hexdigest(),game_original_sha256='c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e'),indent=2))

