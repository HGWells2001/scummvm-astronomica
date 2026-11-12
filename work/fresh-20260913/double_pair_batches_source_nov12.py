"""Optional native observer for ignored double clicks followed by a new click in one poll."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_double_pair_batches")&&ConfMan.getBool("astronomica_verify_double_pair_batches")){
  for(const char*key:{"astronomica_audio","astronomica_animation","astronomica_sprite_input"})ConfMan.setBool(key,true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  class PressBatch:public Common::EventSource{public:Common::Array<Common::Event>events;uint at=0;
   bool allowMapping()const override{return false;}bool pollEvent(Common::Event&e)override{if(at==events.size())return false;e=events[at++];return true;}
   void add(int y){Common::Event e;e.type=Common::EVENT_LBUTTONDOWN;e.mouse=Common::Point(319,y);events.push_back(e);e.type=Common::EVENT_LBUTTONUP;events.push_back(e);}
  };
  uint32 now=0;bool ok=true;uint cases=0;
  auto settle=[&](){for(uint i=0;i<2000&&_place==517&&_runner.pendingCount();++i){runScriptsAt(now);animateSpritesAt(now);now+=20;}return _place==517&&!_runner.pendingCount()&&!_runner.clicksBlocked();};
  auto quiet=[&](){_runner.resetGlobals();_puzzlesCompleted=0;if(!loadPlace(517,false,true))return false;now=scriptClock();if(_runner.enqueueStartup(_scene.scripts,now,true)!=2||!settle())return false;_playerClickPending=false;return true;};
  auto value=[&](int expected){int32 v=0;return _runner.getValue(1,1,v)&&v==expected;};
  auto send=[&](PressBatch&b){_eventMan->getEventDispatcher()->registerSource(&b,false);pollPlayerInput();_eventMan->getEventDispatcher()->unregisterSource(&b);return b.at==b.events.size()&&settle();};
  for(int interval:{10000,0}){
   ConfMan.setInt("double_click_time",interval);bool valid=quiet();PressBatch first;first.add(369);valid=send(first)&&value(5)&&valid;
   // The ignored second press must not consume the one ordinary-click allowance.
   PressBatch mixed;mixed.add(369);mixed.add(420);valid=send(mixed)&&value(4)&&valid;
   PressBatch fourth;fourth.add(420);valid=send(fourth)&&value(4)&&valid;
   PressBatch fifth;fifth.add(420);valid=send(fifth)&&value(3)&&valid;
   debug("Double pair mixed batch: %s (interval%d,ignoredSecond,newThird,ignoredFourth,newFifth)",valid?"PASS":"FAIL",interval);ok=valid&&ok;++cases;
   valid=quiet();PressBatch four;for(int i=0;i<4;++i)four.add(369);valid=send(four)&&value(5)&&valid;
   // Even discarded third/fourth presses update pairing before the next batch.
   PressBatch afterFour;afterFour.add(369);valid=send(afterFour)&&value(6)&&valid;
   debug("Double pair drained batch: %s (interval%d,firstOnly,fifthNew)",valid?"PASS":"FAIL",interval);ok=valid&&ok;++cases;
  }
  debug("Double pair batch result: %s (cases%u)",ok&&cases==4?"PASS":"FAIL",cases);_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def inject(cpp,script):
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }'
 assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+PROBE),script
