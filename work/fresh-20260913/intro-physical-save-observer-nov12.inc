
 if(ConfMan.hasKey("astronomica_verify_default_save_load")&&ConfMan.getBool("astronomica_verify_default_save_load")) {
  const char*keys[]={"astronomica_audio","astronomica_animation","astronomica_sprite_input","astronomica_entry_scripts"};bool ok=true;
  for(const char*key:keys)ok=!ConfMan.hasKey(key)&&ConfMan.getBool(key)&&ok;
  const int expected=ConfMan.getInt("astronomica_default_save_scene");const int slot=ConfMan.getInt("astronomica_default_save_slot");
  const bool introFinished=loadPlace(501);ok=introFinished&&!_introductionActive&&canLoadGameStateCurrently()&&ok;debug("Fresh physical after original introduction: %s (busy%d,pending%u)",ok?"PASS":"FAIL",int(_introductionActive),_runner.pendingCount());
  const Common::Error loaded=loadGameState(slot);ok=loaded.getCode()==Common::kNoError&&_place==expected&&ok;
  uint32 before=2166136261U;for(int i=0;i<100;++i){int32 value=0;ok=_runner.getValue(0,i,value)&&ok;before=(before^uint32(value))*16777619U;}
  const uint completed=_puzzlesCompleted;bool saved=false,reloaded=false;
  if(ok){saved=saveGameState(60,"Fresh default settings native roundtrip").getCode()==Common::kNoError;ok=saved&&ok;}
  if(ok){ok=loadPlace(103,false,true)&&ok;reloaded=loadGameState(60).getCode()==Common::kNoError;ok=reloaded&&_place==expected&&_puzzlesCompleted==completed&&ok;}
  uint32 after=2166136261U;for(int i=0;i<100;++i){int32 value=0;ok=_runner.getValue(0,i,value)&&ok;after=(after^uint32(value))*16777619U;}
  ok=before==after&&ok;for(const char*key:keys)ok=!ConfMan.hasKey(key)&&ConfMan.getBool(key)&&ok;
  debug("Fresh default physical save: %s (expectedP%d,actualP%d,loaded%d,saved%d,reloaded%d,globals%08x/%08x,completed%u/%u)",ok?"PASS":"FAIL",expected,_place,int(loaded.getCode()==Common::kNoError),int(saved),int(reloaded),before,after,completed,_puzzlesCompleted);
  _background.free();_screen.free();quitGame();return Common::kNoError;
 }
