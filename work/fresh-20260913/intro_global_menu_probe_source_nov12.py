"""Diagnostic only:standard EVENT_MAINMENUuses the same transient load/save protection."""
from intro_menu_source_nov12c import FINAL_PROBE
GLOBAL_PROBE=FINAL_PROBE.replace('e.type=Common::EVENT_KEYDOWN;e.kbd.keycode=Common::KEYCODE_F5;','e.type=Common::EVENT_MAINMENU;').replace('else ok=keys.cursorDuringIntro==0&&keys.cursorVisible&&!keys.sawPause&&!held&&ok;','else ok=keys.cursorDuringIntro==0&&keys.cursorVisible&&keys.sawPause&&!keys.loadBlocked&&held>=100&&keys.audioAtEscape>=keys.audioAtPause&&keys.audioAtEscape-keys.audioAtPause<50&&ok;').replace('Introduction actual menu:','Introduction global menu:')
def inject(cpp,script):
 if FINAL_PROBE in cpp:
  assert cpp.count(FINAL_PROBE)==1;return cpp.replace(FINAL_PROBE,GLOBAL_PROBE),script
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }';assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+GLOBAL_PROBE),script
