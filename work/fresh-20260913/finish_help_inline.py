"""Finalize the current inline help build only after matching complete tests."""
from pathlib import Path
import json,shutil,subprocess,sys
from PIL import Image
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
exe=work/'build/Releasex64/scummvm.exe'
required={
 'help.log':['help article rendering: PASS (781 articles)','help inline images: PASS (31 original images','help original exponents: PASS (13 runs','help UI capture: PASS'],
 'runtime.log':['Astronomica script verification: PASS','legacy save verification: PASS','help verification: PASS','help original exponents: PASS (13 runs'],
 'legacy.log':['legacy save verification: PASS'],
 'saves.log':['save verification: PASS','save file verification: PASS'],
 'saves-startup.log':['startup save verification: PASS']}
for name,markers in required.items():
 p=work/name;log=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime,name
 assert 'FAIL' not in log and 'Log closed successfully' in log,name
 for marker in markers:assert marker in log,(name,marker)
for p in (root/'engine/astronomica').glob('*'):
 if p.is_file():
  assert p.read_bytes()==(work/'scummvm/engines/astronomica'/p.name).read_bytes(),p
  assert p.stat().st_mtime<exe.stat().st_mtime,p
for src,dst in [('help.log','help-native-runtime.log'),('legacy.log','legacy-runtime.log'),('legacy-file-proof.json','legacy-file-proof.json')]:
 shutil.copyfile(work/src,root/'evidence'/dst)
for name in ('help-index','help-article','help-image0','help-image12','help-image19','help-format1','help-format38','help-format366','help-inline0','help-inline12','help-inline19'):
 p=work/(name+'.bmp');assert p.stat().st_mtime>exe.stat().st_mtime
 pic=Image.open(p);assert pic.size==(640,480);pic.save(root/'evidence'/(name+'.png'))
p=root/'evidence/help-native-validation.json';j=json.loads(p.read_text())
j.update(date='2026-10-13',inline_images=31,inline_image_articles=20,original_exponent_runs=13,original_exponent_characters=21,
 native_display='Original pictures interleaved with their text and captions; separate image view retained',
 inline_validation=['All 781 articles rendered','31 image pixel comparisons in article surfaces','scrollbar bounds, wheel and mouse drag','narrow-width scaling and height-only resize, then original size restored'],
 capture_inspection='Andromeda, Jupiter and Moon original images and surrounding text inspected at 640x480',
 exponent_display='Explicit ^(exponent) notation preserves original Arial Super runs with bitmap GUI fonts',
 remaining=['exact typography and original paragraph/table measurements','manual audiovisual playthrough'])
p.write_text(json.dumps(j,indent=2))
note=('\n\n## Inline help pictures, 13 October 2026\n\n'
 'All 31 pictures now appear between the original text runs in 20 articles. '
 'Anchors come from decoded bitmap commands, not caption matching. All are '
 'in paragraph records, none in tables. Rendering combines the existing '
 'Markdown text with decoded original pixels in one scrolling article; '
 'pictures shrink only for narrow viewports and retain their aspect ratio. '
 'No generated image archive or filesystem cache is needed. The separate '
 'Images view is still available. Exact WinHelp spacing is not claimed.\n\n'
 'The production GUI opened all 781 articles. Pixel checks cover all 31 '
 'inline pictures, scrolling to both ends, wheel and drag, narrow width, '
 'height-only resize and restored dimensions. Andromeda, Jupiter and Moon '
 'captures were visually inspected. Native save/import regressions and '
 'the full WASAPI suite passed on the matching executable.\n\n'
 'probe_help_inline.py also inventories every nonempty font run. No Symbol '
 'font is used; descriptors with flags 4 and 33 have no nonempty text runs. '
 'Earlier generic pending Symbol/underline items were not demonstrated by '
 'the original contents. Arial Super occurs in 13 runs, 21 characters, '
 'including Kepler and relativity exponents. These now use explicit ^(exponent) '
 'notation instead of misleading baseline digits. All 13 original runs and '
 'both formulas are checked; no new scientific values or corrections are added. '
 'Kepler article rendering was visually inspected. Raised glyph typography '
 'remains an adaptation, not a pixel-identical font recreation. '
 'See help-inline-original.json.\n')
