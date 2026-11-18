"""Use normal entry settings, which also enable the original ambient selector."""
from door_pause_matrix_source_nov18 import observe as previous
def observe(cpp,header):
    cpp,header=previous(cpp,header)
    old='ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",false);uint passed=0;'
    assert cpp.count(old)==1
    return cpp.replace(old,old.replace('false','true')),header
