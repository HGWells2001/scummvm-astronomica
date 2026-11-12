"""Accept the directional key events emitted by ScummVM's standard controller keymap."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_mapped_navigation")&&ConfMan.getBool("astronomica_verify_mapped_navigation")){
  const bool expected=ConfMan.getBool("astronomica_mapped_navigation_expected");bool ok=true;
  Common::KeymapArray maps=getMetaEngine()->initKeymaps(ConfMan.getActiveDomainName().c_str());
  const char*ids[]={Common::kStandardActionMoveLeft,Common::kStandardActionMoveUp,Common::kStandardActionMoveRight};
  const char*joy[]={"JOY_LEFT","JOY_UP","JOY_RIGHT"};const Common::KeyCode pad[]={Common::KEYCODE_KP4,Common::KEYCODE_KP8,Common::KEYCODE_KP6};
  Common::KeyCode mapped[3]={Common::KEYCODE_INVALID,Common::KEYCODE_INVALID,Common::KEYCODE_INVALID};
  for(Common::Keymap*map:maps)for(const Common::Action*action:map->getActions())for(uint d=0;d<3;++d)if(!strcmp(action->id,ids[d])){
   bool bound=false;for(const Common::String&input:action->getDefaultInputMapping())bound=input==joy[d]||bound;
   ok=bound&&action->event.type==Common::EVENT_KEYDOWN&&action->event.kbd.keycode==pad[d]&&ok;mapped[d]=action->event.kbd.keycode;
  }
  for(Common::Keymap*map:maps)delete map;
  for(uint d=0;d<3;++d)ok=mapped[d]==pad[d]&&ok;
  debug("Mapped navigation default keymap: %s (JOY_LEFT/KP4,JOY_UP/KP8,JOY_RIGHT/KP6)",ok?"PASS":"FAIL");
  for(const char*option:{"astronomica_audio","astronomica_animation","astronomica_sprite_input","astronomica_entry_scripts"})ConfMan.setBool(option,false);
  auto quiet=[&](int scene){_runner.resetGlobals();_runner.seedRandom(0x12345+uint(scene));_puzzlesCompleted=0;return loadPlace(scene,false,true);};
  uint scenes=0,routes=0;uint32 digest=2166136261U;
  const int originalScenes[]={101,103,106,107,108,109,110,111,112,113,114,115,117,120,122,125,128,129,130,131,134,136,139,141,144,145,146,147,148,149,150,151,152,155,157,160,162,165,166,167,168,169,172,174,177,179,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,266,268,27,271,273,276,279,28,281,284,286,289,29,290,291,292,293,294,295,296,297,298,299,30,302,304,307,309,31,312,313,314,315,316,319,32,321,324,326,329,33,330,331,332,333,334,335,336,337,338,339,34,340,341,342,343,344,345,346,347,348,349,35,350,351,352,353,354,355,356,357,358,359,36,360,361,362,363,364,365,366,367,368,369,37,370,371,372,373,374,375,376,377,378,379,38,380,381,382,383,384,385,386,387,388,389,39,40,403,404,405,407,41,410,411,412,413,414,415,416,417,418,419,42,420,421,43,430,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,96,98};
  for(int scene:originalScenes){
   if(scene==406)continue;
   if(!quiet(scene)){ok=false;break;}
   if(_scene.mode!=1)continue;
   const int destinations[]={_nav[0],_nav[1],_nav[2]};bool counted=false;
   for(uint d=0;d<3;++d){
    if(destinations[d]<=0)continue;
    if(!quiet(scene)){ok=false;break;}
    handleGameKey(Common::KeyState(d==0?Common::KEYCODE_LEFT:d==1?Common::KEYCODE_UP:Common::KEYCODE_RIGHT));
    const int wanted=_place;Common::Array<int32>globals;for(int i=0;i<100;++i){int32 v=0;if(!_runner.getValue(0,i,v))ok=false;globals.push_back(v);}
    if(!quiet(scene)){ok=false;break;}
    handleGameKey(Common::KeyState(mapped[d]));
    ok=_place==(expected?wanted:scene)&&ok;
    if(expected)for(int i=0;i<100;++i){int32 v=0;ok=_runner.getValue(0,i,v)&&v==globals[i]&&ok;}
    for(uint32 v:{uint32(scene),d,uint32(wanted),uint32(_place)})digest=(digest^v)*16777619U;
    ++routes;counted=true;
   }
   scenes+=counted;
  }
  ok=routes==760&&scenes==306&&ok;
  debug("Mapped navigation original routes: %s (expected%d,scenes%u,routes%u,hash%08x)",ok?"PASS":"FAIL",int(expected),scenes,routes,digest);
  // Use the real original P27 button to establish the script input lock.
  ConfMan.setBool("astronomica_sprite_input",true);ConfMan.setBool("astronomica_animation",true);
  bool locked=quiet(27);Common::File file;locked=file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P27/MEGAFILE.HYP")))&&locked;
  const Frame*f=locked?staticSpriteFrame(_scene,0):nullptr;Graphics::Surface*bmp=f?decodeSpriteBitmap(file,f->image,_screen.format):nullptr;
  if(bmp){const int x=_scene.sprites[0].renderX+bmp->w/2,y=_scene.sprites[0].renderY+bmp->h/2;bmp->free();delete bmp;const uint32 now=scriptClock();clickAtTime(x,y,now);runScriptsAt(now);locked=_runner.clicksBlocked()&&_runner.pendingCount();}else locked=false;
  if(locked){PauseToken pause=pauseEngine();const uint32 hash=p510WholeLiveHash();for(Common::KeyCode key:mapped){handleGameKey(Common::KeyState(key));locked=p510WholeLiveHash()==hash&&locked;}}
  ok=locked&&ok;debug("Mapped navigation actual lock: %s",locked?"PASS":"FAIL");
  bool modifiers=true;for(byte flag:{byte(Common::KBD_CTRL),byte(Common::KBD_ALT),byte(Common::KBD_META)})for(Common::KeyCode key:mapped){if(!quiet(103)){modifiers=false;continue;}PauseToken pause=pauseEngine();const uint32 hash=p510WholeLiveHash();handleGameKey(Common::KeyState(key,0,flag));modifiers=p510WholeLiveHash()==hash&&modifiers;}
  ok=modifiers&&ok;debug("Mapped navigation modifiers: %s",modifiers?"PASS":"FAIL");
  debug("Mapped navigation native result: %s",ok?"PASS":"FAIL");_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def baseline(cpp,header):
 for name in ['engines/metaengine.h','backends/keymapper/action.h','backends/keymapper/keymap.h','backends/keymapper/standard-actions.h']:
  if '#include "'+name+'"'not in cpp:cpp=cpp.replace('#include "graphics/cursorman.h"','#include "'+name+'"\n#include "graphics/cursorman.h"')
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }';assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+PROBE),header

def production(cpp,header):
 for arrow,pad in [('LEFT','KP4'),('UP','KP8'),('RIGHT','KP6')]:
  old='case Common::KEYCODE_'+arrow+': if (_nav[';assert cpp.count(old)==1
  cpp=cpp.replace(old,'case Common::KEYCODE_'+pad+': '+old)
 return baseline(cpp,header)
