"""Keep cursor selection consistent when synchronous intro rendering replaces an exit-hover room."""
from intro_menu_source_nov12b import production as previous,baseline as previous_baseline,FIXED_PROBE
FINAL_PROBE=FIXED_PROBE.replace('int&place;','int&place;int&cursorIndex;int cursorDuringIntro=-99;bool cursorVisible=false;').replace('AstronomicaEngine*e,int&pl):','AstronomicaEngine*e,int&pl,int&ci):').replace('engine(e),place(pl){}','engine(e),place(pl),cursorIndex(ci){}').replace('this,_place);','this,_place,_navigationCursorIndex);').replace('if(!first){first=true;sentAt=now;','if(!first){first=true;cursorDuringIntro=cursorIndex;cursorVisible=CursorMan.isVisible();sentAt=now;')
FINAL_PROBE=FINAL_PROBE.replace('  const bool expected=ConfMan.getBool("astronomica_intro_menu_expected");','  const bool prepared=loadPlace(103,false,true);updateNavigationCursor(0,100);if(!prepared||_navigationCursorIndex!=0){debug("Introduction cursor preparation: FAIL");quitGame();return Common::kNoError;}\n  const bool expected=ConfMan.getBool("astronomica_intro_menu_expected");')
FINAL_PROBE=FINAL_PROBE.replace('if(expected)ok=keys.sawPause&&','if(expected)ok=keys.cursorDuringIntro==-1&&keys.cursorVisible&&keys.sawPause&&').replace('else ok=!keys.sawPause&&!held&&ok;','else ok=keys.cursorDuringIntro==0&&keys.cursorVisible&&!keys.sawPause&&!held&&ok;')
FINAL_PROBE=FINAL_PROBE.replace('wall%u,pending%u)','wall%u,cursor%d,visible%d,pending%u)').replace('_system->getMillis()-wallBefore,_runner.pendingCount()','_system->getMillis()-wallBefore,keys.cursorDuringIntro,int(keys.cursorVisible),_runner.pendingCount()')
def change_probe(cpp,header):
 assert cpp.count(FIXED_PROBE)==1;return cpp.replace(FIXED_PROBE,FINAL_PROBE),header
def baseline(cpp,header):return change_probe(*previous_baseline(cpp,header))
def production(cpp,header):
 cpp,header=previous(cpp,header);assert cpp.count('    _introductionActive=true;')==1
 cpp=cpp.replace('    _introductionActive=true;','    _introductionActive=true;\n    const Common::Point introMouse=_eventMan->getMousePos();updateNavigationCursor(introMouse.x,introMouse.y);')
 return change_probe(cpp,header)
