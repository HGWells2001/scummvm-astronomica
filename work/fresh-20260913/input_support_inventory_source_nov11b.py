"""Classify the sole fresh-session rejection using an isolated runner availability gate."""
from input_support_inventory_source_nov11 import PROBE as INITIAL
EXTRA=r'''
  if(!loadPlace(1,false,true)||_scene.sprites.size()<2)return false;
  const Script&resume=_scene.sprites[1].click;const uint32 before=_runner.p510CompleteHash();
  const bool live=_runner.canRun(resume,true);ScriptRunner available=_runner;available.setLegacyResumeSupport(true);
  const bool admitted=available.canRun(resume,true);ScriptRunner unavailable=available;unavailable.setLegacyResumeSupport(false);
  const bool refused=!unavailable.canRun(resume,true);const bool intact=before==_runner.p510CompleteHash();
  const bool gate=!live&&admitted&&refused&&intact;
  debug("INPUT INVENTORY RESUME GATE %s (live%d,available%d,unavailable_refused%d,live_unchanged%d)",gate?"PASS":"FAIL",int(live),int(admitted),int(refused),int(intact));
  if(!gate)return false;
'''
PROBE=INITIAL.replace('  debug("INPUT INVENTORY COMPLETE',EXTRA+'  debug("INPUT INVENTORY COMPLETE')
def inject(cpp,script):
 anchor='bool AstronomicaEngine::verifyBuilderPuzzle() {';assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+PROBE),script
