"""Keep menu and Space pause usable while a synchronous game voice owns the script stack."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")&&ConfMan.getBool("astronomica_verify_blocking_voice_menu")){
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",false);
  if(!loadPlace(103,false,true)){debug("Blocking voice fixture: FAIL");quitGame();return Common::kNoError;}
  const bool expected=ConfMan.getBool("astronomica_blocking_voice_expected");bool ok=true;uint cases=0;
  for(Common::KeyCode key:{Common::KEYCODE_F5,Common::KEYCODE_SPACE}){
   class VoiceKeys:public Common::EventSource{public:
    OSystem*host;Audio::Mixer*mixer;Audio::SoundHandle&handle;bool&paused;AstronomicaEngine*engine;Common::KeyCode open;
    bool first=false,closed=false,sawPause=false,saveBlocked=false,loadBlocked=false,streamBlocked=false;uint32 sent=0,atPause=0,atClose=0;
    VoiceKeys(OSystem*h,Audio::Mixer*m,Audio::SoundHandle&s,bool&p,AstronomicaEngine*e,Common::KeyCode k):host(h),mixer(m),handle(s),paused(p),engine(e),open(k){}
    bool allowMapping()const override{return false;}
    bool pollEvent(Common::Event&e)override{
     if(!mixer->isSoundHandleActive(handle))return false;uint32 now=host->getMillis();
     if(paused&&!sawPause){sawPause=true;atPause=mixer->getSoundElapsedTime(handle);saveBlocked=!engine->canSaveGameStateCurrently();loadBlocked=!engine->canLoadGameStateCurrently();Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);byte junk[8]={};Common::MemoryReadStream in(junk,sizeof(junk));streamBlocked=engine->saveGameStream(&out,false).getCode()!=Common::kNoError&&out.size()==0&&engine->loadGameStream(&in).getCode()!=Common::kNoError&&in.pos()==0;}
     if(!first){first=true;sent=now;e.type=Common::EVENT_KEYDOWN;e.kbd=Common::KeyState(open);return true;}
     if(!closed&&uint32(now-sent)>=300){closed=true;atClose=mixer->getSoundElapsedTime(handle);e.type=Common::EVENT_KEYDOWN;e.kbd=Common::KeyState(Common::KEYCODE_ESCAPE);return true;}return false;
    }
   } events(_system,_mixer,_soundHandle,_clockPaused,this,key);
   const uint32 pauseBefore=_pausedMillis,wallBefore=_system->getMillis(),runnerBefore=_runner.p510CompleteHash();
   _eventMan->getEventDispatcher()->registerSource(&events,false);const uint32 end=onBlockingSound(912,1000);_eventMan->getEventDispatcher()->unregisterSource(&events);
   const uint32 wall=_system->getMillis()-wallBefore,held=_pausedMillis-pauseBefore;
   bool valid=events.first&&events.closed&&!_clockPaused&&!shouldQuit()&&!_mixer->isSoundHandleActive(_soundHandle)&&_runner.p510CompleteHash()==runnerBefore&&_place==103;
   if(expected)valid=events.sawPause&&events.saveBlocked&&events.loadBlocked&&events.streamBlocked&&held>=200&&events.atClose>=events.atPause&&events.atClose-events.atPause<60&&end>=1000&&uint32(end-1000)+held<=wall+40&&wall<=uint32(end-1000)+held+40&&valid;
   else valid=!events.sawPause&&!held&&end>=1000&&valid;
   debug("Blocking voice actual pause: %s (expected%d,key%d,pause%d,save%d,load%d,streams%d,held%u,audio%u/%u,wall%u,logical%u)",valid?"PASS":"FAIL",int(expected),int(key),int(events.sawPause),int(events.saveBlocked),int(events.loadBlocked),int(events.streamBlocked),held,events.atPause,events.atClose,wall,end-1000);ok=valid&&ok;++cases;
  }
  debug("Blocking voice menu result: %s (expected%d,cases%u)",ok&&cases==2?"PASS":"FAIL",int(expected),cases);_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def add_probe(cpp):
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }'
 assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+PROBE)
def baseline(cpp,header):return add_probe(cpp),header
def production(cpp,header):
 anchor='private:\n';assert header.count(anchor)==1;header=header.replace(anchor,anchor+' uint _blockingSoundDepth=0; // Derived stack guard,not serialized.\n')
 for signature in ['bool AstronomicaEngine::canSaveGameStateCurrently(Common::U32String *msg) {','bool AstronomicaEngine::canLoadGameStateCurrently(Common::U32String *msg) {']:
  assert cpp.count(signature)==1;cpp=cpp.replace(signature,signature+'\n if(_blockingSoundDepth){if(msg)*msg=Common::U32String("Wait until the voice finishes.");return false;}')
 for signature in ['Common::Error AstronomicaEngine::saveGameStream(Common::WriteStream *stream, bool) {','Common::Error AstronomicaEngine::loadGameStream(Common::SeekableReadStream *stream) {']:
  assert cpp.count(signature)==1;cpp=cpp.replace(signature,signature+'\n if(_blockingSoundDepth)return Common::kReadingFailed;')
 signature='uint32 AstronomicaEngine::onBlockingSound(int id, uint32 now) {';assert cpp.count(signature)==1
 cpp=cpp.replace(signature,signature+'\n struct VoiceStackGuard{uint&depth;explicit VoiceStackGuard(uint&d):depth(d){++depth;}~VoiceStackGuard(){--depth;}} voiceStack(_blockingSoundDepth);')
 start=cpp.index(signature);end=cpp.index('uint32 AstronomicaEngine::onPuzzleSuccess(',start);body=cpp[start:end]
 body=body.replace('const uint32 started = _system->getMillis();','const uint32 started = _system->getMillis(),pausedBefore=_pausedMillis;')
 before='''   while (_system->getEventManager()->pollEvent(event))
    if (event.type == Common::EVENT_QUIT) quitGame();'''
 after='''   while (_system->getEventManager()->pollEvent(event)) {
    if (event.type == Common::EVENT_QUIT) quitGame();
    else if(event.type==Common::EVENT_KEYDOWN&&event.kbd.keycode==Common::KEYCODE_F5)openMainMenuDialog();
    else if(event.type==Common::EVENT_KEYDOWN&&event.kbd.keycode==Common::KEYCODE_SPACE&&!(event.kbd.flags&(Common::KBD_CTRL|Common::KBD_ALT|Common::KBD_META)))pauseForPlayer();
   }'''
 assert body.count(before)==1;body=body.replace(before,after)
 before='_lastBlockingSoundEnd = now + uint32(_system->getMillis() - started);';assert body.count(before)==1
 body=body.replace(before,'_lastBlockingSoundEnd = now + uint32(_system->getMillis()-started)-uint32(_pausedMillis-pausedBefore);')
 return add_probe(cpp[:start]+body+cpp[end:]),header