for name in ('README.md','INTERPRETER.md','HELP-RESEARCH.md'):
 p=root/name
 if b'## Inline help pictures, 13 October 2026' not in p.read_bytes():
  with p.open('ab') as out:out.write(note.encode('ascii'))
p=root/'README.md';data=p.read_bytes()
start=data.index(b'Stato sorgenti:') if b'Stato sorgenti:' in data else data.index(b'Stato verificato:')
end=data.index(b'Questo lavoro',start)
current=('Stato verificato: 13 ottobre 2026. Motore ScummVM nativo in sviluppo; '
 'build locale e suite completa WASAPI PASS. Nessun nuovo pacchetto distribuibile.\n\n'
 'Sono verificati automaticamente percorsi in 35 scene di puzzle, oltre a '
 'navigazione, filmati, audio, aiuto e salvataggi di esplorazione. L\'aiuto '
 'legge 781 articoli e 31 immagini originali, ora inserite fra testo e '
 'didascalie. I 13 esponenti originali sono resi con notazione ^(valore).\n\n'
 'Import GAMESTAT originale disponibile per esplorazione con countdown '
 'inattivo. Restano salvataggi durante i puzzle, fedelta tipografica e '
 'verifica manuale integrale. Nessuna percentuale globale attendibile; '
 '94.2% misura solo 114/121 template statici, non la giocabilita.\n\n'
 'Usare NEXT-STEPS.md per riprendere e verify_development_evidence.py '
 'per verificare il checkpoint. Eseguibile corrente: '
 'work/fresh-20260913/build/Releasex64/scummvm.exe dalla radice del workspace.\n\n')
data=data[:start]+current.encode('ascii')+data[end:]
data=data.replace(b'## Risultato disponibile',b'## Registro storico delle funzionalita (settembre)',1)
p.write_bytes(data)
p=root/'NEXT-STEPS.md';s=p.read_text()
s=s.replace('Prossimo: posizionamento immagini nel testo, tipografia/font simbolici,\nsottolineatura/barrato e misure originali di paragrafi/tabelle.',
 'Le 31 immagini sono ora nella sequenza originale di testo e didascalie.\n'
 'Pixel, scroll, rotellina, trascinamento e ridimensionamento PASS.\n'
 'Nessun font Symbol usato; flag 4/33 senza testo non vuoto.\n'
 'Arial Super: 13 esponenti resi come ^(valore), formule Keplero/relativita PASS.\n'
 'Prossimo: tipografia e misure originali di paragrafi/tabelle; prova integrale.')
s=s.replace('checkpoint finish_help_media.py.','checkpoint finish_help_inline.py.')
s=s.replace('# Ripresa: import GAMESTAT originale integrato, 13 ottobre 2026',
 '# Ripresa: immagini nel testo e formule aiuto, 13 ottobre 2026')
s=s.replace('Checkpoint:finish_legacy.py;', 'Checkpoint:finish_help_inline.py;')
if 'Ultimo checkpoint: finish_help_inline.py' not in s:
 s += ('\nUltimo checkpoint: finish_help_inline.py, 13 ottobre 2026.\n'
       'La verifica ripetibile e verify_development_evidence.py; comprende\n'
       'immagini nel testo, 13 esponenti, import originale e salvataggi nativi.\n'
       'Non ricreare un vecchio checkpoint tramite i finalizzatori precedenti.\n')
p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Inline help images checkpoint verified 13 October 2026. Matching build, all 781 articles, 31 inline image pixel/scroll/reflow tests, native saves/import and full WASAPI suite PASS. No tests running. See NEXT-STEPS.md.\n')
print('Inline help checkpoint PASS')
