"""Preserve production indicator;verify portal scripts across their original deferred ticks."""
from contextual_cursor_source_nov11 import production as initial,PORTAL_TEST
def production(cpp,header):
 cpp,header=initial(cpp,header)
 fixed=PORTAL_TEST.replace('clickAtTime(300,300,scriptClock());runScriptsAt(scriptClock());if(_place!=portalTargets[scene])return false;','clickAtTime(300,300,scriptClock());const uint32 at=scriptClock();for(uint tick=0;tick<16&&_place==portalScenes[scene];++tick)runScriptsAt(at+tick);if(_place!=portalTargets[scene]){debug("Contextual portal test: FAIL (source%d,target%d,actual%d,pending%u,blocked%d)",portalScenes[scene],portalTargets[scene],_place,_runner.pendingCount(),_runner.clicksBlocked());return false;}')
 assert cpp.count(PORTAL_TEST)==1;return cpp.replace(PORTAL_TEST,fixed),header
