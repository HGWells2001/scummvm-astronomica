from pathlib import Path
r=Path('outputs/astronomica-cleanroom/engine/astronomica');p=r/'help.h';s=p.read_text().replace('struct HelpArticle { Common::String title, text; };','''struct HelpArticle { Common::String title, text; Common::Array<uint> images; };
struct HelpImage {
 uint width = 0, height = 0, pitch = 0;
 Common::Array<byte> palette, pixels; // Original BGRA palette and bottom-up DIB.
};''').replace('Common::Array<HelpArticle> articles;','Common::Array<HelpArticle> articles;\n Common::Array<HelpImage> images;').replace('bool verifyHelpBookUI','bool verifyHelpImages(const HelpBook &book);\nbool verifyHelpBookUI');p.write_text(s)
p=r/'help.cpp';s=p.read_text();mark='struct Entry { Common::String name; uint32 value = 0, count = 0; };'
insert='''// The original image groups each contain one type-6 DIB at offset 8.
// Packed fields use a low-bit width marker, not a continuation-byte encoding.
uint32 packed(Reader &r, bool small = false) {
 const uint start = r.pos, size = small ? 1 : 2;
 uint32 value = r.get(size);
 if (value & 1) { r.seek(start); value = r.get(size*2); }
 return value >> 1;
}
bool decodeImage(const Bytes &data, HelpImage &image) {
 Reader r(data);
 if (r.get(2) != 0x506c || r.get(2) != 1 || r.get(4) != 8 || r.get(1) != 6) return false;
 const uint compression = r.get(1);
 if (compression != 0 && compression != 2) return false;
 const uint dpiX = packed(r), dpiY = packed(r), planes = packed(r,true), bits = packed(r,true);
 const uint width = packed(r), height = packed(r), colors = packed(r), important = packed(r);
 const uint size = packed(r), hotspots = packed(r), offset = r.get(4), hotspotOffset = r.get(4);
 if (!r.ok || dpiX != 72 || dpiY != 72 || planes != 1 || bits != 8 ||
     !width || width > 640 || !height || height > 480 || colors != 256 || important != 256 ||
     hotspots || hotspotOffset || uint64(offset)+8 != uint64(r.pos)+1024 ||
     uint64(offset)+8+size != data.size()) return false;
 Bytes stored;
 if (!portion(data,r.pos,1024,image.palette) || !portion(data,offset+8,size,stored)) return false;
 if (compression == 2) { if (!decompress(stored,image.pixels)) return false; }
 else image.pixels = stored;
 image.width = width; image.height = height; image.pitch = (width+3)&~3U;
 return image.pixels.size() == image.pitch*height;
}
'''
s=s.replace(mark,insert+mark)
s=s.replace(' if (!fetch("|SYSTEM",data)', ''' for (uint i = 0; i < 31; ++i) {
  HelpImage image;
  if (!fetch(Common::String::format("|bm%u",i).c_str(),data) || !decodeImage(data,image)) return false;
  images.push_back(image);
 }
 if (!fetch("|SYSTEM",data)''')
