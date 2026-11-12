"""Correct only the diagnostic scene count and P27 sound-admission setup."""
from mapped_navigation_source_nov12 import production as original,baseline as original_baseline

def fix(cpp,header):
 assert cpp.count('scenes+=counted;')==1
 cpp=cpp.replace('scenes+=counted;','++scenes;')
 old='ConfMan.setBool("astronomica_sprite_input",true);ConfMan.setBool("astronomica_animation",true);'
 assert cpp.count(old)==1
 return cpp.replace(old,'ConfMan.setBool("astronomica_audio",true);'+old),header

def production(cpp,header):return fix(*original(cpp,header))
def baseline(cpp,header):return fix(*original_baseline(cpp,header))
