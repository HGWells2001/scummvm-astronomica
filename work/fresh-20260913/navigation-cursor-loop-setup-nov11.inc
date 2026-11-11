
 const bool navLoopProbe=ConfMan.hasKey("astronomica_verify_navigation_cursor_loop")&&ConfMan.getBool("astronomica_verify_navigation_cursor_loop");
 uint navProbePhase=0;uint32 navProbeSavedHash=0;uint navProbeSavedCompleted=0;
 Graphics::WinCursorGroup*navProbeOwner=nullptr;
 const bool navProbeOld=navLoopProbe&&ConfMan.hasKey("astronomica_navcursor_old_slot");
 const int navProbeOldSlot=navProbeOld?ConfMan.getInt("astronomica_navcursor_old_slot"):0;
 const int navProbeOldScene=navProbeOld?ConfMan.getInt("astronomica_navcursor_old_scene"):0;
 auto navProbeGlobals=[&](){uint32 hash=2166136261U;for(uint i=0;i<100;++i){int32 value=0;_runner.getValue(0,i,value);hash=(hash^uint32(value))*16777619U;}return hash;};
 auto navProbeMouse=[&](Common::EventType type,int x,int y){Common::Event e;e.type=type;e.mouse=Common::Point(x,y);_eventMan->pushEvent(e);};
 auto navProbeKey=[&](Common::KeyCode key){Common::Event e;e.type=Common::EVENT_KEYDOWN;e.kbd=Common::KeyState(key);_eventMan->pushEvent(e);e.type=Common::EVENT_KEYUP;_eventMan->pushEvent(e);};
 if(navLoopProbe){ConfMan.setBool("astronomica_entry_scripts",false);if(!loadPlace(103,false,true)){debug("Navigation cursor player loop: FAIL (initial room)");quitGame();return Common::kNoError;}navProbeMouse(Common::EVENT_MOUSEMOVE,0,100);}
