"""Keep completed foreground handles stable while a blocking/intro wait is active."""
from speech_duck_probe_nov19c import observe as previous

def observe(cpp,header):
 cpp,header=previous(cpp,header)
 old='const bool keepForeground=looping&&_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle);'
 new='const bool keepForeground=looping&&!(_soundHandle==_musicHandle)&&(_mixer->isSoundHandleActive(_soundHandle)||_blockingSoundDepth||_introductionActive);'
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 old='   if (_scene.introSound && _previousPlace != 408 && _runner.variantRound() <= 1 && playSound(_scene.introSoundId, scriptClock())) {'
 new='''   const bool playIntroduction=_scene.introSound&&_previousPlace!=408&&_runner.variantRound()<=1;
   _introductionActive=playIntroduction;
   if (playIntroduction && playSound(_scene.introSoundId, scriptClock())) {'''
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 old='    const Common::Point introMouse=_eventMan->getMousePos();';assert cpp.count(old)==1;cpp=cpp.replace(old,'    const Audio::SoundHandle introVoice=_soundHandle;\n'+old)
 start=cpp.index('   const bool playIntroduction=');end=cpp.index('Audio::SeekableAudioStream *AstronomicaEngine::openSound',start);scope=cpp[start:end];scope=scope.replace('while (_mixer->isSoundHandleActive(_soundHandle) && !shouldQuit())','while (_mixer->isSoundHandleActive(introVoice) && !shouldQuit())');scope=scope.replace('   _lastSoundAt = 0; // Original resets this after scene loading.','   _introductionActive=false;synchronizeMusicHandle();\n   _lastSoundAt = 0; // Original resets this after scene loading.');cpp=cpp[:start]+scope+cpp[end:]
 old=' if (playSound(id,now)) {\n  while (_mixer->isSoundHandleActive(_soundHandle) && !shouldQuit()) {'
 new=' if (playSound(id,now)) {\n  const Audio::SoundHandle blockingVoice=_soundHandle;\n  while (_mixer->isSoundHandleActive(blockingVoice) && !shouldQuit()) {'
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 # A deterministic ended-voice/late-Music check protects short clips and slow media.
 start=cpp.index(' if(ConfMan.hasKey("astronomica_verify_speech_duck")');end=cpp.index(' if(ConfMan.hasKey("astronomica_verify_door_music")',start);scope=cpp[start:end]
 anchor='  _mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,oldMusic);'
 block='''  bool ended=true;
  for(uint kind=0;kind<2;++kind){
   loadPlace(103,false,true);_loopEnabled=false;_loopSound=902;
   if(kind==0)_introductionActive=true;else ++_blockingSoundDepth;
   ended=playSound(920,scriptClock())&&ended;const Audio::SoundHandle completed=_soundHandle;_mixer->stopHandle(completed);
   ended=playSound(902,scriptClock(),true)&&ended;synchronizeMusicHandle();
   ended=ended&&_soundHandle==completed&&!_mixer->isSoundHandleActive(completed)&&_mixer->isSoundHandleActive(_musicHandle)&&_mixer->getChannelVolume(_musicHandle)==255;
   if(kind==0)_introductionActive=false;else --_blockingSoundDepth;
   _loopEnabled=true;synchronizeMusicHandle();ended=ended&&_soundHandle==_musicHandle;
  }
  all=ended&&all;debug("Speech duck ended foreground ownership: %d",int(ended));
'''
 assert scope.count(anchor)==1;scope=scope.replace(anchor,block+anchor);cpp=cpp[:start]+scope+cpp[end:]
 return cpp,header
