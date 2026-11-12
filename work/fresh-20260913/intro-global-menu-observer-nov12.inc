
 if(ConfMan.hasKey("astronomica_verify_intro_menu")&&ConfMan.getBool("astronomica_verify_intro_menu")) {
  class IntroKeys:public Common::EventSource {
  public:
   OSystem*hostSystem;Audio::Mixer*mixer;Audio::SoundHandle&handle;bool&paused;AstronomicaEngine*engine;int&place;int&cursorIndex;int cursorDuringIntro=-99;bool cursorVisible=false;
   bool first=false,escape=false,sawPause=false,saveBlocked=false,loadBlocked=false;uint32 sentAt=0,audioAtPause=0,audioAtEscape=0;
   IntroKeys(OSystem*s,Audio::Mixer*m,Audio::SoundHandle&h,bool&p,AstronomicaEngine*e,int&pl,int&ci):hostSystem(s),mixer(m),handle(h),paused(p),engine(e),place(pl),cursorIndex(ci){}
   bool allowMapping()const override{return false;}
   bool pollEvent(Common::Event&e)override{
    if(place!=501||!mixer->isSoundHandleActive(handle))return false;
    const uint32 now=hostSystem->getMillis();
    if(paused&&!sawPause){sawPause=true;audioAtPause=mixer->getSoundElapsedTime(handle);saveBlocked=!engine->canSaveGameStateCurrently();loadBlocked=!engine->canLoadGameStateCurrently();}
    if(!first){first=true;cursorDuringIntro=cursorIndex;cursorVisible=CursorMan.isVisible();sentAt=now;e.type=Common::EVENT_MAINMENU;return true;}
    if(!escape&&uint32(now-sentAt)>=300){escape=true;audioAtEscape=mixer->getSoundElapsedTime(handle);e.type=Common::EVENT_KEYDOWN;e.kbd.keycode=Common::KEYCODE_ESCAPE;return true;}
    return false;
   }
  } keys(_system,_mixer,_soundHandle,_clockPaused,this,_place,_navigationCursorIndex);
  const bool prepared=loadPlace(103,false,true);updateNavigationCursor(0,100);if(!prepared||_navigationCursorIndex!=0){debug("Introduction cursor preparation: FAIL");quitGame();return Common::kNoError;}
  const bool expected=ConfMan.getBool("astronomica_intro_menu_expected");const uint32 pausedBefore=_pausedMillis,wallBefore=_system->getMillis();
  _eventMan->getEventDispatcher()->registerSource(&keys,false);const bool loaded=loadPlace(501);_eventMan->getEventDispatcher()->unregisterSource(&keys);
  const uint32 held=_pausedMillis-pausedBefore;bool ok=loaded&&_place==501&&keys.first&&keys.escape&&!_clockPaused&&!shouldQuit()&&!_mixer->isSoundHandleActive(_soundHandle)&&canLoadGameStateCurrently();
  if(expected)ok=keys.cursorDuringIntro==-1&&keys.cursorVisible&&keys.sawPause&&keys.saveBlocked&&keys.loadBlocked&&held>=100&&keys.audioAtEscape>=keys.audioAtPause&&keys.audioAtEscape-keys.audioAtPause<50&&ok;
  else ok=keys.cursorDuringIntro==0&&keys.cursorVisible&&keys.sawPause&&!keys.loadBlocked&&held>=100&&keys.audioAtEscape>=keys.audioAtPause&&keys.audioAtEscape-keys.audioAtPause<50&&ok;
  debug("Introduction global menu: %s (expected%d,paused%d,saveBlocked%d,loadBlocked%d,held%u,audio%u/%u,wall%u,cursor%d,visible%d,pending%u)",ok?"PASS":"FAIL",int(expected),int(keys.sawPause),int(keys.saveBlocked),int(keys.loadBlocked),held,keys.audioAtPause,keys.audioAtEscape,_system->getMillis()-wallBefore,keys.cursorDuringIntro,int(keys.cursorVisible),_runner.pendingCount());
  _background.free();_screen.free();quitGame();return Common::kNoError;
 }
