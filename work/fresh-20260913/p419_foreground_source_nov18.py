"""Observe the original repeated S1 dispatch without assigning an unverified speech/effect role."""
def observe(cpp,header):
    anchor='namespace Astronomica {';assert cpp.count(anchor)==1
    cpp=cpp.replace(anchor,anchor+'\nstatic uint observedP419LocalStarts=0;')
    anchor='bool AstronomicaEngine::playSound(int id, uint32 now, bool looping) {';assert cpp.count(anchor)==1
    cpp=cpp.replace(anchor,anchor+'\n if(_place==419&&id==1&&!looping&&ConfMan.hasKey("astronomica_observe_p419_foreground")&&ConfMan.getBool("astronomica_observe_p419_foreground"))++observedP419LocalStarts;')
    setup=r'''
 const bool observeP419Foreground=ConfMan.hasKey("astronomica_observe_p419_foreground")&&ConfMan.getBool("astronomica_observe_p419_foreground");
 int p419phase=0;uint p419passed=0;bool p419sample=false;uint32 p419at=0,p419elapsed=0,p419deadline=_system->getMillis();Audio::SoundHandle p419owner;
 auto prepareP419Foreground=[&](int state){_runner.resetGlobals();_runner.defineValue(0,52,state);observedP419LocalStarts=0;p419sample=false;p419deadline=_system->getMillis();if(!loadPlace(419)){debug("P419 foreground load FAIL");quitGame();}};
 if(observeP419Foreground)prepareP419Foreground(0);
'''
    anchor=' while (!shouldQuit()) {\n  pollPlayerInput();\n  runScripts();';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,setup+'\n'+anchor)
    sample=r'''
  if(observeP419Foreground){
   const uint32 now=_system->getMillis();const bool music=_mixer->isSoundHandleActive(_musicHandle),foreground=_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle);
   if(now-p419deadline>5000){debug("P419 foreground timeout FAIL phase%d",p419phase);quitGame();}
   else if(p419phase==1){
    if(now-p419deadline>=1000){
     int32 local=-1;_runner.getValue(1,0,local);const bool correct=_place==419&&local==1&&observedP419LocalStarts>=2&&foreground&&!music;
     p419passed+=correct;debug("P419 foreground repeated: local%d starts%u foreground%d music%d result%s",local,observedP419LocalStarts,int(foreground),int(music),correct?"PASS":"FAIL");
     if(!correct)quitGame();else{handleGameKey(Common::KeyState(Common::KEYCODE_LEFT));p419phase=2;p419sample=false;p419deadline=now;}
    }
   }else if(music&&!foreground){
    if(!p419sample){p419sample=true;p419owner=_musicHandle;p419at=now;p419elapsed=_mixer->getSoundElapsedTime(_musicHandle);}
    else if(now-p419at>=300){
     int32 local=-1;_runner.getValue(1,0,local);const bool advancing=p419owner==_musicHandle&&_mixer->getSoundElapsedTime(_musicHandle)>=p419elapsed+50;
     const bool correct=advancing&&_loopSound==902&&!_clockPaused&&(p419phase==0?(_place==419&&local==0&&observedP419LocalStarts==0):_place==358);
     p419passed+=correct;debug("P419 foreground boundary: phase%d place%d local%d starts%u advancing%d loop%d result%s",p419phase,_place,local,observedP419LocalStarts,int(advancing),_loopSound,correct?"PASS":"FAIL");
     if(!correct||p419phase==2){debug("P419 foreground complete: passed%u total3",p419passed);quitGame();}else{p419phase=1;prepareP419Foreground(1);}
    }
   }
  }
'''
    anchor='  updateMovie();\n  updateNavigationCursor(mouse.x,mouse.y);';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,'  updateMovie();\n'+sample+'\n  updateNavigationCursor(mouse.x,mouse.y);')
    return cpp,header
