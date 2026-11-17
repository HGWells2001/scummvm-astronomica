"""Observe released input separately from P504's deliberately persistent background poll."""
from p504_control_effect_source_nov17 import observe as original_observe,production as original_production
def amend(cpp,header):
 old='starts%u idle%d"';assert cpp.count(old)==1;cpp=cpp.replace(old,'starts%u idle%d blocked%d"')
 old='_soundsStarted-before,int(_runner.scriptsIdle()));';assert cpp.count(old)==1;cpp=cpp.replace(old,'_soundsStarted-before,int(_runner.scriptsIdle()),int(_runner.clicksBlocked()));')
 return cpp,header
def observe(cpp,header):return amend(*original_observe(cpp,header))
def production(cpp,header):return amend(*original_production(cpp,header))
