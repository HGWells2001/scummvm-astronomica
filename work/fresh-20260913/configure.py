from pathlib import Path
import subprocess,re,urllib.request,zipfile
base=Path('work/fresh-20260913').resolve();repo=base/'scummvm';build=base/'build';build.mkdir(exist_ok=True)
url='https://libsdl.org/release/SDL2-devel-2.32.6-VC.zip';dest=base/'sdl2.zip'
if not dest.exists():urllib.request.urlretrieve(url,dest)
with zipfile.ZipFile(dest) as z:
 for n in z.namelist():
  target=(base/n).resolve()
  if not target.is_relative_to(base):raise ValueError(n)
 z.extractall(base)
sdl=base/'SDL2-2.32.6';tool=repo/'dists/msvc/create_project.exe'
help=subprocess.run([str(tool)],capture_output=True,text=True).stdout
features=re.findall(r'^\s*enabled\s*\|\s*(\S+)\s*\|',help,re.M)
keep={'16bit','highres','scalers','aspect','translation','builtin-resources','detection-static'}
cmd=[str(tool),'../scummvm','--msvc','--msvc-version','18','--output-dir',str(build),'--disable-all-engines','--enable-engine=astronomica','--include-dir',str(sdl/'include'),'--library-dir',str(sdl/'lib/x64')]+['--disable-'+f for f in features if f not in keep]
p=subprocess.run(cmd,cwd=build,capture_output=True,text=True);(base/'configure.log').write_text(p.stdout+p.stderr);print(p.returncode,p.stdout[-1500:],p.stderr)

