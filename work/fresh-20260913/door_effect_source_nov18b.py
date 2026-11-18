"""Let the real queued second-click program settle before checking traversal."""
from door_effect_source_nov18 import observe as previous_observe,production as previous_production
def settle(cpp,header):
    old='clickAtTime(x,y,scriptClock());runScripts();const bool destination=_place==32;'
    assert cpp.count(old)==1
    return cpp.replace(old,'clickAtTime(x,y,scriptClock());const uint32 traversedAt=_system->getMillis();while(_system->getMillis()-traversedAt<120){runScripts();resumeLoopAt(scriptClock());_system->delayMillis(2);}const bool destination=_place==32;'),header
def observe(cpp,header):return settle(*previous_observe(cpp,header))
def production(cpp,header):return settle(*previous_production(cpp,header))
