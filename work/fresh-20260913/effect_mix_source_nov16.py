"""Keep reviewed shared puzzle feedback separate from music and narration."""
from pathlib import Path

PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_effect_mix")&&ConfMan.getBool("astronomica_verify_effect_mix")){
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",false);
  bool ok=loadPlace(517,false,true);_loopSound=0;_loopEnabled=true;
  ok=playSound(0,scriptClock(),true)&&ok;const Audio::SoundHandle music=_soundHandle;
  for(int id:{2,3,4,5}){
   const uint32 before=_mixer->getSoundElapsedTime(_soundHandle);
   ok=playSound(id,scriptClock())&&ok;_system->delayMillis(80);
   const bool overlap=_soundHandle==music&&_lastSound==0&&_mixer->isSoundHandleActive(_soundHandle)&&_mixer->isSoundHandleActive(_effectHandle)&&_mixer->getSoundElapsedTime(_soundHandle)>=before;
   Common::MemoryWriteStreamDynamic out(DisposeAfterUse::YES);
   const bool guarded=!canSaveGameStateCurrently()&&!canLoadGameStateCurrently()&&saveGameStream(&out,false).getCode()!=Common::kNoError&&out.size()==0;
   debug("Effect mix feedback: %s (id%d,overlap%d,saveGuard%d)",overlap&&guarded?"PASS":"FAIL",id,int(overlap),int(guarded));ok=overlap&&guarded&&ok;
  }
  ok=playSound(1,scriptClock())&&ok;
  const bool voice=!(_soundHandle==music)&&_lastSound==1&&!_mixer->isSoundHandleActive(_effectHandle)&&!_mixer->hasActiveChannelOfType(Audio::Mixer::kMusicSoundType);
  while(_mixer->isSoundHandleActive(_soundHandle)&&!shouldQuit()){pollPlayerInput();_system->delayMillis(10);}
  resumeLoopAt(scriptClock());const bool resumed=_lastSound==0&&_mixer->hasActiveChannelOfType(Audio::Mixer::kMusicSoundType);
  debug("Effect mix voice: %s (voiceExclusive%d,musicResumed%d)",voice&&resumed?"PASS":"FAIL",int(voice),int(resumed));ok=voice&&resumed&&ok;
  ok=playSound(2,scriptClock())&&ok;const bool effectStarted=_mixer->isSoundHandleActive(_effectHandle);
  ok=loadPlace(103,false,true)&&ok;const bool cleaned=!_mixer->isSoundHandleActive(_effectHandle)&&!_mixer->isSoundHandleActive(_soundHandle);
  debug("Effect mix scene cleanup: %s",effectStarted&&cleaned?"PASS":"FAIL");ok=effectStarted&&cleaned&&ok;
  debug("Effect mix native result: %s",ok?"PASS":"FAIL");_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''

def production(cpp,header):
    signatures=[]
    for id in (2,3,4,5):
        data=Path('D:/astro/PLACES/P517/S%d.WAV'%id).read_bytes();h=2166136261
        for value in data:h=((h^value)*16777619)&0xffffffff
        signatures.append((len(data),h))
    role='''bool AstronomicaEngine::isFeedbackEffect(int id) const {
 if(id<0||id>=300||id==_scene.introSoundId||isBlockingSound(id))return false;
 const Common::Path path=ConfMan.getPath("path").join(Common::Path(Common::String::format("PLACES/P%d/S%d.WAV",_place,id)));
'''+''.join(' if(universeFileIdentity(path,%uU,0x%08xU))return true;\n'%pair for pair in signatures)+''' return false;
}
'''
    anchor='bool AstronomicaEngine::playSound(int id, uint32 now, bool looping) {'
    assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,role+anchor)
    old=' // sndPlaySound is a single channel; a new sound replaces the old one.'
    new=''' // Reviewed shared feedback uses a separate transient Effects channel.
 if(!looping&&isFeedbackEffect(id)){
  _mixer->stopHandle(_effectHandle);
  _mixer->playStream(Audio::Mixer::kSFXSoundType,&_effectHandle,stream);
  ++_soundsStarted;return true;
 }
 if(!looping)_mixer->stopHandle(_effectHandle);
 // Narration replaces the music; feedback leaves its clock and loop intact.'''
    assert cpp.count(old)==1;cpp=cpp.replace(old,new)
    cpp=cpp.replace('closeMovie(); _pendingImage.free(); _mixer->stopHandle(_soundHandle);','closeMovie(); _pendingImage.free(); _mixer->stopHandle(_effectHandle); _mixer->stopHandle(_soundHandle);')
    cpp=cpp.replace('if (!keepSound) _mixer->stopHandle(_soundHandle);','if (!keepSound) { _mixer->stopHandle(_effectHandle); _mixer->stopHandle(_soundHandle); }')
    old='if (action.opcode == 3 && _movie) {\n   _mixer->stopHandle(_soundHandle);'
    assert cpp.count(old)==1;cpp=cpp.replace(old,old+' _mixer->stopHandle(_effectHandle);')
    old='// _stop_sounds ignores its argument and calls sndPlaySound(NULL,1).\n   _mixer->stopHandle(_soundHandle);'
    assert cpp.count(old)==1;cpp=cpp.replace(old,old+' _mixer->stopHandle(_effectHandle);')
    for signature in ('bool AstronomicaEngine::canSaveGameStateCurrently(Common::U32String *msg) {','bool AstronomicaEngine::canLoadGameStateCurrently(Common::U32String *msg) {'):
        assert cpp.count(signature)==1
        cpp=cpp.replace(signature,signature+'\n if(_mixer->isSoundHandleActive(_effectHandle)){if(msg)*msg=Common::U32String("Wait until the effect finishes.");return false;}')
    for signature in ('Common::Error AstronomicaEngine::saveGameStream(Common::WriteStream *stream, bool) {','Common::Error AstronomicaEngine::loadGameStream(Common::SeekableReadStream *stream) {'):
        assert cpp.count(signature)==1
        cpp=cpp.replace(signature,signature+'\n if(_mixer->isSoundHandleActive(_effectHandle))return Common::kReadingFailed;')
    assert header.count(' Audio::SoundHandle _soundHandle;')==1
    header=header.replace(' Audio::SoundHandle _soundHandle;',' Audio::SoundHandle _soundHandle;\n Audio::SoundHandle _effectHandle;\n bool isFeedbackEffect(int id) const;')
    anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")'
    assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,PROBE+'\n'+anchor)
    return cpp,header
