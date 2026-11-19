from speech_duck_source_nov19 import production

def observe(cpp,header):
 cpp,header=production(cpp,header)
 anchor=' if(ConfMan.hasKey("astronomica_verify_door_music")'
 block=''' if(ConfMan.hasKey("astronomica_verify_speech_duck")&&ConfMan.getBool("astronomica_verify_speech_duck")){
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",false);
  const int oldMusic=_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType),oldSfx=_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType);
  _mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,77);_mixer->setVolumeForSoundType(Audio::Mixer::kSFXSoundType,91);
  bool all=true;uint passed=0;
  for(int song:{900,901,902,903,908}){
   bool ok=loadPlace(103,false,true);_loopSound=song;_loopEnabled=true;ok=playSound(song,scriptClock(),true)&&ok;
   const Audio::SoundHandle music=_musicHandle;_mixer->setChannelVolume(music,170);_system->delayMillis(140);const uint32 elapsed=_mixer->getSoundElapsedTime(music);
   ok=playSound(920,scriptClock())&&ok;const Audio::SoundHandle voice=_soundHandle;
   ok=ok&&_musicHandle==music&&_mixer->isSoundHandleActive(music)&&_mixer->isSoundHandleActive(voice)&&_mixer->getChannelVolume(music)==85&&_unduckedMusicVolume==170&&!canSaveGameStateCurrently()&&!canLoadGameStateCurrently();
   _system->delayMillis(150);synchronizeMusicHandle();ok=ok&&_mixer->getSoundElapsedTime(music)>elapsed;
   PauseToken pause=pauseEngine();const uint32 mp=_mixer->getSoundElapsedTime(music),vp=_mixer->getSoundElapsedTime(voice);_system->delayMillis(100);
   ok=ok&&_clockPaused&&_mixer->getSoundElapsedTime(music)==mp&&_mixer->getSoundElapsedTime(voice)==vp;pause.clear();_system->delayMillis(140);
   ok=ok&&!_clockPaused&&_mixer->getSoundElapsedTime(music)>mp&&_mixer->getSoundElapsedTime(voice)>vp&&_mixer->getChannelVolume(music)==85;
   ok=playSound(921,scriptClock())&&ok;ok=ok&&_musicHandle==music&&_unduckedMusicVolume==170&&_mixer->getChannelVolume(music)==85;
   const Audio::SoundHandle replacement=_soundHandle;const uint starts=_soundsStarted;
   ok=!playSound(999,scriptClock())&&ok;ok=ok&&_soundHandle==replacement&&_musicHandle==music&&_soundsStarted==starts&&_mixer->getChannelVolume(music)==85;
   ok=playSound(905,scriptClock())&&ok;ok=ok&&_musicHandle==music&&_mixer->isSoundHandleActive(music)&&_mixer->getChannelVolume(music)==170&&_unduckedMusicVolume==-1&&_mixer->isSoundHandleActive(_effectHandle);
   ok=ok&&_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)==77&&_mixer->getVolumeForSoundType(Audio::Mixer::kSFXSoundType)==91;
   if(ok)++passed;all=ok&&all;debug("Speech duck matrix: song%d result%d",song,int(ok));
  }
  bool natural=loadPlace(103,false,true);_loopSound=902;_loopEnabled=true;natural=playSound(902,scriptClock(),true)&&natural;const Audio::SoundHandle naturalMusic=_musicHandle;_mixer->setChannelVolume(naturalMusic,171);natural=playSound(920,scriptClock())&&natural;
  const Audio::SoundHandle naturalVoice=_soundHandle;const uint naturalStarts=_soundsStarted;const uint32 begin=_system->getMillis();
  while(_mixer->isSoundHandleActive(naturalVoice)&&_system->getMillis()-begin<5000){resumeLoopAt(scriptClock());_system->delayMillis(5);}
  resumeLoopAt(scriptClock());natural=natural&&!_mixer->isSoundHandleActive(naturalVoice)&&_musicHandle==naturalMusic&&_soundHandle==naturalMusic&&_mixer->isSoundHandleActive(naturalMusic)&&_mixer->getChannelVolume(naturalMusic)==171&&_unduckedMusicVolume==-1&&_soundsStarted==naturalStarts;
  all=natural&&all;debug("Speech duck natural completion: %d",int(natural));
  bool stop=playSound(921,scriptClock());Script script;Command command;command.opcode=10;command.args.push_back(0);script.push_back(command);stop=_runner.enqueue(script,scriptClock())&&stop;runScripts();
  stop=stop&&_musicHandle==naturalMusic&&_mixer->isSoundHandleActive(naturalMusic)&&_mixer->getChannelVolume(naturalMusic)==171&&_soundHandle==naturalMusic;all=stop&&all;debug("Speech duck stop command: %d",int(stop));
  bool scene=playSound(921,scriptClock())&&loadPlace(104,false,true);scene=scene&&_musicHandle==naturalMusic&&_mixer->isSoundHandleActive(naturalMusic)&&_mixer->getChannelVolume(naturalMusic)==171&&_unduckedMusicVolume==-1;
  scene=scene&&playSound(921,scriptClock())&&loadPlace(219,false,true);resumeLoopAt(scriptClock());scene=scene&&_mixer->isSoundHandleActive(_musicHandle)&&!(_musicHandle==naturalMusic)&&_mixer->getChannelVolume(_musicHandle)==255&&_unduckedMusicVolume==-1;
  all=scene&&all;debug("Speech duck scene transitions: %d",int(scene));
  bool blocked=loadPlace(103,false,true);_loopSound=902;_loopEnabled=true;blocked=playSound(902,scriptClock(),true)&&blocked;const Audio::SoundHandle blockingMusic=_musicHandle;_mixer->setChannelVolume(blockingMusic,150);const uint32 clock=scriptClock();onBlockingSound(912,clock);resumeLoopAt(scriptClock());
  blocked=blocked&&_blockingSoundDepth==0&&_musicHandle==blockingMusic&&_mixer->isSoundHandleActive(blockingMusic)&&_mixer->getChannelVolume(blockingMusic)==150&&_soundHandle==blockingMusic;
  all=blocked&&all;debug("Speech duck blocking voice: %d",int(blocked));
  bool bootstrap=loadPlace(103,false,true);_mixer->stopHandle(_musicHandle);_mixer->stopHandle(_soundHandle);_loopSound=902;_loopEnabled=true;const uint bootStarts=_soundsStarted;
  bootstrap=playSound(920,scriptClock())&&bootstrap;bootstrap=bootstrap&&_mixer->isSoundHandleActive(_soundHandle)&&_mixer->isSoundHandleActive(_musicHandle)&&!(_musicHandle==_soundHandle)&&_lastSound==920&&_mixer->getChannelVolume(_musicHandle)==128&&_soundsStarted==bootStarts+2;
  all=bootstrap&&all;debug("Speech duck first voice bootstrap: %d",int(bootstrap));
  loadPlace(103,false,true);ConfMan.setBool("astronomica_entry_scripts",true);const uint introStarts=_soundsStarted;bool intro=loadPlace(503);ConfMan.setBool("astronomica_entry_scripts",false);
  intro=intro&&!_introductionActive&&_mixer->isSoundHandleActive(_musicHandle)&&_soundHandle==_musicHandle&&_mixer->getSoundElapsedTime(_musicHandle)>5000&&_mixer->getChannelVolume(_musicHandle)==255&&_unduckedMusicVolume==-1&&_soundsStarted==introStarts+2;
  all=intro&&all;debug("Speech duck real introduction: %d",int(intro));
  loadPlace(103,false,true);_loopSound=902;_loopEnabled=true;resumeLoopAt(scriptClock());Common::MemoryWriteStreamDynamic saved(DisposeAfterUse::YES);const bool wrote=saveGameStream(&saved,false).getCode()==Common::kNoError;
  Common::MemoryReadStream restored(saved.getData(),saved.size());const bool loaded=wrote&&loadGameStream(&restored).getCode()==Common::kNoError;
  const bool payload=loaded&&_mixer->isSoundHandleActive(_musicHandle)&&_unduckedMusicVolume==-1&&_mixer->getVolumeForSoundType(Audio::Mixer::kMusicSoundType)==77;
  all=payload&&all;debug("Speech duck settled save/load: %d",int(payload));
  _mixer->setVolumeForSoundType(Audio::Mixer::kMusicSoundType,oldMusic);_mixer->setVolumeForSoundType(Audio::Mixer::kSFXSoundType,oldSfx);
  debug("Speech duck complete: %s (matrix%u/5)",all?"PASS":"FAIL",passed);_background.free();_screen.free();quitGame();return Common::kNoError;
 }

'''
 assert cpp.count(anchor)==1
 return cpp.replace(anchor,block+anchor),header
