from pathlib import Path
import zipfile
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text().replace('Graphics::PixelFormat format(4, 8, 8, 8, 0, 16, 8, 0, 0);','Graphics::PixelFormat format = _system->getSupportedFormats().front();');p.write_text(s);Path('work/fresh-20260913/scummvm/engines/astronomica/astronomica.cpp').write_text(s)
z=zipfile.ZipFile('work/fresh-20260913/scummvm/dists/engine-data/fonts.dat');print(z.namelist()[:20])
base=Path('work/fresh-20260913/fonts').resolve();base.mkdir(exist_ok=True)
for name in z.namelist():
 if not (base/name).resolve().is_relative_to(base):raise ValueError(name)
z.extractall(base)
p=Path('work/fresh-20260913/runtime_test.py');s=p.read_text().replace("'--savepath='+str(base)","'--extrapath='+str(base/'fonts'),'--savepath='+str(base)");p.write_text(s)
