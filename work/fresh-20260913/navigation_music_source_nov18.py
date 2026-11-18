"""Isolated observation of actual navigation handlers with active original Music."""
from pathlib import Path
import json
def observe(cpp,header):
    w=Path(__file__).resolve().parent;data=json.loads((w/'navigation-music-cases-nov18.json').read_text());assert data['status']=='ORIGINAL_NAVIGATION_MUSIC_CASES_READY'
    names=['route_index','source','direction','requested','permit','destination','permit_after','source_loop','destination_loop','keypad']
    rows=',\n'.join('{'+','.join(str(c[n])for n in names)+'}'for c in data['cases'])
    setup=r'''
 const bool observeNavigationMusic=ConfMan.hasKey("astronomica_observe_navigation_music")&&ConfMan.getBool("astronomica_observe_navigation_music");
 struct ObservedRoute {int route,source,direction,requested,permit,destination,permitAfter,sourceLoop,destinationLoop,keypad;};
 const ObservedRoute observedRoutes[]={ROWS};
 uint observedRouteIndex=0,observedRoutePassed=0;int observedRoutePhase=0;
 uint32 observedRouteAt=_system->getMillis(),observedRouteElapsed=0,observedRouteDeadline=observedRouteAt;
 Audio::SoundHandle observedRouteOwner,observedSourceOwner;
 auto prepareObservedRoute=[&](){const ObservedRoute &c=observedRoutes[observedRouteIndex];_runner.resetGlobals();_puzzlesCompleted=0;observedRoutePhase=0;observedRouteDeadline=_system->getMillis();if(!loadPlace(c.source)){debug("Navigation Music load FAIL");quitGame();}};
 if(observeNavigationMusic)prepareObservedRoute();
'''.replace('ROWS',rows)
    anchor=' while (!shouldQuit()) {\n  pollPlayerInput();\n  runScripts();';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,setup+'\n'+anchor)
    sample=r'''
  if(observeNavigationMusic){
   const ObservedRoute &c=observedRoutes[observedRouteIndex];const uint32 now=_system->getMillis();const bool active=_mixer->isSoundHandleActive(_musicHandle);
   if(now-observedRouteDeadline>15000){debug("Navigation Music timeout FAIL case%u phase%d",observedRouteIndex,observedRoutePhase);quitGame();}
   else if(observedRoutePhase==0||observedRoutePhase==2){
    if(active){observedRouteOwner=_musicHandle;observedRouteElapsed=_mixer->getSoundElapsedTime(_musicHandle);observedRouteAt=now;++observedRoutePhase;}
   }else if(now-observedRouteAt>=200){
    const bool advancing=active&&_musicHandle==observedRouteOwner&&_mixer->getSoundElapsedTime(_musicHandle)>=observedRouteElapsed+50;
    if(observedRoutePhase==1){
     if(!advancing||_place!=c.source||_loopSound!=c.sourceLoop){debug("Navigation Music source FAIL case%u P%d loop%d active%d advancing%d",observedRouteIndex,_place,_loopSound,int(active),int(advancing));quitGame();}
     else{
      observedSourceOwner=_musicHandle;_runner.defineValue(0,57,c.permit);
      const Common::KeyCode arrows[]={Common::KEYCODE_LEFT,Common::KEYCODE_UP,Common::KEYCODE_RIGHT};const Common::KeyCode pads[]={Common::KEYCODE_KP4,Common::KEYCODE_KP8,Common::KEYCODE_KP6};
      handleGameKey(Common::KeyState(c.keypad?pads[c.direction]:arrows[c.direction]));
      observedRouteDeadline=_system->getMillis();observedRoutePhase=c.destinationLoop?2:3;observedRouteAt=0;
     }
    }else{
     int32 permitAfter=-999;_runner.getValue(0,57,permitAfter);
     const bool ownership=c.destinationLoop?(c.sourceLoop==c.destinationLoop?observedSourceOwner==_musicHandle:observedSourceOwner!=_musicHandle):!active;
     const bool correct=_place==c.destination&&permitAfter==c.permitAfter&&_loopSound==c.destinationLoop&&ownership&&(c.destinationLoop?advancing:!active)&&!_clockPaused;
     observedRoutePassed+=correct;
     debug("Navigation Music row: case%u route%d P%d dir%d requested%d permit%d pad%d actual%d after%d loop%d active%d advancing%d owner%d result%s",observedRouteIndex,c.route,c.source,c.direction,c.requested,c.permit,c.keypad,_place,permitAfter,_loopSound,int(active),int(advancing),int(ownership),correct?"PASS":"FAIL");
     if(!correct||++observedRouteIndex==ARRAYSIZE(observedRoutes)){debug("Navigation Music complete: passed%u total%u",observedRoutePassed,uint(ARRAYSIZE(observedRoutes)));quitGame();}
     else prepareObservedRoute();
    }
   }
  }
'''
    anchor='  updateMovie();\n  updateNavigationCursor(mouse.x,mouse.y);';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,'  updateMovie();\n'+sample+'\n  updateNavigationCursor(mouse.x,mouse.y);')
    return cpp,header
