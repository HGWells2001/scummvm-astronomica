"""Retain primary foreground semantics while an independent music handle keeps its clock."""
from effect_mix_source_nov16 import production as first

PLAY=r'''void AstronomicaEngine::synchronizeMusicHandle() {
 if(!_mixer->isSoundHandleActive(_soundHandle)&&_mixer->isSoundHandleActive(_musicHandle)){
  _soundHandle=_musicHandle;_lastSound=_loopSound;
 }
}
bool AstronomicaEngine::playSound(int id, uint32 now, bool looping) {
 Audio::SeekableAudioStream *stream=openSound(id);if(!stream)return false;
 if(looping){
  _mixer->stopHandle(_soundHandle);_mixer->stopHandle(_musicHandle);
  _mixer->playStream(Audio::Mixer::kMusicSoundType,&_musicHandle,Audio::makeLoopingAudioStream(stream,0));
  _soundHandle=_musicHandle;
 }else{
  const bool feedback=isFeedbackEffect(id);
  if(!feedback)_mixer->stopHandle(_musicHandle);
  if(!(_soundHandle==_musicHandle))_mixer->stopHandle(_soundHandle);
  _mixer->playStream(Audio::Mixer::kSFXSoundType,&_soundHandle,stream);
  if(feedback)_effectHandle=_soundHandle;
  _lastSoundAt=now;
 }
 _lastSound=id;++_soundsStarted;return true;
}
'''

def production(cpp,header):
 cpp,header=first(cpp,header)
 # Every lifecycle boundary that clears feedback also clears independent music.
 cpp=cpp.replace('_mixer->stopHandle(_effectHandle);','_mixer->stopHandle(_effectHandle); _mixer->stopHandle(_musicHandle);')
 start=cpp.index('bool AstronomicaEngine::playSound(int id, uint32 now, bool looping) {')
 end=cpp.index('void AstronomicaEngine::resumeLoopAt(uint32 now) {',start)
 cpp=cpp[:start]+PLAY+cpp[end:]
 anchor='void AstronomicaEngine::resumeLoopAt(uint32 now) {'
 cpp=cpp.replace(anchor,anchor+'\n synchronizeMusicHandle();\n if(_mixer->isSoundHandleActive(_musicHandle))return;')
 # Availability queries normalize an existing live handle only; no playback is started.
 old=' if(_mixer->isSoundHandleActive(_effectHandle))'
 assert cpp.count(old)==4
 cpp=cpp.replace(old,' synchronizeMusicHandle();\n'+old)
 cpp=cpp.replace('_loopEnabled = false; _mixer->stopHandle(_soundHandle); continue;','_loopEnabled = false; _mixer->stopHandle(_soundHandle); _mixer->stopHandle(_musicHandle); continue;')
 cpp=cpp.replace('_mixer->stopHandle(_soundHandle); _loopSound = action.value;','_mixer->stopHandle(_soundHandle); _mixer->stopHandle(_musicHandle); _loopSound = action.value;')
 header=header.replace(' Audio::SoundHandle _effectHandle;',' Audio::SoundHandle _effectHandle;\n Audio::SoundHandle _musicHandle;\n void synchronizeMusicHandle();')
 cpp=cpp.replace('const Audio::SoundHandle music=_soundHandle;','const Audio::SoundHandle music=_musicHandle;')
 cpp=cpp.replace('const uint32 before=_mixer->getSoundElapsedTime(_soundHandle);','const uint32 before=_mixer->getSoundElapsedTime(_musicHandle);')
 cpp=cpp.replace('const bool overlap=_soundHandle==music&&_lastSound==0&&_mixer->isSoundHandleActive(_soundHandle)&&_mixer->isSoundHandleActive(_effectHandle)&&_mixer->getSoundElapsedTime(_soundHandle)>=before;','const bool overlap=_musicHandle==music&&_lastSound==id&&_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_effectHandle)&&_mixer->getSoundElapsedTime(_musicHandle)>=before;')
 return cpp,header
