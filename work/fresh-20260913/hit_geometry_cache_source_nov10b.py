"""Cache decoded hit-image dimensions, preserving the original rectangular hit rules."""
HELPER=r'''
bool AstronomicaEngine::spriteImageDimensions(Common::SeekableReadStream &file, const BitmapRef &image, int &width, int &height) {
 if (_hitGeometryPlace != _place) {
  _hitGeometry.clear();
  _hitGeometryPlace = _place;
 }
 for (const HitGeometry &entry : _hitGeometry) {
  if (entry.offset == image.offset && entry.size == image.size) {
   width = entry.width; height = entry.height;
   return true;
  }
 }
 ++_hitGeometryDecodes;
 Graphics::Surface *bmp = decodeSpriteBitmap(file, image, _screen.format);
 if (!bmp) return false;
 width = bmp->w; height = bmp->h;
 bmp->free(); delete bmp;
 // The cache owns only dimensions, never resource streams or pixel buffers.
 if (_hitGeometry.size() < 4096) {
  HitGeometry entry = {image.offset, image.size, width, height};
  _hitGeometry.push_back(entry);
 }
 return true;
}
'''

TEST=r'''
bool AstronomicaEngine::verifyHitGeometry() {
 // Frozen pre-cache algorithm: retain the old decoder path as a test oracle.
 auto uncached = [&](int x, int y) -> int { @ORACLE@ };
 uint queries=0, hidden=0, unknownFrames=0, unsupported=0;
 const int places[]={1,2,27,29,281,501,502,503,504,505,506,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537};
 for(int place:places){
  ConfMan.setBool("astronomica_entry_scripts",false);
  if(!loadPlace(place,false,true))return false;
  if(!_hitGeometry.empty()||_hitGeometryPlace!=-1)return false;
  auto compare=[&](int x,int y){const int expected=uncached(x,y),actual=spriteAt(x,y);++queries;if(actual!=expected){debug("Hit geometry mismatch: P%d xy%d,%d expected%d actual%d",place,x,y,expected,actual);return false;}return true;};
  for(Common::Point p:{Common::Point(0,0),Common::Point(320,240),Common::Point(639,479)})if(!compare(p.x,p.y))return false;
  uint selected=0;
  for(uint i=0;i<_scene.sprites.size()&&selected<8;++i){
   Sprite&s=_scene.sprites[i];if(!s.clickEnabled&&!s.dragEnabled)continue;++selected;if(!s.visible)++hidden;
   Common::File f;if(!f.open(Common::FSNode(ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/MEGAFILE.HYP",place))))))return false;
   const Frame*frame=staticSpriteFrame(_scene,i);Graphics::Surface*bmp=frame?decodeSpriteBitmap(f,frame->image,_screen.format):nullptr;if(!bmp)continue;const int width=bmp->w,height=bmp->h;bmp->free();delete bmp;
   const int left=s.renderX,top=s.renderY,right=int16(left+width),bottom=int16(top+height);
   for(Common::Point p:{Common::Point(left,top),Common::Point(right,top),Common::Point(left,bottom),Common::Point(right,bottom),Common::Point(left-1,top),Common::Point(right+1,bottom),Common::Point(left,top-1),Common::Point(right,bottom+1)})if(!compare(p.x,p.y))return false;
   if(spriteFrameCount(_scene,i)>1){const int saved=s.selectedFrame;s.selectedFrame=-1;if(!compare(left,top))return false;++unknownFrames;s.selectedFrame=spriteFrameCount(_scene,i)-1;if(!compare(right,bottom))return false;s.selectedFrame=saved;}
   const bool saved=s.autoFrame;s.autoFrame=true;if(!compare(left,top))return false;s.autoFrame=saved;++unsupported;
  }
  const int expected=spriteAt(320,240);const uint32 decoded=_hitGeometryDecodes;
  for(uint repeat=0;repeat<32;++repeat)if(spriteAt(320,240)!=expected)return false;
  if(_hitGeometryDecodes!=decoded)return false;
  debug("Hit geometry scene: PASS (P%d,cache%u,queries%u,decodeAttempts%u)",place,_hitGeometry.size(),queries,_hitGeometryDecodes);
 }
 // Cache entries must neither make a missing file hittable nor survive a reload.
 if(!loadPlace(536,false,true))return false;
 const int expected=spriteAt(320,240);const uint32 warmed=_hitGeometryDecodes;const Common::Path root=ConfMan.getPath("path");
 const Common::Path absent=root.join("__astronomica_no_such_hit_geometry_root__");if(Common::FSNode(absent).exists())return false;
 ConfMan.setPath("path",absent);const int missing=spriteAt(320,240);ConfMan.setPath("path",root);if(missing!=-2||spriteAt(320,240)!=expected||_hitGeometryDecodes!=warmed)return false;
 if(!loadPlace(536,false,true)||!_hitGeometry.empty()||_hitGeometryPlace!=-1)return false;
 if(spriteAt(320,240)!=expected||_hitGeometryDecodes==warmed)return false;
 Common::File file;if(!file.open(Common::FSNode(root.join("PLACES/P536/MEGAFILE.HYP"))))return false;
 const Frame*first=spriteFrameAt(_scene,0,0);if(!first)return false;const BitmapRef good=first->image;int width,height;
 if(!spriteImageDimensions(file,good,width,height))return false;const uint size=_hitGeometry.size();
 for(uint mode=0;mode<3;++mode){BitmapRef bad=good;if(!mode)bad.size=0;else if(mode==1)bad.size=16*1024*1024+1;else bad.offset=uint32(file.size());const uint32 before=_hitGeometryDecodes;for(uint repeat=0;repeat<2;++repeat)if(spriteImageDimensions(file,bad,width,height))return false;if(_hitGeometry.size()!=size||_hitGeometryDecodes-before!=2)return false;}
 if(!spriteImageDimensions(file,good,width,height)||_hitGeometry.size()!=size)return false;
 debug("Hit geometry verification: PASS (%u original scenes,%u oracle queries,%u hidden controls,%u unknown-frame cases,%u unsupported states;warm repeats,reload,missing file,unpoisoned failures)",uint(ARRAYSIZE(places)),queries,hidden,unknownFrames,unsupported);
 return true;
}
'''

