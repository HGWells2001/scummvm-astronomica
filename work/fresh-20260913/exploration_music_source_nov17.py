"""Restore original mode1 regional ambience while retaining the loop through same-zone navigation."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_exploration_music")&&ConfMan.getBool("astronomica_verify_exploration_music")){
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",true);_runner.resetGlobals();
  int observed=0,total=0;bool stable=true;
  for(int flag:{0,1})for(int place:{103,101,219,220,361,362,410,420}){
   _runner.defineValue(0,60,flag);const int expected=flag?908:((place>=219&&place<=251)||place==410?901:((place>=361&&place<=389)||place==420?903:902));
   const int prior=_loopSound;const Audio::SoundHandle old=_musicHandle;const uint starts=_soundsStarted;
   bool loaded=loadPlace(place);resumeLoopAt(scriptClock());_system->delayMillis(35);
   const bool active=loaded&&_loopSound==expected&&_mixer->isSoundHandleActive(_musicHandle)&&_soundHandle==_musicHandle;
   const bool continuous=prior!=expected||!_mixer->isSoundHandleActive(old)||_musicHandle==old;
   const bool countOK=!active||_soundsStarted==starts+uint(prior!=expected||old!=_musicHandle);
   debug("Exploration music entry: flag%d P%d expected%d actual%d active%d continuity%d starts%d",flag,place,expected,_loopSound,int(active),int(continuous),int(countOK));
   observed+=active;stable=stable&&continuous&&countOK;++total;
  }
  _runner.defineValue(0,60,0);bool loaded=loadPlace(103);resumeLoopAt(scriptClock());
  Common::MemoryWriteStreamDynamic saved(DisposeAfterUse::YES);const bool wrote=loaded&&saveGameStream(&saved,false).getCode()==Common::kNoError;
  _runner.defineValue(0,60,1);loaded=loadPlace(117)&&loaded;resumeLoopAt(scriptClock());
  Common::MemoryReadStream input(saved.getData(),saved.size());const bool restored=wrote&&loadGameStream(&input).getCode()==Common::kNoError;resumeLoopAt(scriptClock());
  const bool restoredMusic=restored&&_place==103&&_loopSound==902&&_mixer->isSoundHandleActive(_musicHandle);
  debug("Exploration music ASVM2 restore: wrote%d restored%d music%d",int(wrote),int(restored),int(restoredMusic));
  const Audio::SoundHandle music=_musicHandle;const bool started=playSound(911,scriptClock());const bool exclusive=started&&!_mixer->isSoundHandleActive(music);
  while(_mixer->isSoundHandleActive(_soundHandle)&&!shouldQuit()){pollPlayerInput();_system->delayMillis(10);}
  resumeLoopAt(scriptClock());const bool resumed=_loopSound==902&&_mixer->isSoundHandleActive(_musicHandle);
  debug("Exploration music narration: exclusive%d resumed%d",int(exclusive),int(resumed));
  debug("Exploration music observation complete: observed%d total%d stable%d",observed,total,int(stable));
  _background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def observe(cpp,header):
 anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")';assert cpp.count(anchor)==1
 return cpp.replace(anchor,PROBE+'\n'+anchor),header
def production(cpp,header):
 old=' if (!keepSound) { _mixer->stopHandle(_effectHandle); _mixer->stopHandle(_musicHandle); _mixer->stopHandle(_soundHandle); }'
 new=''' int explorationLoop=-1;int32 explorationState=0;
 if(!restoring&&parsed.mode==1&&ConfMan.getBool("astronomica_audio")&&ConfMan.getBool("astronomica_entry_scripts")){
  _runner.getValue(0,60,explorationState);
  explorationLoop=explorationState==1?908:((place>=219&&place<=251)||place==410||place==1?901:((place>=361&&place<=389)||place==420?903:902));
 }
 const bool keepMusic=explorationLoop>=0&&_loopSound==explorationLoop&&_mixer->isSoundHandleActive(_musicHandle);
 if(!keepSound){
  _mixer->stopHandle(_effectHandle);
  if(!keepMusic)_mixer->stopHandle(_musicHandle);
  if(!keepMusic||!(_soundHandle==_musicHandle))_mixer->stopHandle(_soundHandle);
  if(keepMusic){_soundHandle=_musicHandle;_lastSound=explorationLoop;}
 }'''
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 old=' _loopSound = -1; _loopEnabled = true; _lastSoundAt = 0;';assert cpp.count(old)==1
 cpp=cpp.replace(old,' _loopSound = explorationLoop; _loopEnabled = true; _lastSoundAt = 0;')
 return observe(cpp,header)
