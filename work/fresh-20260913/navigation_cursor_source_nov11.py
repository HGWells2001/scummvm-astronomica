"""Use the original NE navigation arrows with derived UI ownership only."""
METHODS=r'''
void AstronomicaEngine::clearNavigationCursors() {
 if(_navigationCursorIndex>=0)CursorMan.setDefaultArrowCursor();
 for(uint i=0;i<3;++i){delete _navigationCursors[i];_navigationCursors[i]=nullptr;}
 _navigationCursorIndex=-1;_navigationCursorAttempted=false;
}
bool AstronomicaEngine::ensureNavigationCursors() {
 if(_navigationCursorAttempted)return _navigationCursors[0]&&_navigationCursors[1]&&_navigationCursors[2];
 _navigationCursorAttempted=true;
 Common::Path exe=ConfMan.getPath("path").join("ASTRO.EXE");
 if(!universeFileIdentity(exe,418376,1628467759U))exe=ConfMan.getPath("path").join("SETUP/ASTRO.EXE");
 if(!universeFileIdentity(exe,418376,1628467759U))return false;
 Common::File*file=new Common::File();if(!file->open(Common::FSNode(exe))){delete file;return false;}
 Common::NEResources resources;if(!resources.loadFromEXE(file))return false;
 // _do_place9:00f0-012b loads handles; _place_loop selects2left/1top/3right.
 const uint32 groupIds[]={2,1,3};Graphics::WinCursorGroup*groups[3]={};bool valid=true;
 for(uint i=0;i<3&&valid;++i){
  groups[i]=Graphics::WinCursorGroup::createCursorGroup(&resources,Common::WinResourceID(groupIds[i]));
  if(!groups[i]||groups[i]->cursors.size()!=1){valid=false;break;}
  const Graphics::Cursor*c=groups[i]->cursors[0].cursor;
  valid=c&&c->getSurface()&&c->getPalette()&&c->getWidth()==32&&c->getHeight()==32&&c->getHotspotX()<32&&c->getHotspotY()<32;
 }
 if(!valid){for(uint i=0;i<3;++i)delete groups[i];return false;}
 for(uint i=0;i<3;++i)_navigationCursors[i]=groups[i];return true;
}
void AstronomicaEngine::updateNavigationCursor(int x,int y) {
 int direction=-1;
 if(_scene.mode==1){
  // Original hover _in_mr9:0dbd-0dfb tests nonempty rectangle click lists.
  // Click consumption independently includes empty rectangles in _do_mouse.
  bool rectangle=false;for(const MouseRect&r:_scene.mouseRects)if(!r.click.empty()&&x>=r.rect[0]&&y>=r.rect[1]&&x<r.rect[2]&&y<r.rect[3]){rectangle=true;break;}
  if(!rectangle){const int hit=navigationDirectionAt(x,y);if(hit>=0&&_nav[hit]!=0)direction=hit;}
 }
 if(direction>=0&&!ensureNavigationCursors())direction=-1;
 if(direction==_navigationCursorIndex)return;
 if(direction>=0)CursorMan.replaceCursor(_navigationCursors[direction]->cursors[0].cursor);
 else CursorMan.setDefaultArrowCursor();
 _navigationCursorIndex=direction;
}
'''
TEST=r'''
bool AstronomicaEngine::verifyNavigationCursors() {
 if(!ensureNavigationCursors())return false;
 const uint expectedHotX[]={0,6,31},expectedHotY[]={6,0,6};const uint32 expectedHash[]={0x8cf023afU,0x565522f7U,0x11480b87U};
 for(uint i=0;i<3;++i){
  const Graphics::Cursor*c=_navigationCursors[i]->cursors[0].cursor;if(c->getWidth()!=32||c->getHeight()!=32||c->getHotspotX()!=expectedHotX[i]||c->getHotspotY()!=expectedHotY[i]||c->getPaletteCount()<2)return false;
  const byte*palette=c->getPalette();for(uint j=0;j<6;++j)if(palette[j]!=(j<3?0:255))return false;
  const byte*pixels=c->getSurface(),*mask=c->getMask();uint32 hash=2166136261U,counts[4]={};
  for(uint j=0;j<1024;++j){uint value;if(mask){if(mask[j]==kCursorMaskTransparent)value=2;else if(mask[j]==kCursorMaskInvert)value=3;else if(mask[j]==kCursorMaskOpaque&&pixels[j]<2)value=pixels[j];else return false;}else{if(pixels[j]==c->getKeyColor())value=2;else if(pixels[j]<2)value=pixels[j];else return false;}++counts[value];hash=(hash^value)*16777619U;}
  if(hash!=expectedHash[i]||counts[0]!=49||counts[1]!=42||counts[2]!=933||counts[3])return false;
  debug("Navigation cursor resource: PASS (axis%u,32x32,hotspot%u/%u,classHash%08x,mask%d)",i,expectedHotX[i],expectedHotY[i],hash,mask?1:0);
 }
 auto quiet=[&](int scene){ConfMan.setBool("astronomica_entry_scripts",false);return loadPlace(scene,false,true);};
 if(!quiet(103))return false;
 const bool initiallyVisible=CursorMan.isVisible();
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();updateNavigationCursor(0,100);if(_navigationCursorIndex!=0||p510WholeLiveHash()!=before||CursorMan.isVisible()!=initiallyVisible)return false;updateNavigationCursor(639,100);if(_navigationCursorIndex!=2||p510WholeLiveHash()!=before)return false;updateNavigationCursor(100,0);if(_navigationCursorIndex!=-1||p510WholeLiveHash()!=before)return false;}
 if(!quiet(106))return false;updateNavigationCursor(100,0);if(_navigationCursorIndex!=1)return false;
 if(!quiet(103))return false;updateNavigationCursor(0,100);Graphics::WinCursorGroup*left=_navigationCursors[0];
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();Common::Event close;close.type=Common::EVENT_KEYDOWN;close.kbd.keycode=Common::KEYCODE_ESCAPE;_eventMan->pushEvent(close);openMainMenuDialog();if(p510WholeLiveHash()!=before||_navigationCursorIndex!=0||_navigationCursors[0]!=left||CursorMan.isVisible()!=initiallyVisible)return false;}
 // Shape selection never forces visibility when another owner hides the pointer.
 CursorMan.showMouse(false);updateNavigationCursor(639,100);if(CursorMan.isVisible())return false;updateNavigationCursor(100,0);if(CursorMan.isVisible())return false;CursorMan.showMouse(initiallyVisible);
 debug("Navigation cursor live UI: PASS (three directions,missing exit fallback,unchanged game state,actual F5menu,visibility ownership)");
 // Native hover consumption depends on a nonempty click list; the click path has its own rule.
 if(!quiet(103)||_scene.mouseRects.size()!=1)return false;MouseRect&r=_scene.mouseRects[0];r.rect[0]=0;r.rect[1]=50;r.rect[2]=50;r.rect[3]=270;updateNavigationCursor(10,100);if(_navigationCursorIndex!=-1)return false;r.click.clear();updateNavigationCursor(10,100);if(_navigationCursorIndex!=0)return false;
 if(!quiet(27)||_scene.sprites.empty())return false;Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P27/MEGAFILE.HYP"))))return false;const Frame*f=staticSpriteFrame(_scene,0);Graphics::Surface*bmp=f?decodeSpriteBitmap(file,f->image,_screen.format):nullptr;if(!bmp)return false;const int bx=_scene.sprites[0].renderX+bmp->w/2,by=_scene.sprites[0].renderY+bmp->h/2;bmp->free();delete bmp;clickAtTime(bx,by,scriptClock());runScriptsAt(scriptClock());if(!_runner.clicksBlocked()||!_runner.pendingCount())return false;
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();updateNavigationCursor(0,100);if(_navigationCursorIndex!=0||p510WholeLiveHash()!=before||!_runner.clicksBlocked())return false;}
 if(!quiet(103))return false;_scene.mode=0;updateNavigationCursor(0,100);if(_navigationCursorIndex!=-1)return false;
 debug("Navigation cursor original rules: PASS (nonempty rectangle hover consumption,empty rectangle arrow,hover during original lock,mode guard)");
 // Isolated save directory has no EXE; no original file or user preference is changed.
 const Common::Path original=ConfMan.getPath("path");clearNavigationCursors();ConfMan.setPath("path",ConfMan.getPath("savepath"));const bool refused=!ensureNavigationCursors();ConfMan.setPath("path",original);const bool retainedFailure=!ensureNavigationCursors();clearNavigationCursors();if(!refused||!retainedFailure||!ensureNavigationCursors())return false;
 for(uint pass=0;pass<3;++pass){clearNavigationCursors();for(uint i=0;i<3;++i)if(_navigationCursors[i])return false;if(!ensureNavigationCursors())return false;}
 updateNavigationCursor(100,0);if(CursorMan.isVisible()!=initiallyVisible)return false;
 debug("Navigation cursor ownership: PASS (missing-file fallback,cached failed attempt,three clear/reload cycles,groups own pixels after NE release)");
 debug("Navigation cursor verification: PASS (three exact original resources,selection,GUI,visibility,mode and lifetime)");return true;
}
'''
def production(cpp,header):
 anchor='#include "graphics/cursorman.h"';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,anchor+'\n#include "graphics/wincursor.h"\n#include "common/formats/winexe_ne.h"')
 anchor='AstronomicaEngine::~AstronomicaEngine() {\n';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,anchor+' clearNavigationCursors();\n')
 anchor='void AstronomicaEngine::clickAt(int x, int y) {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,METHODS+'\n'+anchor)
 anchor='bool AstronomicaEngine::verifyBuilderPuzzle() {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,TEST+'\n'+anchor)
 anchor='  updateMovie();\n  // Cursor movement must be presented';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,'  updateMovie();\n  updateNavigationCursor(mouse.x,mouse.y);\n  // Cursor movement must be presented')
 anchor=' if(ConfMan.hasKey("astronomica_verify_edge_navigation")';assert cpp.count(anchor)==1
 branch=''' if(ConfMan.hasKey("astronomica_verify_navigation_cursors")&&ConfMan.getBool("astronomica_verify_navigation_cursors")) {
  const bool ok=verifyNavigationCursors();debug("Navigation cursor native result: %s",ok?"PASS":"FAIL");_background.free();_screen.free();quitGame();return Common::kNoError;
 }
''';cpp=cpp.replace(anchor,branch+'\n'+anchor)
 anchor='namespace Video { class QuickTimeDecoder; }';assert header.count(anchor)==1;header=header.replace(anchor,anchor+'\nnamespace Graphics { struct WinCursorGroup; }')
 anchor='private:\n';assert header.count(anchor)==1
 fields=''' Graphics::WinCursorGroup *_navigationCursors[3] = {};
 bool _navigationCursorAttempted = false;
 int _navigationCursorIndex = -1;
 bool ensureNavigationCursors();
 void clearNavigationCursors();
 void updateNavigationCursor(int x,int y);
 bool verifyNavigationCursors();
''';header=header.replace(anchor,anchor+fields)
 return cpp,header
