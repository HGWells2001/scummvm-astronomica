"""Exercise actual script audio admission/dispatch instead of bypassing the configured runner."""
from startup_defaults_source_nov12b import production as second,baseline as second_baseline
OLD='  const int oldSound=_lastSound;const bool sound=playSound(0,scriptClock());ok=sound==bool(expected&1)&&ok;if(!sound)ok=_lastSound==oldSound&&ok;_mixer->stopHandle(_soundHandle);'
NEW='''  ok=loadPlace(27,false,true)&&ok;const int oldSound=_lastSound;Command note;note.opcode=9;note.args.push_back(1);Script audio;audio.push_back(note);
  const bool admitted=_runner.canRun(audio,true),dispatched=_runner.start(audio,scriptClock(),true);applyScriptActions(scriptClock());const bool sound=_lastSound==0;
  ok=admitted==bool(expected&1)&&dispatched==bool(expected&1)&&sound==bool(expected&1)&&ok;if(!sound)ok=_lastSound==oldSound&&ok;_mixer->stopHandle(_soundHandle);'''
def fix(cpp,header):
 assert cpp.count(OLD)==1;return cpp.replace(OLD,NEW),header
def production(cpp,header):return fix(*second(cpp,header))
def baseline(cpp,header):return fix(*second_baseline(cpp,header))
