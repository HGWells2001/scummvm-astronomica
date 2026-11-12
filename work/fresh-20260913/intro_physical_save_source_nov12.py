"""Verify old native files after a full original introduction has released its transient busy guard."""
from defaults_physical_saves_source_nov12 import PROBE as INITIAL
PROBE=INITIAL.replace('  const Common::Error loaded=loadGameState(slot);','  const bool introFinished=loadPlace(501);ok=introFinished&&!_introductionActive&&canLoadGameStateCurrently()&&ok;debug("Fresh physical after original introduction: %s (busy%d,pending%u)",ok?"PASS":"FAIL",int(_introductionActive),_runner.pendingCount());\n  const Common::Error loaded=loadGameState(slot);')
def inject(cpp,script):
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }';assert cpp.count(anchor)==1
 return cpp.replace(anchor,anchor+'\n'+PROBE),script
