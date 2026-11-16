"""Keep rejected save/load requests read-only while normalizing music on normal ticks/pause."""
from effect_mix_source_nov16c import production as previous

def production(cpp,header):
 cpp,header=previous(cpp,header)
 old=' synchronizeMusicHandle();\n if(_mixer->isSoundHandleActive(_effectHandle))'
 assert cpp.count(old)==4
 guard=' if(_mixer->isSoundHandleActive(_effectHandle)||(_mixer->isSoundHandleActive(_musicHandle)&&!_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle)))'
 cpp=cpp.replace(old,guard)
 anchor='void AstronomicaEngine::pauseEngineIntern(bool pause) {\n Engine::pauseEngineIntern(pause);'
 assert cpp.count(anchor)==1
 cpp=cpp.replace(anchor,'void AstronomicaEngine::pauseEngineIntern(bool pause) {\n if(pause)synchronizeMusicHandle();\n Engine::pauseEngineIntern(pause);')
 anchor='  ok=playSound(2,scriptClock())&&ok;const bool effectStarted='
 extra=r'''
  ok=playSound(2,scriptClock())&&ok;
  while(_mixer->isSoundHandleActive(_effectHandle)&&!shouldQuit())_system->delayMillis(5);
  const Audio::SoundHandle primaryBefore=_soundHandle;const int lastBefore=_lastSound;
  byte invalid[8]={};Common::MemoryReadStream bad(invalid,sizeof(invalid));
  const bool rejected=loadGameStream(&bad).getCode()!=Common::kNoError&&bad.pos()==0&&_soundHandle==primaryBefore&&_lastSound==lastBefore;
  debug("Effect mix rejected load: %s",rejected?"PASS":"FAIL");ok=rejected&&ok;resumeLoopAt(scriptClock());
  const uint32 clockBefore=_mixer->getSoundElapsedTime(_musicHandle);uint32 clockHeld=0;
  {PauseToken hold=pauseEngine();_system->delayMillis(150);clockHeld=_mixer->getSoundElapsedTime(_musicHandle);}
  const bool paused=clockHeld>=clockBefore&&clockHeld-clockBefore<60;
  debug("Effect mix pause: %s",paused?"PASS":"FAIL");ok=paused&&ok;
'''
 assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,extra+'\n'+anchor)
 return cpp,header
