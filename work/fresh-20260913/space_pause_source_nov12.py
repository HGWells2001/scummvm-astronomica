"""Implement the standard ScummVMspace-pause action without changing puzzle or save state."""
from intro_menu_source_nov12c import FINAL_PROBE
NORMAL=r'''
  class ResumeSpace:public Common::EventSource {
   OSystem*hostSystem;bool&paused;uint32 since=0;
  public:bool saw=false,sent=false;
   ResumeSpace(OSystem*s,bool&p):hostSystem(s),paused(p){}
   bool allowMapping()const override{return false;}
   bool pollEvent(Common::Event&e)override{if(!paused)return false;if(!saw){saw=true;since=hostSystem->getMillis();}if(!sent&&uint32(hostSystem->getMillis()-since)>=300){sent=true;e.type=Common::EVENT_KEYDOWN;e.kbd=Common::KeyState(Common::KEYCODE_SPACE);return true;}return false;}
  };
  auto normalPause=[&](int scene,bool locked){
   if(!loadPlace(scene,false,true))return false;updateNavigationCursor(0,100);
   if(locked){Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P27/MEGAFILE.HYP"))))return false;const Frame*f=staticSpriteFrame(_scene,0);Graphics::Surface*bmp=f?decodeSpriteBitmap(file,f->image,_screen.format):nullptr;if(!bmp)return false;const int x=_scene.sprites[0].renderX+bmp->w/2,y=_scene.sprites[0].renderY+bmp->h/2;bmp->free();delete bmp;const uint32 now=scriptClock();clickAtTime(x,y,now);runScriptsAt(now);if(!_runner.clicksBlocked()||!_runner.pendingCount())return false;}
   const uint32 runner=_runner.p510CompleteHash(),pixels=screenRGBHash(_screen);const int cursor=_navigationCursorIndex;const bool visible=CursorMan.isVisible();bool modifiers=true;
   for(byte flag:{byte(Common::KBD_CTRL),byte(Common::KBD_ALT),byte(Common::KBD_META)}){ResumeSpace fallback(_system,_clockPaused);const uint32 before=_pausedMillis;_eventMan->getEventDispatcher()->registerSource(&fallback,false);handleGameKey(Common::KeyState(Common::KEYCODE_SPACE,' ',flag));_eventMan->getEventDispatcher()->unregisterSource(&fallback);modifiers=!fallback.saw&&_pausedMillis==before&&modifiers;}
   ResumeSpace resume(_system,_clockPaused);const uint32 epoch=_pausedMillis,clock=scriptClock();_eventMan->getEventDispatcher()->registerSource(&resume,false);handleGameKey(Common::KeyState(Common::KEYCODE_SPACE));_eventMan->getEventDispatcher()->unregisterSource(&resume);
   const uint32 held=_pausedMillis-epoch,clockDelta=scriptClock()-clock;const bool stable=_place==scene&&_runner.p510CompleteHash()==runner&&screenRGBHash(_screen)==pixels&&_navigationCursorIndex==cursor&&CursorMan.isVisible()==visible&&!_clockPaused&&!shouldQuit();
   const bool result=modifiers&&stable&&clockDelta<100&&resume.saw==expected&&(expected?held>=100:held==0);
   debug("Space room pause: %s (P%d,expected%d,paused%d,held%u,clock%u,modifiers%d,stable%d)",result?"PASS":"FAIL",scene,int(expected),int(resume.saw),held,clockDelta,int(modifiers),int(stable));return result;
  };
  ok=normalPause(103,false)&&ok;ok=normalPause(27,true)&&ok;
  debug("Space pause native result: %s",ok?"PASS":"FAIL");
'''
SPACE_PROBE=FINAL_PROBE.replace('astronomica_verify_intro_menu','astronomica_verify_space_pause').replace('astronomica_intro_menu_expected','astronomica_space_pause_expected').replace('e.kbd.keycode=Common::KEYCODE_F5;','e.kbd=Common::KeyState(Common::KEYCODE_SPACE);').replace('e.kbd.keycode=Common::KEYCODE_ESCAPE;','e.kbd=Common::KeyState(Common::KEYCODE_SPACE);').replace('else ok=keys.cursorDuringIntro==0&&','else ok=keys.cursorDuringIntro==-1&&').replace('Introduction actual menu:','Space spoken pause:')
tail='  _background.free();_screen.free();quitGame();return Common::kNoError;';assert SPACE_PROBE.count(tail)==1;SPACE_PROBE=SPACE_PROBE.replace(tail,NORMAL+tail)
PAUSE=r'''
void AstronomicaEngine::pauseForPlayer() {
 class PlayerPauseDialog:public GUI::MessageDialog {
 public:PlayerPauseDialog():GUI::MessageDialog(_("Game paused"),_("Resume")){}
 protected:void handleKeyDown(Common::KeyState key)override{
  if(key.keycode==Common::KEYCODE_SPACE&&!(key.flags&(Common::KBD_CTRL|Common::KBD_ALT|Common::KBD_META)))close();
  else GUI::MessageDialog::handleKeyDown(key);
 }
 } dialog;
 runDialog(dialog);
}
'''
def add_probe(cpp):
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }';assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+SPACE_PROBE)
def baseline(cpp,header):return add_probe(cpp),header
def production(cpp,header):
 assert header.count('private:\n')==1;header=header.replace('private:\n','private:\n void pauseForPlayer();\n')
 for name in ['gui/message.h','common/translation.h']:
  if '#include "'+name+'"'not in cpp:cpp=cpp.replace('#include "graphics/cursorman.h"','#include "'+name+'"\n#include "graphics/cursorman.h"')
 anchor='void AstronomicaEngine::handleGameKey(const Common::KeyState &key) {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,PAUSE+'\n'+anchor)
 key=' if(key.keycode==Common::KEYCODE_F5){openMainMenuDialog();return;}';assert cpp.count(key)==1
 cpp=cpp.replace(key,key+'\n if(key.keycode==Common::KEYCODE_SPACE&&!(key.flags&(Common::KBD_CTRL|Common::KBD_ALT|Common::KBD_META))){pauseForPlayer();return;}')
 intro='      else if(event.type==Common::EVENT_KEYDOWN&&event.kbd.keycode==Common::KEYCODE_F5)openMainMenuDialog();';assert cpp.count(intro)==1
 cpp=cpp.replace(intro,intro+'\n      else if(event.type==Common::EVENT_KEYDOWN&&event.kbd.keycode==Common::KEYCODE_SPACE&&!(event.kbd.flags&(Common::KBD_CTRL|Common::KBD_ALT|Common::KBD_META)))pauseForPlayer();')
 verifier=' if (ConfMan.hasKey("astronomica_verify") && ConfMan.getBool("astronomica_verify")) {\n  bool scriptsOK = verifyScriptRunner()';assert cpp.count(verifier)==1
 setup='\n  // Establish this diagnostic\'s initial render-only contract;normal gameplay defaults stay enabled.\n'+''.join('  ConfMan.setBool("'+key+'",false);\n'for key in ['astronomica_audio','astronomica_animation','astronomica_sprite_input','astronomica_entry_scripts'])
 cpp=cpp.replace(verifier,verifier.replace('\n  bool scriptsOK',setup+'  bool scriptsOK'))
 return add_probe(cpp),header
