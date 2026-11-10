"""Exercise the actual global menu, not an engine-error fallback dialog."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_global_menu")&&ConfMan.getBool("astronomica_verify_global_menu")) {
  const Graphics::Font *big=FontMan.getFontByUsage(Graphics::FontManager::kBigGUIFont),*named=FontMan.getFontByName("helvb12.bdf");
  debug("Global menu font probe: big%d named%d same%d height%d",big!=nullptr,named!=nullptr,big==named,big?big->getFontHeight():-1);
  Common::Event escape;escape.type=Common::EVENT_KEYDOWN;escape.kbd.keycode=Common::KEYCODE_ESCAPE;_eventMan->pushEvent(escape);
  const int oldPlace=_place;const uint32 before=screenRGBHash(_screen);openMainMenuDialog();
  const bool ok=_place==oldPlace&&screenRGBHash(_screen)==before&&!_clockPaused;
  debug("Global menu actual open-close: %s (P%d,screen preserved,clock resumed)",ok?"PASS":"FAIL",_place);
  _background.free();_screen.free();quitGame();return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"Global menu verification failed");
 }
'''
def inject(cpp):
 anchor=' if(ConfMan.hasKey("astronomica_verify_hit_geometry")';assert cpp.count(anchor)==1;return cpp.replace(anchor,PROBE+'\n'+anchor)
