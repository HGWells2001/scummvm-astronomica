"""Refresh the existing reviewed source-only export after checkpoint validation."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('publish/scummvm-astronomica')
subprocess.run([sys.executable,'work/fresh-20260913/verify_development_evidence.py'],check=True)
assert subprocess.check_output(['git','-C',str(root),'remote','get-url','origin'],text=True).strip()=='https://github.com/HGWells2001/scummvm-astronomica.git'
manifest=json.loads((root/'SOURCE-MANIFEST.json').read_text())
# Only refresh paths already in the reviewed export. Do not add game media,
# binaries, saves or the full workspace through a recursive wildcard copy.
for name in manifest['sha256']:
    if name.startswith(('outputs/astronomica-cleanroom/','work/fresh-20260913/')):
        src=Path(name); assert src.is_file(),name
        shutil.copyfile(src,root/name)
for name in ('work/fresh-20260913/finish_help_keyboard.py','work/fresh-20260913/update_github_export.py','outputs/astronomica-cleanroom/GITHUB-PUBLISH.md','outputs/astronomica-cleanroom/P508-SAVE-PLAN.md'):
    shutil.copyfile(name,root/name)
m=json.loads(Path('outputs/astronomica-cleanroom/evidence/development-validation.json').read_text())
p=root/'SCUMMVM_BASE.json';j=json.loads(p.read_text())
j.update(engine_sha256=m['engine_sha256'],validated_executable_sha256=m['exe_sha256']);p.write_text(json.dumps(j,indent=2)+'\n')
p=root/'README.md';s=p.read_text().replace('on 13 October 2026','on 14 October 2026')
if 'PageUp/PageDown/Home/End' not in s:
    s=s.replace('- Help checks cover', '- PageUp/PageDown/Home/End scroll the native help reader; all 781 articles pass keyboard navigation and boundary checks.\n- Help checks cover')
p.write_text(s)
manifest['date']='2026-10-14'
manifest['sha256']={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(root.rglob('*')) if p.is_file()
                   and not {'.git','__pycache__'}.intersection(p.parts) and p.name!='SOURCE-MANIFEST.json'}
(root/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
subprocess.run([sys.executable,str(root/'tools/verify_export.py')],check=True)
print('Source-only export refreshed; review git diff before commit/push')
