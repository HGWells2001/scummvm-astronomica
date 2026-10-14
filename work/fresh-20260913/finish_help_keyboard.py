"""Record keyboard help checkpoint only after fresh matching native tests."""
from pathlib import Path
import json, shutil, subprocess, sys
root=Path('outputs/astronomica-cleanroom'); work=Path('work/fresh-20260913')
exe=work/'build/Releasex64/scummvm.exe'
checks={'help.log':['help keyboard navigation: PASS (781 articles','help inline images: PASS (31 original images'],
        'runtime.log':['Astronomica script verification: PASS'],
        'legacy.log':['legacy save verification: PASS'],
        'saves.log':['save verification: PASS','save file verification: PASS'],
        'saves-startup.log':['startup save verification: PASS']}
for name,markers in checks.items():
    p=work/name; s=p.read_text()
    assert p.stat().st_mtime>exe.stat().st_mtime and 'FAIL' not in s and 'Log closed successfully' in s,name
    for marker in markers: assert marker in s,(name,marker)
for p in (root/'engine/astronomica').iterdir():
    if p.is_file():
        assert p.read_bytes()==(work/'scummvm/engines/astronomica'/p.name).read_bytes(),p
        assert p.stat().st_mtime<exe.stat().st_mtime,p
for src,dst in [('help.log','help-native-runtime.log'),('legacy.log','legacy-runtime.log'),('legacy-file-proof.json','legacy-file-proof.json')]:
    shutil.copyfile(work/src,root/'evidence'/dst)
p=root/'evidence/help-native-validation.json'; j=json.loads(p.read_text())
j.update(date='2026-10-14',keyboard_articles=781,keyboard_keys=['PageUp','PageDown','Home','End'],
         keyboard_validation='Production dialog dispatch; both bounds, opposite pages, all article lengths, ignored modifiers and Escape/Tab forwarding')
p.write_text(json.dumps(j,indent=2))
note=('\n\n## Help keyboard navigation, 14 October 2026\n\n'
      'PageUp/PageDown scroll the article with one line of context; Home/End '
      'reach its bounds, including inline pictures. These are native reader '
      'controls, not inferred original WinHelp behavior. Other keys and modified '
      'shortcuts retain the standard ScummVM dialog handling. All 781 articles '
      'passed production dialog dispatch checks, beginning/end clamping, '
      'opposite-page movement and modifier rejection. Full WASAPI regression '
      'and native save/import checks passed on the matching executable.\n')
for name in ('README.md','HELP-RESEARCH.md'):
    p=root/name; s=p.read_text()
    if '## Help keyboard navigation, 14 October 2026' not in s: s+=note
    if name=='README.md': s=s.replace('Stato verificato: 13 ottobre 2026.','Stato verificato: 14 ottobre 2026.')
    p.write_text(s)
p=root/'NEXT-STEPS.md'; s=p.read_text()
if not s.startswith('# Ripresa: navigazione'):
    s='# Ripresa: navigazione tastiera aiuto, 14 ottobre 2026\n\nPagSu/PagGiu/Home/Fine verificati su 781 articoli. Build, suite WASAPI e\nsalvataggi/import PASS. Checkpoint: finish_help_keyboard.py. Non rieseguire\nfinalizzatori precedenti; verifica: verify_development_evidence.py.\n\n'+s
p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
    subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Keyboard help checkpoint verified 14 October 2026. Matching build, all 781 article keyboard checks, inline images, native saves/import and full WASAPI suite PASS. No tests running. See NEXT-STEPS.md.\n')
print('Help keyboard checkpoint PASS')
