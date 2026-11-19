"""Keep speech over a temporarily attenuated Music stream; transient state is not serialized."""
from pathlib import Path
w=Path(__file__).resolve().parent

def production(cpp,header):
 old=' Audio::SoundHandle _musicHandle;';assert header.count(old)==1
 header=header.replace(old,old+'\n Audio::SoundHandle _duckedMusicHandle;\n int _unduckedMusicVolume = -1; // Transient channel volume, never a saved preference.')
 start=cpp.index('void AstronomicaEngine::synchronizeMusicHandle() {');end=cpp.index('bool AstronomicaEngine::isBlockingSound(',start)
 body='''void AstronomicaEngine::synchronizeMusicHandle() {
 const bool music=_mixer->isSoundHandleActive(_musicHandle);
 const bool foreground=_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle);
 const bool speech=foreground&&!(_soundHandle==_effectHandle);
 if(_unduckedMusicVolume>=0&&(!music||!(_duckedMusicHandle==_musicHandle))){
  if(_mixer->isSoundHandleActive(_duckedMusicHandle))_mixer->setChannelVolume(_duckedMusicHandle,byte(_unduckedMusicVolume));
  _unduckedMusicVolume=-1;
 }
 if(music){
  if(speech){
   if(_unduckedMusicVolume<0){_duckedMusicHandle=_musicHandle;_unduckedMusicVolume=_mixer->getChannelVolume(_musicHandle);}
   _mixer->setChannelVolume(_musicHandle,byte((_unduckedMusicVolume+1)/2));
  }else if(_unduckedMusicVolume>=0){
   _mixer->setChannelVolume(_musicHandle,byte(_unduckedMusicVolume));_unduckedMusicVolume=-1;
  }
 }
 // Blocking/intro loops wait on _soundHandle: never replace their completed
 // voice handle with the endless Music handle while that wait is on stack.
 if(!foreground&&music&&!_blockingSoundDepth&&!_introductionActive){
  _soundHandle=_musicHandle;_lastSound=_loopSound;
 }
}
bool AstronomicaEngine::playSound(int id, uint32 now, bool looping) {
 Audio::SeekableAudioStream *stream=openSound(id);if(!stream)return false;
 const bool keepForeground=looping&&_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle);
 if(looping){
  if(!keepForeground)_mixer->stopHandle(_soundHandle);_mixer->stopHandle(_musicHandle);
  Audio::AudioStream*loop=Audio::makeLoopingAudioStream(stream,0);
  if(_clockPaused&&id>=900){
   if(!Video::playPausedAudioStream(_mixer,Audio::Mixer::kMusicSoundType,&_musicHandle,loop,Audio::Mixer::kMaxChannelVolume,0,DisposeAfterUse::YES,0))return false;
  }else _mixer->playStream(Audio::Mixer::kMusicSoundType,&_musicHandle,loop);
  if(!keepForeground)_soundHandle=_musicHandle;
 }else{
  const bool feedback=isFeedbackEffect(id);
  if(!(_soundHandle==_musicHandle))_mixer->stopHandle(_soundHandle);
  _mixer->playStream(Audio::Mixer::kSFXSoundType,&_soundHandle,stream);
  if(feedback)_effectHandle=_soundHandle;
  _lastSoundAt=now;
 }
 if(!keepForeground)_lastSound=id;++_soundsStarted;
 synchronizeMusicHandle();
 // Start the selected ambience under an initial voice/effect too. P501's
 // default S0 is its introduction until an original opcode27 selects Music.
 if(!looping&&!_mixer->isSoundHandleActive(_musicHandle)&&!_moviePlaying&&_loopEnabled&&_loopSound>=0&&_loopSound!=id&&!(_place==501&&_loopSound==0))
  playSound(_loopSound,now,true);
 return true;
}
void AstronomicaEngine::resumeLoopAt(uint32 now) {
 synchronizeMusicHandle();
 if(_mixer->isSoundHandleActive(_musicHandle))return;
 if(_moviePlaying||_loopSound<0||!_loopEnabled)return;
 const bool foreground=_mixer->isSoundHandleActive(_soundHandle);
 if(foreground&&(_loopSound==_lastSound||(_place==501&&_loopSound==0)))return;
 if(!foreground&&_place>=500&&_place<=550&&uint32(now-_lastSoundAt)<=5000)return;
 if(!playSound(_loopSound,now,true))_loopSound=-1;
 else debug("Astronomica P%d loop: S%d.WAV",_place,_loopSound);
}
'''
 cpp=cpp[:start]+body+cpp[end:]
 # Both channel timelines are transient; save formats have one settled ambient stream.
 old='(_mixer->isSoundHandleActive(_musicHandle)&&!_mixer->isSoundHandleActive(_soundHandle)&&!(_soundHandle==_musicHandle))';assert cpp.count(old)==4
 cpp=cpp.replace(old,'(_mixer->isSoundHandleActive(_musicHandle)&&!(_soundHandle==_musicHandle))')
 old='''  if (action.opcode == 10) {
   // _stop_sounds ignores its argument and calls sndPlaySound(NULL,1).
   _mixer->stopHandle(_soundHandle); _mixer->stopHandle(_effectHandle); _mixer->stopHandle(_musicHandle);
   continue;
  }''';assert cpp.count(old)==1
 cpp=cpp.replace(old,'''  if (action.opcode == 10) {
   // Stop the foreground voice/effect. Ambience has its own explicit loop,
   // scene and movie controls, and must not restart after a voice is stopped.
   if(!(_soundHandle==_musicHandle))_mixer->stopHandle(_soundHandle);
   _mixer->stopHandle(_effectHandle);synchronizeMusicHandle();
   continue;
  }''')
 old='    _introductionActive=false;';assert cpp.count(old)==1;cpp=cpp.replace(old,old+'synchronizeMusicHandle();')
 old=' if (pauseMovie && _movie) _movie->pauseVideo(false);';assert cpp.count(old)==1;cpp=cpp.replace(old,' synchronizeMusicHandle();\n'+old)
 old=''' return true;
}
Audio::SeekableAudioStream *AstronomicaEngine::openSound''';assert cpp.count(old)==1;cpp=cpp.replace(old,''' synchronizeMusicHandle();
 return true;
}
Audio::SeekableAudioStream *AstronomicaEngine::openSound''')
 return cpp,header
