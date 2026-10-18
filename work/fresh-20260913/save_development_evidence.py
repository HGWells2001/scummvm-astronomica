"""Save evidence only after the complete native verification passes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

root = Path('outputs/astronomica-cleanroom')
work = Path('work/fresh-20260913')
log = (work/'runtime.log').read_text()
assert 'FAIL' not in log and 'Astronomica script verification: PASS' in log
assert 'legacy save verification: PASS' in log
assert 'help original exponents: PASS (13 runs' in log
assert 'help images verification: PASS' in log
assert 'help format: 1335 records, 11455 commands, b5265663' in log
assert 'P525 interaction verification: PASS' in log
assert 'P529 interaction verification: PASS' in log
assert 'P528 interaction verification: PASS' in log
assert 'P530 interaction verification: PASS' in log
assert 'P521 interaction verification: PASS' in log
assert 'P518 interaction verification: PASS' in log
assert 'variant puzzle verification: PASS' in log
assert 'P526 interaction verification: PASS' in log
assert 'P526 original motion comparison: PASS' in log
assert 'P512 interaction verification: PASS' in log
assert 'P515/P536 interaction verification: PASS' in log
assert 'P514 interaction verification: PASS' in log
assert 'P514 original motion verification: PASS' in log
assert 'P513 interaction verification: PASS' in log
assert 'P507 interaction verification: PASS' in log
assert 'P522 original motion verification: PASS' in log
assert 'P522 interaction verification: PASS' in log
assert 'P524 interaction verification: PASS' in log
assert 'P501 interaction verification: PASS' in log
assert 'P501 original state comparison: PASS' in log
assert 'P501 original motion verification: PASS' in log
assert 'comet original motion comparison: PASS' in log
assert 'comet original setup comparison: PASS' in log
assert 'comet original composition comparison: PASS' in log
assert 'comet interaction verification: PASS' in log
assert 'P516 original motion comparison: PASS' in log
assert 'P516 original setup comparison: PASS' in log
assert 'P516 collision verification: PASS' in log
assert 'P516 graphics verification: PASS' in log
assert 'P516 interaction verification: PASS' in log
assert 'P510 interaction verification: PASS' in log
assert 'P523 interaction verification: PASS' in log
assert 'mentors interaction verification: PASS' in log
assert 'mentor continuous playback: PASS' in log
assert 'P523 help return: PASS' in log
assert 'save verification: PASS' in log
assert 'transition integration verification: PASS' in log
assert 'game state interaction verification: PASS' in log
assert 'advice/countdown interaction verification: PASS' in log
assert 'advice continuous playback: PASS' in log
assert 'endings interaction verification: PASS' in log
assert 'ending continuous playback: PASS' in log
assert 'post-credits verification: PASS' in log
assert 'intro verification: PASS' in log
assert 'logo verification: PASS' in log
assert 'P29 movie verification: PASS' in log
assert 'world movies verification: PASS' in log
assert 'hover verification: PASS; 32 targets, 4 sounds, 256 dispatch cases' in log
assert 'Hover original overlap and sound order: PASS' in log
assert 'help verification: PASS' in log
assert 'Astronomica P1 help control: PASS' in log
assert 'Astronomica P408 help control: PASS' in log
for name in ['runtime.log','runtime-console.log','build.log']:
    shutil.copyfile(work/name,root/'evidence'/name)
for src,dst in [('continuous-movies-529.log','p529-continuous.log'),('continuous-movies-512.log','p512-continuous.log')]:
    text = (work/src).read_text()
    assert 'continuous movie verification: PASS' in text and 'FAIL' not in text
    shutil.copyfile(work/src,root/'evidence'/dst)
subprocess.run([sys.executable,str(root/'survey_puzzles.py'),'D:/astro','--runtime-log',str(work/'runtime.log'),'--out',str(root)],check=True)
coverage = json.loads((root/'evidence/puzzle-coverage.json').read_text())
source = {}
for p in sorted((root/'engine/astronomica').glob('*')):
    if p.is_file():
        assert p.read_bytes() == (work/'scummvm/engines/astronomica'/p.name).read_bytes()
        source[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
manifest = dict(date='2026-10-18',scope='Local development build; no new package',research_manifest='research-oct01.json',engine_sha256=source,exe_sha256=hashlib.sha256((work/'build/Releasex64/scummvm.exe').read_bytes()).hexdigest(),runtime_log_sha256=hashlib.sha256((work/'runtime.log').read_bytes()).hexdigest(),build_exit=0,runtime_exit=0,complete_route_scenes=[501,502,503,504,505,506,508,509,510,511,512,513,514,515,516,517,518,519,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537],interactive_nonpuzzle_scenes=[507],manual_confirmation_scenes=[508],world_interactive_scenes=[29,82,222,231],continuous_video_scenes=[29,82,222,231,510,512,520,523,525,527,529],entry_template_validation=dict(accepted=coverage['accepted'],total=coverage['total'],percent=round(100*coverage['accepted']/coverage['total'],1)),whole_game_completion_percent=None)
(root/'evidence/development-validation.json').write_text(json.dumps(manifest,indent=2))
shutil.copyfile(work/'variants.log',root/'evidence/variants-runtime.log')
shutil.copyfile(work/'p514.log',root/'evidence/p514-runtime.log')
shutil.copyfile(work/'builder.log',root/'evidence/builder-runtime.log')
print('Development evidence saved:',manifest['entry_template_validation'])

for n in ('501','507','513','522','524'):
    shutil.copyfile(work/('p'+n+'.log'),root/'evidence'/('p'+n+'-runtime.log'))
shutil.copyfile(work/'comet.log',root/'evidence/comet-runtime.log')
shutil.copyfile(work/'p516.log',root/'evidence/p516-runtime.log')
