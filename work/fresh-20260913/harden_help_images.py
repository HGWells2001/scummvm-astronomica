from pathlib import Path
import json
r=Path('outputs/astronomica-cleanroom');w=Path('work/fresh-20260913');p=r/'engine/astronomica/help.cpp';s=p.read_text().replace('g_system->getOverlayHeight()-16) {}','g_system->getOverlayHeight()-16) { _backgroundType = GUI::ThemeEngine::kDialogBackgroundPlain; }')
s=s.replace('ArticleDialog(const HelpBook &book, const HelpArticle &article) :','ArticleDialog(const HelpBook &book, const HelpArticle &article, bool hasPrevious = false, bool hasNext = false) :')
s=s.replace('  new GUI::ButtonWidget(this,10,_h-32,buttonWidth,22,Common::U32String("Previous"),Common::U32String(),1);','  GUI::ButtonWidget *previous = new GUI::ButtonWidget(this,10,_h-32,buttonWidth,22,Common::U32String("Previous"),Common::U32String(),1);\n  previous->setEnabled(hasPrevious);')
s=s.replace('  new GUI::ButtonWidget(this,20+buttonWidth,_h-32,buttonWidth,22,Common::U32String("Next"),Common::U32String(),2);','  GUI::ButtonWidget *next = new GUI::ButtonWidget(this,20+buttonWidth,_h-32,buttonWidth,22,Common::U32String("Next"),Common::U32String(),2);\n  next->setEnabled(hasNext);')
s=s.replace('ArticleDialog article(_book,_book.articles[_visible[index]])','ArticleDialog article(_book,_book.articles[_visible[index]],index > 0,uint(index+1) < _visible.size())');p.write_text(s)
# Additional independent file-boundary corruptions for packed fields and LZ.
d=json.loads((r/'evidence/help-directory.json').read_text());data=Path('D:/astro/HELP/ASTRONOM.HLP').read_bytes();off=d['streams']['|bm0']['offset']+9
cases=[(off+9,0xff),(off+10,0),(off+14,0),(off+15,0),(off+16,0),(off+18,0),(off+22,0),(off+27,0xff)]
# Stream extent and palette-relative offset are also independently checked.
for delta in (4,5): cases.append((d['streams']['|bm0']['offset']+delta,0xff))
p=r/'engine/astronomica/astronomica.cpp';s=p.read_text();marker=' debug("Astronomica help images verification:';pos=s.index(marker)
s=s[:pos]+''' struct ImageDamage { uint offset; byte value; };
 const ImageDamage imageDamage[] = {'''+','.join('{%s,%s}'%(hex(a),hex(b)) for a,b in cases)+'''};
 for (const ImageDamage &damage : imageDamage) {
  const byte before = bytes[damage.offset]; bytes[damage.offset] = damage.value;
  Common::MemoryReadStream damaged(&bytes[0],bytes.size());
  const bool rejected = !_helpBook.load(damaged); bytes[damage.offset] = before;
  imageOK = rejected && verifyHelpImages(_helpBook) && imageOK;
  debug("Astronomica help image header %x: %s",damage.offset,rejected ? "PASS" : "FAIL");
 }
'''+s[pos:];s=s.replace('31 corrupt image streams)','31 corrupt image streams, 10 header/extent corruptions)');p.write_text(s)
for n in ('help.cpp','astronomica.cpp'):(w/'scummvm/engines/astronomica'/n).write_bytes((r/'engine/astronomica'/n).read_bytes())
