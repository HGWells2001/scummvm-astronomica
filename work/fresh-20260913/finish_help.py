"""Record native help only after matching build, targeted tests and full suite."""
from pathlib import Path
import json,shutil,subprocess,sys
from PIL import Image
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
log=(work/'runtime.log').read_text();target=(work/'help.log').read_text()
for text in (log,target):
 assert 'FAIL' not in text
 for marker in ('help verification: PASS','Astronomica P1 help control: PASS','Astronomica P408 help control: PASS','Log closed successfully'):
  assert marker in text,marker
assert 'Astronomica script verification: PASS' in log
assert 'Astronomica help UI capture: PASS' in target
exe=work/'build/Releasex64/scummvm.exe'
assert exe.stat().st_mtime<(work/'help.log').stat().st_mtime<(work/'runtime.log').stat().st_mtime
for src in (root/'engine/astronomica').glob('*'):
 if src.suffix in ('.h','.cpp','.mk'):
  assert src.read_bytes()==(work/'scummvm/engines/astronomica'/src.name).read_bytes()
  assert src.stat().st_mtime<exe.stat().st_mtime
shutil.copyfile(work/'help.log',root/'evidence/help-native-runtime.log')
for name in ('help-index','help-article'):
 image=Image.open(work/(name+'.bmp'));assert image.size==(640,480)
 image.save(root/'evidence'/(name+'.png'))
(root/'evidence/help-native-validation.json').write_text(json.dumps(dict(date='2026-10-12',status='PASS',
 original_file='HELP/ASTRONOM.HLP',runtime_conversion_required=False,record_count=2117,record_hash_fnv32='2cab83c0',
 readable_articles=781,keyword_count=812,keyword_references=2008,search_cases=5,truncations=11,corruptions=7,
 failed_load_preserves_book=True,original_buttons=[1,408],scoped_command_validation=True,
 modal_return=True,clock_pause=True,mentor_movie_stopped=True,gui_overlay_capture=True,
 capture_inspection='Index search and Astronomical Unit article inspected at640x480',full_suite=True,
 manual_gameplay_confirmation=False,remaining=['inline images','original formatting and symbol fonts','inline hyperlinks','manual audiovisual playthrough']),indent=2))
p=root/'HELP-RESEARCH.md';s=p.read_text().replace('12 October 2026 (validation in progress)','12 October 2026 (targeted and full suite PASS)');p.write_text(s)
p=root/'NEXT-STEPS.md';s=p.read_text();start=s.index('Prossimo: visualizzatore aiuto nativo/custom22.');end=s.index('Custom33 usa gamestat',start)
s=s[:start]+('Aiuto/custom22 integrato come lettura nel motore:781 articoli,812 keyword,\n'
 '2008 riferimenti; file HLP originale letto direttamente. Ricerca, menuP1,\n'
 'mentoriP408, pausa e ritorno, dati corrotti, catture GUI e suite completa PASS.\n'
 'Prossimo:31 immagini dell\'aiuto, formattazione originale, font simbolici e\n'
 'hyperlink nel testo. Il lettore attuale NON riproduce tutta la resa WinHelp.\n'
 'Le31 immagini sono gia decodificate in ricerca:probe_help_bitmaps.py;\n'
 'bitmap12 non compressa, le altre30 LZ. Hash palette/pixel disponibili.\n'
 'Leggere HELP-RESEARCH.md. Sorgenti help.cpp/help.h; test check_help.py;\n'
 'riferimenti indipendenti help-native-reference.json. Navigazione originale:\n'
 '781 contesti,812 keyword e2008 riferimenti nei testi decodificati.\n')+s[end:]
s=s.replace('Restano verifica audiovisiva manuale, aiuto Windows, resume originale, salvataggi','Restano verifica audiovisiva manuale, completamento aiuto, resume originale, salvataggi').replace('Checkpoint:finish_hover.py','Checkpoint:finish_help.py').replace('# Ripresa: introduzione, post-crediti e logo integrati, 11 ottobre 2026','# Ripresa: lettore aiuto nativo integrato, 12 ottobre 2026')
p.write_text(s)
note=('\n\n## Native help reading view, 12 October 2026\n\n'
 'The original HLP is read directly by the engine.781 articles and812 keywords '
 'are accessible from the original P1/P408 help controls. Search, modal return, '
 'pause, corrupt/truncated data and scoped command validation pass. All2117 '
 'decoded records match independent FNV2cab83c0. Actual GUI captures of the '
 'index and an article were inspected. Build and full WASAPI regression PASS. '
 'This is a reading view:31 inline images, original styles/symbol fonts and '
 'inline hyperlinks remain pending. No manual game-playthrough claim. '
 'See HELP-RESEARCH.md and help-native-validation.json.\n')
for name in ('README.md','INTERPRETER.md'):
 p=root/name
 if b'## Native help reading view, 12 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Native help reading view: build,2117 records,781 articles,812 keywords,original P1/P408 controls,GUI captures and full suite PASS. Checkpoint verified. Images/styles/inline hyperlinks remain pending. See NEXT-STEPS.md.\n')
print('Native help checkpoint PASS')
