"""Admit one gameplay mouse click per polled batch,matching original queue draining."""
PROBE = r'''
 if(ConfMan.hasKey("astronomica_verify_input_backlog")&&ConfMan.getBool("astronomica_verify_input_backlog")){
  const bool expected=ConfMan.getBool("astronomica_input_backlog_expected");
  for(const char*key:{"astronomica_audio","astronomica_animation","astronomica_sprite_input"})ConfMan.setBool(key,true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  class BatchEvents:public Common::EventSource {
  public:Common::Array<Common::Event>events;uint at=0;bool&paused;bool sawPause=false;
   explicit BatchEvents(bool&p):paused(p){}
   bool allowMapping()const override{return false;}
   bool pollEvent(Common::Event&e)override{if(paused)sawPause=true;if(at>=events.size())return false;e=events[at++];return true;}
   void click(int x,int y){Common::Event e;e.type=Common::EVENT_LBUTTONDOWN;e.mouse=Common::Point(x,y);events.push_back(e);}
   void key(Common::KeyCode key){Common::Event e;e.type=Common::EVENT_KEYDOWN;e.kbd=Common::KeyState(key);events.push_back(e);}
  };
  uint32 now=0;bool ok=true;uint cases=0,differences=0;
  auto settle=[&](){for(uint tick=0;tick<20000&&_place==536&&_runner.pendingCount();++tick){runScriptsAt(now);animateSpritesAt(now);now+=50;}return _place!=536||(!_runner.pendingCount()&&!_runner.clicksBlocked());};
  auto quiet=[&](bool warm){_runner.resetGlobals();_runner.seedRandom(1);_puzzlesCompleted=0;if(!loadPlace(536,false,true))return false;now=scriptClock();if(_runner.enqueueStartup(_scene.scripts,now,true)!=7)return false;return !warm||settle();};
  auto point=[&](uint id,Common::Point&out){if(id<1||id>_scene.sprites.size())return false;const Sprite&s=_scene.sprites[id-1];Common::File file;if(!file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P536/MEGAFILE.HYP"))))return false;const Frame*f=staticSpriteFrame(_scene,id-1);Graphics::Surface*bmp=f?decodeSpriteBitmap(file,f->image,_screen.format):nullptr;if(!bmp)return false;const int right=int16(s.renderX+bmp->w),bottom=int16(s.renderY+bmp->h);bmp->free();delete bmp;for(int y=MAX(0,int(s.renderY));y<=MIN(479,bottom);++y)for(int x=MAX(0,int(s.renderX));x<=MIN(639,right);++x)if(spriteAt(x,y)==int(id)-1){out=Common::Point(x,y);return true;}return false;};
  auto scalars=[&](){Common::Array<int32>values;values.push_back(_place);values.push_back(_puzzlesCompleted);values.push_back(_runner.clicksBlocked());values.push_back(_runner.pendingCount());for(int scope=0;scope<2;++scope)for(int id=0;id<(scope?13:100);++id){int32 v=0;const bool defined=_runner.getValue(scope,id,v);values.push_back(defined);values.push_back(v);}return values;};
  const uint paths[][3]={{8,5,6},{5,8,6},{8,6,5},{8,5,8},{5,6,8},{5,5,8}};
  for(bool warm:{false,true})for(uint path=0;path<ARRAYSIZE(paths);++path){
   if(!quiet(warm)){ok=false;break;}Common::Point first;if(!point(paths[path][0],first)){ok=false;break;}clickAtTime(first.x,first.y,scriptClock());if(!settle()){ok=false;break;}const Common::Array<int32>reference=scalars();
   if(!quiet(warm)){ok=false;break;}BatchEvents batch(_clockPaused);for(uint id:paths[path]){Common::Point p;if(!point(id,p)){ok=false;break;}batch.click(p.x,p.y);}
   _eventMan->getEventDispatcher()->registerSource(&batch,false);pollPlayerInput();_eventMan->getEventDispatcher()->unregisterSource(&batch);
   const bool settled=settle(),same=scalars()==reference;differences+=!same;ok=batch.at==3&&settled&&(!expected||same)&&ok;
   debug("Click backlog original burst: %s (expected%d,warm%d,path%u,consumed%u,sameFirst%d,place%d)",ok?"PASS":"FAIL",int(expected),int(warm),path,batch.at,int(same),_place);++cases;
  }
  ok=cases==12&&(expected?differences==0:differences>0)&&ok;
  // Host keyboard/menu/quit events remain available after a mouse event.
  if(!loadPlace(103,false,true))ok=false;BatchEvents keys(_clockPaused);keys.click(-30,-30);keys.key(Common::KEYCODE_RIGHT);_eventMan->getEventDispatcher()->registerSource(&keys,false);pollPlayerInput();_eventMan->getEventDispatcher()->unregisterSource(&keys);const bool keyboard=_place==98&&keys.at==2;ok=keyboard&&ok;
  BatchEvents menu(_clockPaused);menu.click(-30,-30);menu.key(Common::KEYCODE_F5);menu.key(Common::KEYCODE_ESCAPE);_eventMan->getEventDispatcher()->registerSource(&menu,false);pollPlayerInput();_eventMan->getEventDispatcher()->unregisterSource(&menu);const bool menuOK=menu.sawPause&&!_clockPaused&&!shouldQuit();ok=menuOK&&ok;
  BatchEvents exit(_clockPaused);exit.click(-30,-30);Common::Event quit;quit.type=Common::EVENT_QUIT;exit.events.push_back(quit);_eventMan->getEventDispatcher()->registerSource(&exit,false);pollPlayerInput();_eventMan->getEventDispatcher()->unregisterSource(&exit);const bool quitOK=shouldQuit();ok=quitOK&&ok;
  debug("Click backlog host controls: %s (keyboard%d,menu%d,quit%d)",keyboard&&menuOK&&quitOK?"PASS":"FAIL",int(keyboard),int(menuOK),int(quitOK));
  debug("Click backlog native result: %s (expected%d,cases%u,differences%u)",ok?"PASS":"FAIL",int(expected),cases,differences);_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''


def baseline(cpp, header):
    anchor = ' while (!shouldQuit()) {\n  Common::Event event;\n  while (_eventMan->pollEvent(event)) {'
    assert cpp.count(anchor) == 1
    start = cpp.index(anchor)
    body_start = start + len(' while (!shouldQuit()) {\n')
    body_end = cpp.index('\n  runScripts();', body_start)
    body = cpp[body_start:body_end]
    cpp = cpp[:body_start] + '  pollPlayerInput();' + cpp[body_end:]
    method = 'void AstronomicaEngine::pollPlayerInput() {\n' + body + '\n}\n\n'
    signature = 'void AstronomicaEngine::handleGameKey(const Common::KeyState &key) {'
    assert cpp.count(signature) == 1
    cpp = cpp.replace(signature, method + signature)
    assert header.count('private:\n') == 1
    header = header.replace('private:\n', 'private:\n void pollPlayerInput();\n')
    initial = ' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }'
    assert cpp.count(initial) == 1
    return cpp.replace(initial, initial + '\n' + PROBE), header


def production(cpp, header):
    cpp, header = baseline(cpp, header)
    signature = 'void AstronomicaEngine::pollPlayerInput() {\n'
    cpp = cpp.replace(signature, signature + '  bool mouseClickConsumed=false;\n')
    original = 'if (event.type == Common::EVENT_LBUTTONDOWN) { clickAt(event.mouse.x, event.mouse.y); continue; }'
    assert cpp.count(original) == 1
    replacement = 'if (event.type == Common::EVENT_LBUTTONDOWN) { if(!mouseClickConsumed){mouseClickConsumed=true;clickAt(event.mouse.x,event.mouse.y);} continue; }'
    return cpp.replace(original, replacement), header
