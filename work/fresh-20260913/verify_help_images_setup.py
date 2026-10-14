from pathlib import Path
import json,runpy,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');sys.argv=['probe','D:/astro','--out',str(root/'evidence/help-bitmaps.json')]
r=runpy.run_path(str(root/'probe_help_bitmaps.py')); src=r['d']; directory=r['directory']; rows=[]
def fnv(b):
 h=2166136261
 for c in b:h=((h^c)*16777619)&0xffffffff
 return h
maps=json.loads((root/'evidence/help-image-articles.json').read_text())['associations']
for m in maps:
 i=m['image'];info=directory['streams'][f'|bm{i}'];b=src[info['offset']+9:info['offset']+9+info['used']];q=r['Reader'](b)
 vals=[q.packed(),q.packed(),q.packed(True),q.packed(True)]+[q.packed() for _ in range(6)]
 offset=int.from_bytes(b[q.pos:q.pos+4],'little');q.pos+=8;palette=b[q.pos:q.pos+1024];stored=b[8+offset:];pixels=r['lz'](stored) if b[9]==2 else stored
 rows.append(dict(image=i,article=m['article'],width=vals[4],height=vals[5],palette_fnv=fnv(palette),pixels_fnv=fnv(pixels)))
p=root/'evidence/help-image-articles.json';d=json.loads(p.read_text());d['native_references']=rows;p.write_text(json.dumps(d,indent=2))
p=root/'engine/astronomica/help.cpp';s=p.read_text();table='\n'.join('  {%d,%d,%d,0x%08xU,0x%08xU},'%(v['article'],v['width'],v['height'],v['palette_fnv'],v['pixels_fnv']) for v in rows)
impl='''bool verifyHelpImages(const HelpBook &book) {
 // Independent original-file references: help-image-articles.json.
 struct Reference { uint article, width, height; uint32 paletteHash, pixelHash; };
 const Reference references[] = {
'''+table+'''
 };
 if (book.images.size() != ARRAYSIZE(references)) return false;
 auto hash = [](const Common::Array<byte> &bytes) {
  uint32 value = 2166136261U; for (byte b : bytes) value = (value ^ b)*16777619U; return value;
 };
 uint associations = 0;
 for (uint a = 0; a < book.articles.size(); ++a) for (uint id : book.articles[a].images) {
  if (id >= ARRAYSIZE(references) || references[id].article != a) return false; ++associations;
 }
 if (associations != ARRAYSIZE(references)) return false;
 for (uint i = 0; i < book.images.size(); ++i) {
  const HelpImage &image = book.images[i]; const Reference &ref = references[i];
  if (image.width != ref.width || image.height != ref.height || image.pitch != ((ref.width+3)&~3U) ||
      hash(image.palette) != ref.paletteHash || hash(image.pixels) != ref.pixelHash) return false;
  uint count = 0; for (uint id : book.articles[ref.article].images) if (id == i) ++count;
  if (count != 1) return false;
 }
 return true;
}
'''
s=s.replace('bool verifyHelpBookUI(',impl+'bool verifyHelpBookUI(');p.write_text(s)
p=root/'engine/astronomica/astronomica.cpp';s=p.read_text();marker=' const uint lengths[] = {0,1,4,8,12,15,16,32,256,65536,uint(bytes.size()-1)};';offsets=','.join(hex(directory['streams'][f'|bm{i}']['offset']+9+8) for i in range(31))
s=s.replace(marker,''' // Reject invalid image types in every original bitmap stream. Failed loads
 // must preserve both the text and every image in the previously loaded book.
 const uint imageTypeOffsets[] = {'''+offsets+'''};
 bool imageOK = verifyHelpImages(_helpBook);
 for (uint offset : imageTypeOffsets) {
  const byte before = bytes[offset]; bytes[offset] = 0xff;
  Common::MemoryReadStream damaged(&bytes[0],bytes.size());
  imageOK = !_helpBook.load(damaged) && verifyHelpImages(_helpBook) && imageOK; bytes[offset] = before;
 }
 debug("Astronomica help images verification: %s (31 palettes/pixels, 31 original article associations, 31 corrupt image streams)",imageOK ? "PASS" : "FAIL");
 ok = imageOK && ok;
'''+marker);p.write_text(s)
for name in ('help.h','help.cpp','astronomica.cpp'):
 (work/'scummvm/engines/astronomica'/name).write_bytes((root/'engine/astronomica'/name).read_bytes())
(root/'RUN-IN-PROGRESS.md').write_text('Native help article image viewer in development. Original bitmap references and associations recorded; build and native tests pending. Do not treat prior evidence as validation of this change.\n')
