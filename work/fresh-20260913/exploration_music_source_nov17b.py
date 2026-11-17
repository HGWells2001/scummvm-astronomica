"""Complete exploration ambience continuity, paused admission and the P117 save recipient."""
from exploration_music_source_nov17 import production as previous
EXTRA=r'''
  _runner.defineValue(0,60,1);bool pauseLoaded=loadPlace(117);resumeLoopAt(scriptClock());
  PauseToken paused=pauseEngine();Common::MemoryReadStream pausedInput(saved.getData(),saved.size());
  pauseLoaded=loadGameStream(&pausedInput).getCode()==Common::kNoError&&pauseLoaded;resumeLoopAt(scriptClock());
  const Audio::SoundHandle pausedMusic=_musicHandle;const uint32 stoppedAt=_mixer->getSoundElapsedTime(pausedMusic);_system->delayMillis(70);
  const bool held=pauseLoaded&&_clockPaused&&_mixer->isSoundHandleActive(pausedMusic)&&_mixer->getSoundElapsedTime(pausedMusic)==stoppedAt;
  paused.clear();_system->delayMillis(220);const bool moving=!_clockPaused&&_mixer->getSoundElapsedTime(pausedMusic)>stoppedAt;
  debug("Exploration music paused ASVM2: paused%d resumed%d",int(held),int(moving));
  _runner.defineValue(0,60,0);bool recipient=loadPlace(117);resumeLoopAt(scriptClock());
  playSound(911,scriptClock());PauseToken voicePause=pauseEngine();const uint32 before=p510WholeLiveHash();
  const bool refused=loadGameState(32).getCode()!=Common::kNoError;const bool preserved=p510WholeLiveHash()==before&&_place==117;
  voicePause.clear();while(_mixer->isSoundHandleActive(_soundHandle)&&!shouldQuit()){pollPlayerInput();_system->delayMillis(10);}
  resumeLoopAt(scriptClock());const bool puzzleLoaded=recipient&&loadGameState(32).getCode()==Common::kNoError;
  const bool memoryMusic=puzzleLoaded&&_place==525&&_loopSound==0&&_musicHandle==_soundHandle&&_mixer->isSoundHandleActive(_musicHandle);
  debug("Exploration music P525 recipient: busyRefused%d preserved%d loaded%d music%d",int(refused),int(preserved),int(puzzleLoaded),int(memoryMusic));
'''
def production(cpp,header):
 cpp,header=previous(cpp,header)
 old='const int prior=_loopSound;const Audio::SoundHandle old=_musicHandle;const uint starts=_soundsStarted;'
 assert cpp.count(old)==1;cpp=cpp.replace(old,old+'const bool hadMusic=_mixer->isSoundHandleActive(old);')
 cpp=cpp.replace('const bool continuous=prior!=expected||!_mixer->isSoundHandleActive(old)||_musicHandle==old;','const bool continuous=!hadMusic||prior!=expected||(_musicHandle==old&&_mixer->isSoundHandleActive(old));')
 cpp=cpp.replace('const bool countOK=!active||_soundsStarted==starts+uint(prior!=expected||old!=_musicHandle);','const bool countOK=!active||_soundsStarted==starts+uint(!hadMusic||prior!=expected);')
 anchor='  debug("Exploration music observation complete: observed%d total%d stable%d",observed,total,int(stable));';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,EXTRA+'\n'+anchor)
 old='_mixer->playStream(Audio::Mixer::kMusicSoundType,&_musicHandle,Audio::makeLoopingAudioStream(stream,0));'
 new='''Audio::AudioStream*loop=Audio::makeLoopingAudioStream(stream,0);
  if(_clockPaused&&id>=900){
   if(!Video::playPausedAudioStream(_mixer,Audio::Mixer::kMusicSoundType,&_musicHandle,loop,Audio::Mixer::kMaxChannelVolume,0,DisposeAfterUse::YES,0))return false;
  }else _mixer->playStream(Audio::Mixer::kMusicSoundType,&_musicHandle,loop);'''
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 start=cpp.index('}else if(fromP117){');end=cpp.index('}else if(fromP519){',start);part=cpp[start:end]
 old='_mixer->isSoundHandleActive(_soundHandle)';assert part.count(old)==1
 part=part.replace(old,'(_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle))');cpp=cpp[:start]+part+cpp[end:]
 return cpp,header
