
 if(ConfMan.hasKey("astronomica_verify_input_support_inventory")&&ConfMan.getBool("astronomica_verify_input_support_inventory")) {
  uint scenes=0,rejected=0,lists=0,commands=0,unsupported=0;
  for(int place=0;place<=537;++place){
   const Common::Path path=ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/MEGAFILE.HYP",place)));
   if(!Common::FSNode(path).exists())continue;
   _runner.resetGlobals();if(!loadPlace(place,false,true)){++rejected;debug("INPUT INVENTORY SCENE REJECTED P%d",place);continue;}++scenes;
   auto inspect=[&](const Script&p,const char*owner,uint index){if(p.empty())return;++lists;commands+=p.size();const bool accepted=_runner.canRun(p,true);if(!accepted)++unsupported;debug("INPUT INVENTORY LIST P%d owner%s index%u commands%u accepted%d offset%u",place,owner,index,p.size(),int(accepted),p[0].offset);};
   for(uint i=0;i<_scene.scripts.size();++i)inspect(_scene.scripts[i],"program",i);
   for(uint i=0;i<_scene.sprites.size();++i){const Sprite&s=_scene.sprites[i];inspect(s.click,"sprite-click",i+1);inspect(s.mouseIn,"sprite-in",i+1);inspect(s.mouseOut,"sprite-out",i+1);}
   for(uint i=0;i<_scene.mouseRects.size();++i){const MouseRect&m=_scene.mouseRects[i];inspect(m.click,"rectangle-click",i);inspect(m.mouseIn,"rectangle-in",i);inspect(m.mouseOut,"rectangle-out",i);}
  }

  if(!loadPlace(1,false,true)||_scene.sprites.size()<2)return false;
  const Script&resume=_scene.sprites[1].click;const uint32 before=_runner.p510CompleteHash();
  const bool live=_runner.canRun(resume,true);ScriptRunner available=_runner;available.setLegacyResumeSupport(true);
  const bool admitted=available.canRun(resume,true);ScriptRunner unavailable=available;unavailable.setLegacyResumeSupport(false);
  const bool refused=!unavailable.canRun(resume,true);const bool intact=before==_runner.p510CompleteHash();
  const bool gate=!live&&admitted&&refused&&intact;
  debug("INPUT INVENTORY RESUME GATE %s (live%d,available%d,unavailable_refused%d,live_unchanged%d)",gate?"PASS":"FAIL",int(live),int(admitted),int(refused),int(intact));
  if(!gate)return false;
  debug("INPUT INVENTORY COMPLETE scenes%u rejected%u lists%u commands%u unsupported%u",scenes,rejected,lists,commands,unsupported);
  return scenes==420&&rejected==1;
 }
