"""Keep the production fix;use the S0file actually shipped in the P27audio check."""
from startup_defaults_source_nov12 import production as first,baseline as first_baseline
def sound_fix(cpp,header):
 assert cpp.count('const bool sound=playSound(1,scriptClock());')==1
 return cpp.replace('const bool sound=playSound(1,scriptClock());','const bool sound=playSound(0,scriptClock());').replace('Startup defaults actual audio: %s (S1played%d)','Startup defaults actual audio: %s (S0played%d)'),header
def production(cpp,header):return sound_fix(*first(cpp,header))
def baseline(cpp,header):return sound_fix(*first_baseline(cpp,header))
