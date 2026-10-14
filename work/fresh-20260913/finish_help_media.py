"""Finalize only a matching native help image/format build and full regression."""
from pathlib import Path
import json,shutil,subprocess,sys
from PIL import Image
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
exe=work/'build/Releasex64/scummvm.exe';target=work/'help.log';full=work/'runtime.log'
assert exe.stat().st_mtime<target.stat().st_mtime<full.stat().st_mtime
for p in (target,full):
 text=p.read_text();assert 'FAIL' not in text
 for marker in ('help verification: PASS','help images verification: PASS','help format: 1335 records, 11455 commands, b5265663','P1 help control: PASS','P408 help control: PASS','Log closed successfully'):
  assert marker in text,(p,marker)
assert 'Astronomica script verification: PASS' in full.read_text()
assert 'help UI capture: PASS' in target.read_text()
assert 'help article rendering: PASS (781 articles)' in target.read_text()
assert 'STUB:' not in target.read_text()
for p in (root/'engine/astronomica').glob('*'):
 if p.suffix in ('.cpp','.h','.mk'):
  assert p.stat().st_mtime<exe.stat().st_mtime
  assert p.read_bytes()==(work/'scummvm/engines/astronomica'/p.name).read_bytes()
shutil.copyfile(target,root/'evidence/help-native-runtime.log')
for name in ('help-index','help-article','help-image0','help-image12','help-image19','help-format1','help-format38'):
 pic=Image.open(work/(name+'.bmp'));assert pic.size==(640,480);pic.save(root/'evidence'/(name+'.png'))
p=root/'evidence/help-native-validation.json';j=json.loads(p.read_text());j.update(image_count=31,image_articles=20,image_palette_pixel_comparisons=31,image_corruptions=41,rendered_articles=781,format_records=1335,format_commands=11455,format_semantic_hash='b5265663',table_rows=304,fonts=16,
 native_display='Original article images in a separate view, basic bold/italic and paragraphs, table cells',
 capture_inspection='Index, text, Andromeda/Jupiter/Moon images, Aberration emphasis and Apollo Program table inspected at640x480',
 remaining=['inline picture positioning','exact typography and symbol font mappings','underline/strikeout and original paragraph/table measurements','manual audiovisual playthrough'],
 correction='All body commands decoded: no clickable hyperlink opcode occurs in original HLP; textual See references are preserved.')
p.write_text(json.dumps(j,indent=2))
p=root/'NEXT-STEPS.md';s=p.read_text();start=s.index('Prossimo:31 immagini');end=s.index('Custom33 usa gamestat',start)
s=s[:start]+('Le31 immagini originali sono consultabili da20 articoli tramite Images;\n'
 'tutte le palette/pixel e41 corruzioni verificate. Decodificati1335 record\n'
 'di formato e11455 comandi, incluse304 righe di tabelle; hashb5265663.\n'
 'Grassetto/corsivo, paragrafi e celle sono resi nel lettore nativo.\n'
 'Correzione: nessun opcode hyperlink nei1335 record originali; i rimandi\n'
 'See sono testo. Non inventare collegamenti mancanti.\n'
 'Prossimo: posizionamento immagini nel testo, tipografia/font simbolici,\n'
 'sottolineatura/barrato e misure originali di paragrafi/tabelle.\n'
 'Leggere HELP-RESEARCH.md, probe_help_format.py, help-format.json e\n'
 'help-image-articles.json. Test check_help.py; checkpoint finish_help_media.py.\n')+s[end:]
s=s.replace('Checkpoint:finish_help.py','Checkpoint:finish_help_media.py');p.write_text(s)
note=('\n\n## Native help images and basic formatting, 12 October 2026\n\n'
 'All31 original bitmap palettes/pixels and their associations with20 articles '
 'are checked against independent file research. The native Images button '
 'opens article pictures with previous/next navigation.41 image corruption '
 'cases reject bad data while preserving the loaded book. All1335 body records '
 'and11455 formatting commands match semantic FNVb5265663;304 table rows are '
 'decoded. Basic bold/italic, paragraphs and table cells are rendered. '
 'All781 articles opened in the production renderer without failure; targeted GUI captures and full WASAPI regression PASS. Exact typography, '
 'symbol fonts, underline/strikeout, original measurements and inline image '
 'positions remain pending. All body commands were inspected: there are no '
 'inline hyperlink opcodes in this original file; See references are text. '
 'This corrects the earlier pending-hyperlink assumption. No manual complete '
 'game-playthrough claim. See help-native-validation.json.\n')
for name in ('README.md','INTERPRETER.md','HELP-RESEARCH.md'):
 p=root/name
 if b'## Native help images and basic formatting, 12 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
for script in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/script)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Native help images and basic formatting: build, targeted GUI captures and full WASAPI suite PASS.31 images in20 articles;1335 format records,11455 commands,304 table rows. Checkpoint verified. Exact layout/fonts/inline images and manual full playthrough remain. See NEXT-STEPS.md.\n')
print('Native help images/format checkpoint PASS')
