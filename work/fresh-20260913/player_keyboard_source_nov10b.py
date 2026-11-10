"""Route real player keys through the original input lock; gate diagnostic shortcuts."""
TEST=r'''
bool AstronomicaEngine::verifyKeyboardRouting() {
 auto quiet=[&](int place){ConfMan.setBool("astronomica_entry_scripts",false);return loadPlace(place,false,true);};
 ConfMan.removeKey("astronomica_debug_controls",ConfMan.getActiveDomainName());
 // Enter the actual original P27 sprite click and execute its first block command.
 if(!quiet(27)||_scene.sprites.empty())return false;
 Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P27/MEGAFILE.HYP"))))return false;
 const Frame*frame=staticSpriteFrame(_scene,0);Graphics::Surface*bmp=frame?decodeSpriteBitmap(file,frame->image,_screen.format):nullptr;if(!bmp)return false;
 const int x=_scene.sprites[0].renderX+bmp->w/2,y=_scene.sprites[0].renderY+bmp->h/2;bmp->free();delete bmp;
 if(spriteAt(x,y)!=0)return false;clickAtTime(x,y,scriptClock());runScriptsAt(scriptClock());
 if(!_runner.clicksBlocked()||!_runner.pendingCount())return false;
 const Common::KeyCode blocked[]={Common::KEYCODE_LEFT,Common::KEYCODE_UP,Common::KEYCODE_RIGHT,Common::KEYCODE_PAGEUP,Common::KEYCODE_PAGEDOWN,Common::KEYCODE_v,Common::KEYCODE_m,Common::KEYCODE_r,Common::KEYCODE_c,Common::KEYCODE_f};
 {PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();for(bool diagnostic:{false,true}){ConfMan.setBool("astronomica_debug_controls",diagnostic);for(Common::KeyCode key:blocked){handleGameKey(Common::KeyState(key));if(p510WholeLiveHash()!=before)return false;}}}
 debug("Player keyboard blocked: PASS (20 keys,actual original P27 block/pending queue,all live game state preserved)");
 // Global menu remains usable during the original lock and preserves its queue.
 const uint32 runner=_runner.p510CompleteHash(),pixels=screenRGBHash(_screen);Common::Event escape;escape.type=Common::EVENT_KEYDOWN;escape.kbd.keycode=Common::KEYCODE_ESCAPE;_eventMan->pushEvent(escape);
 handleGameKey(Common::KeyState(Common::KEYCODE_F5));if(_place!=27||_runner.p510CompleteHash()!=runner||screenRGBHash(_screen)!=pixels||!_runner.clicksBlocked()||_clockPaused||shouldQuit())return false;
 debug("Player keyboard menu: PASS (F5 during original lock,actual dialog closes,queue/pixels preserved)");
 struct Check {int place;Common::KeyCode key;};const Check diagnosticKeys[]={{29,Common::KEYCODE_v},{517,Common::KEYCODE_m},{510,Common::KEYCODE_m},{510,Common::KEYCODE_r},{510,Common::KEYCODE_c},{510,Common::KEYCODE_f},{103,Common::KEYCODE_PAGEUP},{103,Common::KEYCODE_PAGEDOWN}};
 for(uint present=0;present<2;++present){if(present)ConfMan.setBool("astronomica_debug_controls",false);else ConfMan.removeKey("astronomica_debug_controls",ConfMan.getActiveDomainName());for(const Check&c:diagnosticKeys){if(!quiet(c.place))return false;PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();handleGameKey(Common::KeyState(c.key));if(p510WholeLiveHash()!=before)return false;}}
 debug("Player keyboard diagnostics: PASS (16 absent/false option cases,no scene skip/demonstration in player mode)");
 ConfMan.setBool("astronomica_debug_controls",false);
 const Common::KeyCode arrows[]={Common::KEYCODE_LEFT,Common::KEYCODE_UP,Common::KEYCODE_RIGHT};
 for(uint i=0;i<3;++i){if(!quiet(103))return false;const int expected=_nav[i]>0?_nav[i]:103;handleGameKey(Common::KeyState(arrows[i]));if(_place!=expected)return false;}
 for(byte modifier:{byte(Common::KBD_CTRL),byte(Common::KBD_ALT),byte(Common::KBD_META)})for(Common::KeyCode key:arrows){if(!quiet(103))return false;PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();handleGameKey(Common::KeyState(key,0,modifier));if(p510WholeLiveHash()!=before)return false;}
 debug("Player keyboard navigation: PASS (three original nav targets,nine modified arrows ignored)");
 // Explicit development opt-in keeps the old visibility diagnostic available.
 ConfMan.setBool("astronomica_debug_controls",true);if(!quiet(29))return false;const bool visible=_scene.sprites[1].visible;
 handleGameKey(Common::KeyState(Common::KEYCODE_v));for(uint i=0;i<8&&_runner.pendingCount();++i)runScriptsAt(scriptClock()+1000+i);
 if(bool(_scene.sprites[1].visible)==visible)return false;ConfMan.setBool("astronomica_debug_controls",false);
 handleGameKey(Common::KeyState(Common::KEYCODE_ESCAPE));if(!shouldQuit())return false;
 debug("Player keyboard verification: PASS (original block,diagnostics opt-in,nav,modified keys,F5 and Escape)");return true;
}
'''
BASELINE=r'''
 if(ConfMan.hasKey("astronomica_verify_keyboard_baseline")&&ConfMan.getBool("astronomica_verify_keyboard_baseline")) {
  ConfMan.setBool("astronomica_entry_scripts",false);if(!loadPlace(27,false,true))return Common::kReadingFailed;
  Common::File file;file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P27/MEGAFILE.HYP")));const Frame*f=staticSpriteFrame(_scene,0);Graphics::Surface*bmp=f?decodeSpriteBitmap(file,f->image,_screen.format):nullptr;if(!bmp)return Common::kReadingFailed;
  const int x=_scene.sprites[0].renderX+bmp->w/2,y=_scene.sprites[0].renderY+bmp->h/2;bmp->free();delete bmp;if(spriteAt(x,y)!=0)return Common::kReadingFailed;
  clickAtTime(x,y,scriptClock());runScriptsAt(scriptClock());const bool blocked=_runner.clicksBlocked();const uint pending=_runner.pendingCount();const int target=_nav[2];
  handleGameKey(Common::KeyState(Common::KEYCODE_RIGHT));debug("Original keyboard counterexample: blocked%d pending%u P27 rightTarget%d actualP%d",blocked,pending,target,_place);
  _background.free();_screen.free();quitGame();return blocked&&pending&&target>0&&_place==target?Common::kNoError:Common::kReadingFailed;
 }
'''
def production(cpp,header,guard=True):
 start=cpp.index('   switch (event.kbd.keycode) {');end=cpp.index('\n   }\n  }\n  runScripts();',start)+len('\n   }');old=cpp[start:end]
 switch=old.replace('event.kbd.keycode','key.keycode')
 if guard:
  for line in('   case Common::KEYCODE_F5: openMainMenuDialog(); break;\n','   case Common::KEYCODE_ESCAPE: quitGame(); break;\n'):
   assert switch.count(line)==1;switch=switch.replace(line,'')
  prefix=''' if(key.keycode==Common::KEYCODE_F5){openMainMenuDialog();return;}
 if(key.keycode==Common::KEYCODE_ESCAPE){quitGame();return;}
 if((key.flags&(Common::KBD_CTRL|Common::KBD_ALT|Common::KBD_META))||_runner.clicksBlocked())return;
 const bool diagnostic=ConfMan.hasKey("astronomica_debug_controls")&&ConfMan.getBool("astronomica_debug_controls");
 if(!diagnostic&&(key.keycode==Common::KEYCODE_v||key.keycode==Common::KEYCODE_m||key.keycode==Common::KEYCODE_r||key.keycode==Common::KEYCODE_c||key.keycode==Common::KEYCODE_f||key.keycode==Common::KEYCODE_PAGEUP||key.keycode==Common::KEYCODE_PAGEDOWN))return;
'''
 else:prefix=''
 method='void AstronomicaEngine::handleGameKey(const Common::KeyState &key) {\n'+prefix+switch+'\n}\n'
 cpp=cpp[:start]+'   handleGameKey(event.kbd);'+cpp[end:]
 anchor='bool AstronomicaEngine::verifyBuilderPuzzle() {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,method+'\n'+(TEST if guard else'')+'\n'+anchor)
 anchor=' if(ConfMan.hasKey("astronomica_verify_hit_geometry")';assert cpp.count(anchor)==1
 branch=''' if(ConfMan.hasKey("astronomica_verify_keyboard")&&ConfMan.getBool("astronomica_verify_keyboard")) {
  const bool ok=verifyKeyboardRouting();debug("Player keyboard native result: %s",ok?"PASS":"FAIL");_background.free();_screen.free();quitGame();return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"Keyboard verification failed");
 }
'''if guard else BASELINE
 cpp=cpp.replace(anchor,branch+'\n'+anchor)
 anchor='#include "engines/engine.h"';assert header.count(anchor)==1;header=header.replace(anchor,anchor+'\n#include "common/keyboard.h"')
 anchor=' void configureHover();';assert header.count(anchor)==1;header=header.replace(anchor,' void handleGameKey(const Common::KeyState &key);\n bool verifyKeyboardRouting();\n'+anchor)
 return cpp,header
