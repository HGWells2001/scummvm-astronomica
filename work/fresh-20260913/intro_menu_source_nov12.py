"""Keep original synchronous introductions,but allow a safely paused ScummVMmenu."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_intro_menu")&&ConfMan.getBool("astronomica_verify_intro_menu")) {
  class IntroKeys:public Common::EventSource {
  public:
   OSystem*system;Audio::Mixer*mixer;Audio::SoundHandle&handle;bool&paused;AstronomicaEngine*engine;int&place;
   bool first=false,escape=false,sawPause=false,saveBlocked=false,loadBlocked=false;uint32 sentAt=0,audioAtPause=0,audioAtEscape=0;
   IntroKeys(OSystem*s,Audio::Mixer*m,Audio::SoundHandle&h,bool&p,AstronomicaEngine*e,int&pl):system(s),mixer(m),handle(h),paused(p),engine(e),place(pl){}
   bool allowMapping()const override{return false;}
   bool pollEvent(Common::Event&e)override{
    if(place!=501||!mixer->isSoundHandleActive(handle))return false;
    const uint32 now=system->getMillis();
    if(paused&&!sawPause){sawPause=true;audioAtPause=mixer->getSoundElapsedTime(handle);saveBlocked=!engine->canSaveGameStateCurrently();loadBlocked=!engine->canLoadGameStateCurrently();}
    if(!first){first=true;sentAt=now;e.type=Common::EVENT_KEYDOWN;e.kbd.keycode=Common::KEYCODE_F5;return true;}
    if(!escape&&uint32(now-sentAt)>=300){escape=true;audioAtEscape=mixer->getSoundElapsedTime(handle);e.type=Common::EVENT_KEYDOWN;e.kbd.keycode=Common::KEYCODE_ESCAPE;return true;}
    return false;
   }
  } keys(_system,_mixer,_soundHandle,_clockPaused,this,_place);
  const bool expected=ConfMan.getBool("astronomica_intro_menu_expected");const uint32 pausedBefore=_pausedMillis,wallBefore=_system->getMillis();
  _eventMan->getEventDispatcher()->registerSource(&keys,false);const bool loaded=loadPlace(501);_eventMan->getEventDispatcher()->unregisterSource(&keys);
  const uint32 held=_pausedMillis-pausedBefore;bool ok=loaded&&_place==501&&keys.first&&keys.escape&&!_clockPaused&&!shouldQuit()&&!_mixer->isSoundHandleActive(_soundHandle);
  if(expected)ok=keys.sawPause&&keys.saveBlocked&&keys.loadBlocked&&held>=100&&keys.audioAtEscape>=keys.audioAtPause&&keys.audioAtEscape-keys.audioAtPause<50&&ok;
  else ok=!keys.sawPause&&!held&&ok;
  debug("Introduction actual menu: %s (expected%d,paused%d,saveBlocked%d,loadBlocked%d,held%u,audio%u/%u,wall%u,pending%u)",ok?"PASS":"FAIL",int(expected),int(keys.sawPause),int(keys.saveBlocked),int(keys.loadBlocked),held,keys.audioAtPause,keys.audioAtEscape,_system->getMillis()-wallBefore,_runner.pendingCount());
  _background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def add_probe(cpp):
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }';assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+PROBE)
def baseline(cpp,header):return add_probe(cpp),header
def production(cpp,header):
 anchor='private:\n';assert header.count(anchor)==1;header=header.replace(anchor,anchor+' bool _introductionActive = false; // Derived UIguard;not serialized.\n')
 for signature,label in [('bool AstronomicaEngine::canSaveGameStateCurrently(Common::U32String *msg) {','save'),('bool AstronomicaEngine::canLoadGameStateCurrently(Common::U32String *msg) {','load')]:
  assert cpp.count(signature)==1;cpp=cpp.replace(signature,signature+'\n if(_introductionActive){if(msg)*msg=Common::U32String("Wait until the introduction finishes.");return false;}')
 for signature in ['Common::Error AstronomicaEngine::saveGameStream(Common::WriteStream *stream, bool) {','Common::Error AstronomicaEngine::loadGameStream(Common::SeekableReadStream *stream) {']:
  assert cpp.count(signature)==1,signature;cpp=cpp.replace(signature,signature+'\n if(_introductionActive)return Common::kReadingFailed;')
 begin=cpp.index('    while (_mixer->isSoundHandleActive(_soundHandle) && !shouldQuit()) {',cpp.index('bool AstronomicaEngine::loadPlace('));end=cpp.index('\n   }',begin);body=cpp[begin:end]
 old='''     while (_system->getEventManager()->pollEvent(event))
      if (event.type == Common::EVENT_QUIT) quitGame();''';assert body.count(old)==1
 body=body.replace(old,'''     while (_system->getEventManager()->pollEvent(event)) {
      if (event.type == Common::EVENT_QUIT) quitGame();
      else if(event.type==Common::EVENT_KEYDOWN&&event.kbd.keycode==Common::KEYCODE_F5)openMainMenuDialog();
     }''')
 cpp=cpp[:begin]+'    _introductionActive=true;\n'+body+'\n    _introductionActive=false;'+cpp[end:]
 return add_probe(cpp),header
