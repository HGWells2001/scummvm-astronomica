"""Optional actual-engine preflight inventory;not installed and no scripts executed."""
PROBE=r'''
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
  debug("INPUT INVENTORY COMPLETE scenes%u rejected%u lists%u commands%u unsupported%u",scenes,rejected,lists,commands,unsupported);
  return scenes==420&&rejected==1;
 }
'''
def inject(cpp,script):
 anchor='bool AstronomicaEngine::verifyBuilderPuzzle() {';assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+PROBE),script
