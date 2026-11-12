"""Preserve intro-menu production delta;avoid the stock forbidden-system macro in observer."""
from intro_menu_source_nov12 import production as initial,baseline as initial_baseline,PROBE
FIXED_PROBE=PROBE.replace('OSystem*system;','OSystem*hostSystem;').replace(':system(s),',':hostSystem(s),').replace('now=system->getMillis()','now=hostSystem->getMillis()').replace('&&!_mixer->isSoundHandleActive(_soundHandle);','&&!_mixer->isSoundHandleActive(_soundHandle)&&canLoadGameStateCurrently();')
def fix(cpp,header):
 assert cpp.count(PROBE)==1;return cpp.replace(PROBE,FIXED_PROBE),header
def production(cpp,header):return fix(*initial(cpp,header))
def baseline(cpp,header):return fix(*initial_baseline(cpp,header))
