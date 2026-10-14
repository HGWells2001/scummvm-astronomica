"""Export authored cleanroom development, without game media or build dependencies."""
from pathlib import Path
import hashlib,json,shutil

base=Path.cwd()
target=base/'publish/scummvm-astronomica'
assert not target.exists(), 'Choose a new destination; never overwrite a publication checkout.'
root=base/'outputs/astronomica-cleanroom'
work=base/'work/fresh-20260913'
target.mkdir(parents=True)
excluded=[];included=[]

def copy(p):
 rel=p.relative_to(base);dst=target/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(p,dst);included.append(rel.as_posix())

omitted={'exe-strings.json','help-compression.json','help-format.json','astronomica-engine.patch'}
for p in sorted(root.iterdir()):
 if not p.is_file():continue
 if (p.suffix in ('.py','.md','.json') or p.name=='COPYING') and p.name not in omitted:copy(p)
 else:excluded.append(dict(path=p.relative_to(base).as_posix(),reason='Extracted game content or superseded generated patch'))
for p in sorted((root/'engine/astronomica').iterdir()):
 if p.is_file():copy(p)
for p in sorted((root/'evidence').iterdir()):
 if p.is_file() and p.suffix in ('.json','.log') and p.name not in omitted:copy(p)
 elif p.is_file():excluded.append(dict(path=p.relative_to(base).as_posix(),reason='Game imagery or extracted article corpus; regenerate from owned original files'))
for p in sorted(work.glob('*.py')):copy(p)
shutil.copyfile(root/'COPYING',target/'COPYING')
validation=json.loads((root/'evidence/development-validation.json').read_text())
(target/'SCUMMVM_BASE.json').write_text(json.dumps(dict(repository='https://github.com/scummvm/scummvm.git',
 commit='2085bcb368c19bc90f0190efcd56b9d58cd7fb5a',engine_directory='outputs/astronomica-cleanroom/engine/astronomica',
 validated_executable_sha256=validation['exe_sha256'],engine_sha256=validation['engine_sha256']),indent=2))
(target/'EXPORT-NOTES.json').write_text(json.dumps(dict(date='2026-10-14',included_files=len(included),excluded_files=excluded,
 omitted_trees=['Original game D:/astro','ScummVM upstream checkout and Git history (pinned separately)','Compiler SDKs, dependencies, executables, user saves and local configuration'],
 evidence_note='Historical manifests refer to some excluded game-derived files. Local full-checkpoint verification requires those original inputs and generated artifacts. Use tools/verify_export.py for this source export.'),indent=2))
print('Export prepared:',len(included),'authored source/research/report files;',sum(p.stat().st_size for p in target.rglob('*') if p.is_file()),'bytes')
