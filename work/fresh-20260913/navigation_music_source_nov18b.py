"""Treat the engine's absent-track sentinel separately from the original no-loop selector."""
from navigation_music_source_nov18 import observe as previous
def observe(cpp,header):
    cpp,header=previous(cpp,header)
    old='_loopSound==c.destinationLoop&&ownership'
    assert cpp.count(old)==1
    return cpp.replace(old,'(c.destinationLoop?_loopSound==c.destinationLoop:_loopSound==-1)&&ownership'),header
