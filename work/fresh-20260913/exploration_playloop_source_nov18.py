"""Observe all original mode1 rooms through the real frame loop; canonical behavior is unchanged."""
from pathlib import Path
import json
def observe(cpp,header):
 w=Path(__file__).resolve().parent;inventory=json.loads((w/'scene-audio-mode-inventory-nov17.json').read_text());rooms=[r for r in inventory['rows']if r['mode']==1];assert len(rooms)==306
 places=','.join(str(r['place'])for r in rooms);loops=','.join(str(r['normal_loop'])for r in rooms)
 setup=r'''
 const bool observeExplorationFrames=ConfMan.hasKey("astronomica_observe_exploration_frames")&&ConfMan.getBool("astronomica_observe_exploration_frames");
 const int observedWorldPlaces[]={PLACES};const int observedWorldLoops[]={LOOPS};
 uint observedWorldIndex=0,observedWorldPassed=0;bool observedWorldSample=false;uint32 observedWorldAt=0,observedWorldElapsed=0;
 Audio::SoundHandle observedWorldOwner;
 if(observeExplorationFrames){_runner.resetGlobals();if(!loadPlace(observedWorldPlaces[0])){debug("Exploration frame sweep: initial load failed");quitGame();}}
'''.replace('PLACES',places).replace('LOOPS',loops)
 anchor=' while (!shouldQuit()) {\n  pollPlayerInput();\n  runScripts();';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,setup+'\n'+anchor)
 sample=r'''
  if(observeExplorationFrames){
   const bool active=_mixer->isSoundHandleActive(_musicHandle);
   if(active&&!observedWorldSample){observedWorldSample=true;observedWorldAt=_system->getMillis();observedWorldElapsed=_mixer->getSoundElapsedTime(_musicHandle);observedWorldOwner=_musicHandle;}
   if(observedWorldSample&&_system->getMillis()-observedWorldAt>=250){
    const bool advancing=active&&_musicHandle==observedWorldOwner&&_mixer->getSoundElapsedTime(_musicHandle)>=observedWorldElapsed+50;
    const bool correct=_place==observedWorldPlaces[observedWorldIndex]&&_loopSound==observedWorldLoops[observedWorldIndex]&&active&&advancing&&!_clockPaused;
    observedWorldPassed+=correct;
    debug("Exploration frame room: P%d expected%d actual%d active%d advancing%d paused%d volume%d muted%d",_place,observedWorldLoops[observedWorldIndex],_loopSound,int(active),int(advancing),int(_clockPaused),_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType),int(_mixer->isSoundTypeMuted(Audio::Mixer::kMusicSoundType)));
    if(!correct||++observedWorldIndex==ARRAYSIZE(observedWorldPlaces)){debug("Exploration frame sweep complete: passed%u total%u",observedWorldPassed,uint(ARRAYSIZE(observedWorldPlaces)));quitGame();}
    else{observedWorldSample=false;_runner.defineValue(0,60,0);if(!loadPlace(observedWorldPlaces[observedWorldIndex])){debug("Exploration frame sweep: next load failed");quitGame();}}
   }
  }
'''
 anchor='  updateMovie();\n  updateNavigationCursor(mouse.x,mouse.y);';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,'  updateMovie();\n'+sample+'\n  updateNavigationCursor(mouse.x,mouse.y);')
 return cpp,header