s=s.replace('if (READ_LE_UINT16(&raw[i+7]) >= 31) return false; ++images; i += 8;', 'const uint id = READ_LE_UINT16(&raw[i+7]); if (id >= this->images.size()) return false; articles.back().images.push_back(id); ++images; i += 8;')
mark='class ArticleDialog : public BookDialog {'
insert='''// Images stay associated with their original article. A separate image view
// avoids inventing inline positions while the WinHelp format runs are researched.
class HelpImageDialog : public BookDialog {
public:
 HelpImageDialog(const HelpBook &book, const HelpArticle &article, uint index) {
  const HelpImage &image = book.images[article.images[index]];
  const Common::String caption = Common::String::format("%s (%u/%u)",article.title.c_str(),index+1,article.images.size());
  new GUI::StaticTextWidget(this,10,8,_w-20,20,Common::U32String(caption,Common::kWindows1252),Graphics::kTextAlignCenter);
  Graphics::Surface surface; surface.create(image.width,image.height,g_system->getOverlayFormat());
  for (uint y = 0; y < image.height; ++y) for (uint x = 0; x < image.width; ++x) {
   const uint color = image.pixels[(image.height-1-y)*image.pitch+x];
   surface.setPixel(x,y,surface.format.RGBToColor(image.palette[4*color+2],image.palette[4*color+1],image.palette[4*color]));
  }
  // Preserve the aspect ratio and never enlarge the source. Small overlays
  // still display the whole picture above the navigation controls.
  const uint fitWidth = MIN<uint>(image.width,MAX(1,_w-20));
  const uint fitHeight = MIN<uint>(image.height,MAX(1,_h-76));
  uint width = fitWidth, height = MAX(1U,image.height*width/image.width);
  if (height > fitHeight) { height = fitHeight; width = MAX(1U,image.width*height/image.height); }
  Graphics::Surface *scaled = surface.scale(width,height,false);
  GUI::GraphicsWidget *picture = new GUI::GraphicsWidget(this,(_w-width)/2,32+(_h-76-height)/2,width,height);
  picture->setGfx(scaled); scaled->free(); delete scaled; surface.free();
  const int buttonWidth = (_w-40)/3;
  GUI::ButtonWidget *previous = new GUI::ButtonWidget(this,10,_h-32,buttonWidth,22,Common::U32String("Previous"),Common::U32String(),1);
  GUI::ButtonWidget *next = new GUI::ButtonWidget(this,20+buttonWidth,_h-32,buttonWidth,22,Common::U32String("Next"),Common::U32String(),2);
  new GUI::ButtonWidget(this,30+buttonWidth*2,_h-32,buttonWidth,22,Common::U32String("Back to article"),Common::U32String(),3);
  previous->setEnabled(index > 0); next->setEnabled(index+1 < article.images.size());
 }
 void handleCommand(GUI::CommandSender *sender, uint32 cmd, uint32 data) override {
  if (cmd >= 1 && cmd <= 3) { setResult(cmd); close(); }
  else GUI::Dialog::handleCommand(sender,cmd,data);
 }
};
'''
s=s.replace(mark,insert+mark).replace('class ArticleDialog : public BookDialog {\npublic:', 'class ArticleDialog : public BookDialog {\n const HelpBook &_book; const HelpArticle &_article;\npublic:')
s=s.replace('explicit ArticleDialog(const HelpArticle &article) : BookDialog() {','ArticleDialog(const HelpBook &book, const HelpArticle &article) : BookDialog(), _book(book), _article(article) {')
s=s.replace('  new GUI::ButtonWidget(this,10,_h-32,90,22,Common::U32String("Previous"),Common::U32String(),1);\n  new GUI::ButtonWidget(this,110,_h-32,90,22,Common::U32String("Next"),Common::U32String(),2);\n  new GUI::ButtonWidget(this,_w-110,_h-32,100,22,Common::U32String("Back to index"),Common::U32String(),3);', '''  const int buttonWidth = (_w-50)/4;
  new GUI::ButtonWidget(this,10,_h-32,buttonWidth,22,Common::U32String("Previous"),Common::U32String(),1);
  new GUI::ButtonWidget(this,20+buttonWidth,_h-32,buttonWidth,22,Common::U32String("Next"),Common::U32String(),2);
  GUI::ButtonWidget *pictures = new GUI::ButtonWidget(this,30+buttonWidth*2,_h-32,buttonWidth,22,Common::U32String("Images"),Common::U32String(),4);
  pictures->setEnabled(!article.images.empty());
  new GUI::ButtonWidget(this,40+buttonWidth*3,_h-32,buttonWidth,22,Common::U32String("Back to index"),Common::U32String(),3);''')
pos=s.index('class ArticleDialog :');a=s[:pos];b=s[pos:];b=b.replace('  if (cmd >= 1 && cmd <= 3)', '''  if (cmd == 4) {
   uint index = 0;
   while (index < _article.images.size()) {
    HelpImageDialog image(_book,_article,index); const int result = image.runModal();
    if (result == 1 && index > 0) --index;
    else if (result == 2 && index+1 < _article.images.size()) ++index;
    else break;
   }
   return;
  }
  if (cmd >= 1 && cmd <= 3)''',1);s=a+b
s=s.replace('ArticleDialog article(_book.articles[_visible[index]])','ArticleDialog article(_book,_book.articles[_visible[index]])').replace('ArticleDialog article(book.articles[58])','ArticleDialog article(book,book.articles[58])')
s=s.replace(' return article.captured;', ''' if (!article.captured) return false;
 for (const uint id : {0U,12U,19U}) {
  uint owner = 0, index = 0; bool found = false;
  for (uint a = 0; a < book.articles.size(); ++a) for (uint n = 0; n < book.articles[a].images.size(); ++n)
   if (book.articles[a].images[n] == id) { owner = a; index = n; found = true; }
  if (!found) return false;
  HelpImageDialog picture(book,book.articles[owner],index);
  picture.captureThenClose(directory.join(Common::String::format("help-image%u.bmp",id))); picture.runModal();
  if (!picture.captured) return false;
 }
 return true;''')
p.write_text(s)
