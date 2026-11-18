"""Bound no-stream observations inside the native verifier, without terminating processes."""
from exploration_playloop_source_nov18 import observe as previous
def observe(cpp,header):
 cpp,header=previous(cpp,header)
 old='Audio::SoundHandle observedWorldOwner;';assert cpp.count(old)==1;cpp=cpp.replace(old,old+'uint32 observedWorldCaseAt=_system->getMillis();')
 old='  if(observeExplorationFrames){\n   const bool active=';assert cpp.count(old)==1
 cpp=cpp.replace(old,'  if(observeExplorationFrames){\n   if(!observedWorldSample&&_system->getMillis()-observedWorldCaseAt>15000){debug("Exploration frame sweep: no stream P%d",_place);quitGame();}\n   const bool active=')
 old='else{observedWorldSample=false;_runner.defineValue(0,60,0);';assert cpp.count(old)==1
 cpp=cpp.replace(old,'else{observedWorldSample=false;observedWorldCaseAt=_system->getMillis();_runner.defineValue(0,60,0);')
 return cpp,header
