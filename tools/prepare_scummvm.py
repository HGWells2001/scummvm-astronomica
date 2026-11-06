# SPDX-License-Identifier: GPL-3.0-or-later
"""Fetch the pinned upstream revision and install the paired engine/video core."""
from pathlib import Path
import argparse,json,subprocess
from install_engine import ROOT,install

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--destination',type=Path,default=ROOT/'work/fresh-20260913/scummvm')
a=ap.parse_args();destination=a.destination.resolve()
info=json.loads((ROOT/'SCUMMVM_BASE.json').read_text())
if not destination.exists():
    destination.mkdir(parents=True)
    subprocess.run(['git','init',str(destination)],check=True)
    subprocess.run(['git','-C',str(destination),'remote','add','origin',info['repository']],check=True)
    subprocess.run(['git','-C',str(destination),'fetch','--depth=1','origin',info['commit']],check=True)
    subprocess.run(['git','-C',str(destination),'checkout','--detach','FETCH_HEAD'],check=True)
install(destination)
