from pathlib import Path
import zipfile
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text().replace('536','537');p.write_text(s);Path('work/fresh-20260913/scummvm/engines/astronomica/astronomica.cpp').write_text(s)
z=zipfile.ZipFile('work/fresh-20260913/scummvm/dists/engine-data/fonts.dat');print([n for n in z.namelist() if 'helv' in n.lower()][:20]);print(zipfile.ZipFile('work/fresh-20260913/scummvm/gui/themes/scummmodern.zip').namelist()[:25])
