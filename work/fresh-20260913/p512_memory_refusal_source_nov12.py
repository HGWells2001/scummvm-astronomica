"""Diagnostic only: locate a naturally observed P512 verifier refusal without weakening any check."""
def inject(cpp,script):
 start=cpp.index('bool AstronomicaEngine::testP512MemoryInstall(uint32 now){');end=cpp.index('\nbool AstronomicaEngine::testP512PauseMatrix',start)
 body=cpp[start:end];count=body.count('return false;');assert count>15
 body=body.replace('return false;','{debug("P512 memory refusal detail line%d",__LINE__);return false;}')
 return cpp[:start]+body+cpp[end:],script
