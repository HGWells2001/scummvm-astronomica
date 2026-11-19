"""General exact-identity effect catalogue; no runtime acoustic heuristic or new save fields."""
from pathlib import Path
import json
w=Path(__file__).resolve().parent

def production(cpp,header):
    j=json.loads((w/'audio-role-catalogue-nov19.json').read_text())
    entries=sorted({(x['bytes'],x['fnv1a'])for x in j['clips']if x['role']=='effect'})
    table='\n'.join('  {%dU,0x%08xU},'%row for row in entries)
    start=cpp.index('bool AstronomicaEngine::isFeedbackEffect(int id) const {');end=cpp.index('void AstronomicaEngine::synchronizeMusicHandle()',start)
    body='''bool AstronomicaEngine::isFeedbackEffect(int id) const {
 // Original-file catalogue covers effects throughout exploration and puzzles.
 // Speech and music retain foreground/loop routing; unknown files stay conservative.
 // Introductions can also be nonverbal effects: the file identity decides the role.
 if(id<0||id>922||isBlockingSound(id))return false;
 static const struct { uint32 size; uint32 hash; } effects[] = {
'''+table+'''
 };
 const Common::Path path=ConfMan.getPath("path").join(Common::Path(id>=900?Common::String::format("SOUNDS/S%d.WAV",id-900):Common::String::format("PLACES/P%d/S%d.WAV",_place,id)));
 Common::File file;if(!file.open(Common::FSNode(path)))return false;
 bool candidate=false;for(uint i=0;i<ARRAYSIZE(effects);++i)candidate|=file.size()==effects[i].size;
 if(!candidate)return false;
 uint32 hash=2166136261U;byte bytes[4096];
 while(file.pos()<file.size()){
  const uint count=file.read(bytes,sizeof(bytes));if(!count)return false;
  for(uint i=0;i<count;++i)hash=(hash^bytes[i])*16777619U;
 }
 if(file.err())return false;
 for(uint i=0;i<ARRAYSIZE(effects);++i)if(file.size()==effects[i].size&&hash==effects[i].hash)return true;
 return false;
}
'''
    return cpp[:start]+body+cpp[end:],header

def observe(cpp,header):
    cpp,header=production(cpp,header)
    anchor=' if(ConfMan.hasKey("astronomica_verify_door_music")'
    assert cpp.count(anchor)==1
    block=''' if(ConfMan.hasKey("astronomica_verify_audio_roles")&&ConfMan.getBool("astronomica_verify_audio_roles")){
  ConfMan.setBool("astronomica_entry_scripts",false);ConfMan.setBool("astronomica_audio",true);
  Common::File fixture;if(!fixture.open(Common::FSNode(ConfMan.getPath("astronomica_audio_role_fixture"))))error("Audio catalogue fixture missing");
  const uint32 count=fixture.readUint32LE();if(count!=632)error("Audio catalogue fixture count");
  uint passed=0,effects=0,foreground=0;
  for(uint i=0;i<count;++i){
   const int place=fixture.readSint32LE(),id=fixture.readSint32LE();const bool effect=fixture.readSint32LE()!=0;
   _runner.resetGlobals();const bool loaded=loadPlace(place,false,true);const bool role=isFeedbackEffect(id)==effect;
   _loopSound=900;_loopEnabled=true;const bool ambient=playSound(900,scriptClock(),true);const Audio::SoundHandle owner=_musicHandle;
   _system->delayMillis(25);const uint32 elapsed=_mixer->getSoundElapsedTime(owner);const uint starts=_soundsStarted;
   const bool played=playSound(id,scriptClock());
   const bool overlap=_musicHandle==owner&&_mixer->isSoundHandleActive(owner)&&_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==owner);
   const bool exclusive=!_mixer->isSoundHandleActive(owner)&&_mixer->isSoundHandleActive(_soundHandle);
   _system->delayMillis(20);resumeLoopAt(scriptClock());
   const bool continuity=!effect||(_musicHandle==owner&&_mixer->isSoundHandleActive(owner)&&_mixer->getSoundElapsedTime(owner)>=elapsed);
   const bool correct=loaded&&role&&ambient&&played&&(effect?overlap:exclusive)&&continuity&&_soundsStarted==starts+1;
   if(correct)++passed;if(effect)++effects;else ++foreground;
   debug("Audio catalogue row: %u P%d S%d effect%d role%d overlap%d exclusive%d continuous%d result%d",i,place,id,int(effect),int(role),int(overlap),int(exclusive),int(continuity),int(correct));
  }
  debug("Audio catalogue complete: %s (passed%u,total%u,effects%u,foreground%u)",passed==count?"PASS":"FAIL",passed,count,effects,foreground);
  _background.free();_screen.free();quitGame();return Common::kNoError;
 }

'''
    return cpp.replace(anchor,block+anchor),header
