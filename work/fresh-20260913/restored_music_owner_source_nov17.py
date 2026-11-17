"""Observe boot admission and music ownership after a genuine pre-change P525 save."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_restored_music_owner")&&ConfMan.getBool("astronomica_verify_restored_music_owner")){
  const int boot=_place;const bool bootLoaded=loadGameState(32).getCode()==Common::kNoError;
  debug("Restored music boot admission: scene%d loaded%d",boot,int(bootLoaded));
  ConfMan.setBool("astronomica_entry_scripts",false);bool menuLoaded=loadPlace(1,false,true)&&loadGameState(32).getCode()==Common::kNoError;
  const Audio::SoundHandle original=_soundHandle;const bool active=_mixer->isSoundHandleActive(original)&&_mixer->hasActiveChannelOfType(Audio::Mixer::kMusicSoundType);
  const bool adopted=_musicHandle==original;const bool feedback=menuLoaded&&playSound(2,scriptClock());_system->delayMillis(80);
  const bool retained=feedback&&_mixer->isSoundHandleActive(original)&&_mixer->hasActiveChannelOfType(Audio::Mixer::kMusicSoundType);
  debug("Restored music ownership observation: menuLoaded%d active%d adopted%d feedback%d retained%d scene%d",int(menuLoaded),int(active),int(adopted),int(feedback),int(retained),_place);
  debug("Restored music owner observation complete");_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def production(cpp,header):
 anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")'
 assert cpp.count(anchor)==1
 return cpp.replace(anchor,PROBE+'\n'+anchor),header
