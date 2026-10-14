"""Install the verified engine into its pinned upstream checkout without overwrites."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess

ROOT=Path(__file__).resolve().parents[1]

def install(destination):
 destination=destination.resolve()
 info=json.loads((ROOT/'SCUMMVM_BASE.json').read_text())
 head=subprocess.check_output(['git','-C',str(destination),'rev-parse','HEAD'],text=True).strip()
 if head!=info['commit']:raise SystemExit('Checkout revision differs from SCUMMVM_BASE.json; no files changed.')
 source=ROOT/info['engine_directory'];target=destination/'engines/astronomica'
 for name,expected in info['engine_sha256'].items():
  if hashlib.sha256((source/name).read_bytes()).hexdigest()!=expected:
   raise SystemExit('Engine source differs from validated export: '+name)
 if target.exists():
  actual={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir() if p.is_file()}
  if actual!=info['engine_sha256'] or any(p.is_dir() for p in target.iterdir()):
   raise SystemExit('Existing engine directory differs; no files overwritten.')
  print('Engine already matches the verified export.')
 else:
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copytree(source,target)
  print('Engine installed at',target)

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('checkout',type=Path)
 install(ap.parse_args().checkout)