def production(cpp,header):
 anchor='uint AstronomicaEngine::renderStaticSprites(';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,HELPER+'\n'+anchor)
 start=cpp.index('int AstronomicaEngine::spriteAt(int x, int y) {');end=cpp.index('\nvoid AstronomicaEngine::clickAt(',start)
 old=cpp[start:end];oracle=old.split('{',1)[1].rsplit('}',1)[0]
 block='''   Graphics::Surface *bmp = frame ? decodeSpriteBitmap(file, frame->image, _screen.format) : nullptr;
   if (!bmp) return -2;
   const bool mismatch = width >= 0 && (width != bmp->w || height != bmp->h);
   width = bmp->w; height = bmp->h; bmp->free(); delete bmp;'''
 assert old.count(block)==1
 cached=old.replace(block,'''   int frameWidth, frameHeight;
   if (!frame || !spriteImageDimensions(file, frame->image, frameWidth, frameHeight)) return -2;
   const bool mismatch = width >= 0 && (width != frameWidth || height != frameHeight);
   width = frameWidth; height = frameHeight;''')
 cpp=cpp[:start]+cached+cpp[end:]
 anchor=' _scene = parsed;';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,anchor+'\n _hitGeometry.clear(); _hitGeometryPlace = -1;')
 anchor=' void configureHover();';assert header.count(anchor)==1;header=header.replace(anchor,''' struct HitGeometry { uint32 offset, size; int width, height; };
 Common::Array<HitGeometry> _hitGeometry;
 int _hitGeometryPlace = -1;
 uint32 _hitGeometryDecodes = 0;
 bool spriteImageDimensions(Common::SeekableReadStream &file, const BitmapRef &image, int &width, int &height);
 bool verifyHitGeometry();
'''+anchor)
 # The oracle lives only in the explicit native verification entry point.
 cpp=cpp.replace('bool AstronomicaEngine::verifyBuilderPuzzle() {',TEST.replace('@ORACLE@',oracle)+'\nbool AstronomicaEngine::verifyBuilderPuzzle() {')
 anchor=' if(ConfMan.hasKey("astronomica_verify_p281_saves")';assert cpp.count(anchor)==1
 cpp=cpp.replace(anchor,''' if(ConfMan.hasKey("astronomica_verify_hit_geometry")&&ConfMan.getBool("astronomica_verify_hit_geometry")) {
  const bool ok=verifyHitGeometry();_background.free();_screen.free();quitGame();return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"Hit geometry verification failed");
 }
'''+anchor)
 return cpp,header
