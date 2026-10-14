from pathlib import Path
p=Path('outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp');s=p.read_text().replace('#include "common/file.h"','#include "common/file.h"\n#include "common/fs.h"').replace('file.open(path)','file.open(Common::FSNode(path))');p.write_text(s);Path('work/fresh-20260913/scummvm/engines/astronomica/astronomica.cpp').write_text(s)
