"""Adapt original CS_DBLCLKS input pairing to ScummVM's mouse-down events."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_double_click")&&ConfMan.getBool("astronomica_verify_double_click")){
  const bool expected=ConfMan.getBool("astronomica_double_click_expected");
  for(const char*key:{"astronomica_audio","astronomica_animation","astronomica_sprite_input"})ConfMan.setBool(key,true);
  ConfMan.setBool("astronomica_entry_scripts",false);ConfMan.setInt("double_click_time",10000);
  class MousePress:public Common::EventSource{public:Common::Array<Common::Event>events;uint at=0;
   bool allowMapping()const override{return false;}bool pollEvent(Common::Event&e)override{if(at==events.size())return false;e=events[at++];return true;}
   explicit MousePress(Common::Point p){Common::Event e;e.type=Common::EVENT_LBUTTONDOWN;e.mouse=p;events.push_back(e);e.type=Common::EVENT_LBUTTONUP;events.push_back(e);}
  };
  uint32 now=0;bool ok=true;uint cases=0,differences=0,tripleMatches=0;
  auto settle=[&](){for(uint pass=0;pass<2000&&_place==517&&_runner.pendingCount();++pass){runScriptsAt(now);animateSpritesAt(now);now+=20;}return _place==517&&!_runner.pendingCount()&&!_runner.clicksBlocked();};
  auto quiet=[&](){_runner.resetGlobals();_puzzlesCompleted=0;if(!loadPlace(517,false,true))return false;now=scriptClock();if(_runner.enqueueStartup(_scene.scripts,now,true)!=2||!settle())return false;_playerClickPending=false;return true;};
  auto scalars=[&](){Common::Array<int32>values;values.push_back(_place);values.push_back(_puzzlesCompleted);values.push_back(_runner.pendingCount());values.push_back(_runner.clicksBlocked());for(int scope=0;scope<2;++scope)for(int id=0;id<(scope?2:100);++id){int32 v=0;values.push_back(_runner.getValue(scope,id,v));values.push_back(v);}if(_scene.sprites.size()>7){values.push_back(_scene.sprites[6].renderX);values.push_back(_scene.sprites[7].renderX);values.push_back(_scene.sprites[7].renderY);}return values;};
  auto press=[&](Common::Point p){MousePress source(p);_eventMan->getEventDispatcher()->registerSource(&source,false);pollPlayerInput();_eventMan->getEventDispatcher()->unregisterSource(&source);return source.at==2&&settle();};
  for(int y:{420,369})for(int shift:{0,1,2}){
   if(!quiet()){ok=false;break;}clickAtTime(319,y,scriptClock());if(!settle()){ok=false;break;}const Common::Array<int32>first=scalars();clickAtTime(319+shift,y,scriptClock());if(!settle()){ok=false;break;}const Common::Array<int32>two=scalars();
   if(first==two||!quiet()||spriteAt(319,y)<0){ok=false;break;}
   if(!press(Common::Point(319,y))){ok=false;break;}_system->delayMillis(10);if(!press(Common::Point(319+shift,y))){ok=false;break;}
   const bool same=scalars()==first;differences+=!same;ok=(!expected||same)&&ok;
   _system->delayMillis(10);if(!press(Common::Point(319+shift,y))){ok=false;break;}const bool third=scalars()==two;tripleMatches+=third;ok=(!expected||third)&&ok;
   debug("Double click original P517 controls: %s (expected%d,y%d,shift%d,sameFirst%d,thirdIsNew%d)",ok?"PASS":"FAIL",int(expected),y,shift,int(same),int(third));++cases;
  }
  // A delayed second press remains a new original control action.
  bool delayed=quiet();ConfMan.setInt("double_click_time",50);delayed=press(Common::Point(319,369))&&delayed;_system->delayMillis(90);delayed=press(Common::Point(319,369))&&delayed;int32 value=0;delayed=_runner.getValue(1,1,value)&&value==6&&delayed;
  // A nearby but distinct press outside the portable 3-pixel tolerance is new.
  ConfMan.setInt("double_click_time",10000);bool separate=quiet()&&press(Common::Point(319,369))&&press(Common::Point(322,369));separate=_runner.getValue(1,1,value)&&value==6&&separate;
  ok=cases==6&&(expected?differences==0&&tripleMatches==6:differences==6)&&delayed&&separate&&ok;
  debug("Double click native result: %s (expected%d,cases%u,differences%u,tripleMatches%u,delayed%d,separate%d)",ok?"PASS":"FAIL",int(expected),cases,differences,tripleMatches,int(delayed),int(separate));_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''

def common(cpp,header,enabled):
    private='private:\n'
    assert header.count(private)==1
    header=header.replace(private,private+' bool playerClickIsDouble(const Common::Point &position,uint32 now);\n Common::Point _playerClickPosition;\n uint32 _playerClickTime=0;\n bool _playerClickPending=false;\n')
    signature='void AstronomicaEngine::pollPlayerInput() {\n'
    assert cpp.count(signature)==1
    method='''bool AstronomicaEngine::playerClickIsDouble(const Common::Point &position,uint32 now) {
 const uint32 configured=_system->getDoubleClickTime();
 const uint32 interval=configured?configured:500;
 const bool paired=PAIR_TEST;
 if(paired){_playerClickPending=false;return true;}
 _playerClickPosition=position;_playerClickTime=now;_playerClickPending=true;return false;
}

'''.replace('PAIR_TEST','_playerClickPending&&uint32(now-_playerClickTime)<interval&&ABS(int(position.x)-int(_playerClickPosition.x))<3&&ABS(int(position.y)-int(_playerClickPosition.y))<3' if enabled else 'false')
    cpp=cpp.replace(signature,method+signature)
    before='if (event.type == Common::EVENT_LBUTTONDOWN) { if(!mouseClickConsumed){mouseClickConsumed=true;clickAt(event.mouse.x,event.mouse.y);} continue; }'
    after='if (event.type == Common::EVENT_LBUTTONDOWN) { const bool doubleClick=playerClickIsDouble(event.mouse,_system->getMillis());if(!doubleClick&&!mouseClickConsumed){mouseClickConsumed=true;clickAt(event.mouse.x,event.mouse.y);} continue; }'
    assert cpp.count(before)==1;cpp=cpp.replace(before,after)
    # Independent repetitions of the already accepted optional backlog fixture.
    fixture='auto quiet=[&](bool warm){_runner.resetGlobals();'
    assert cpp.count(fixture)==1;cpp=cpp.replace(fixture,'auto quiet=[&](bool warm){_playerClickPending=false;_runner.resetGlobals();')
    anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }'
    assert cpp.count(anchor)==1
    return cpp.replace(anchor,anchor+'\n'+PROBE),header

def production(cpp,header):return common(cpp,header,True)
def baseline(cpp,header):return common(cpp,header,False)
