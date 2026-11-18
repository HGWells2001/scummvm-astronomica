"""Observe door effects, real mixer pause and Music position across original ambient tracks."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_door_pause_matrix")&&ConfMan.getBool("astronomica_verify_door_pause_matrix")){
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",false);uint passed=0;
  struct Case{int place,state,loop;};const Case cases[]={{126,0,900},{103,0,902},{219,0,901},{361,0,903},{103,1,908}};
  for(const Case&c:cases)for(int id:{905,907}){
   _runner.resetGlobals();_runner.defineValue(0,60,c.state);const bool loaded=loadPlace(c.place);resumeLoopAt(scriptClock());_system->delayMillis(100);
   const Audio::SoundHandle owner=_musicHandle;const uint32 musicAt=_mixer->getSoundElapsedTime(owner);const uint before=_soundsStarted;const bool started=playSound(id,scriptClock());
   const bool overlap=_musicHandle==owner&&_mixer->isSoundHandleActive(owner)&&_mixer->isSoundHandleActive(_effectHandle);
   const bool guard=!canSaveGameStateCurrently()&&!canLoadGameStateCurrently();bool frozen=false;
   {PauseToken pause=pauseEngine();const uint32 musicPaused=_mixer->getSoundElapsedTime(owner),effectPaused=_mixer->getSoundElapsedTime(_effectHandle);_system->delayMillis(150);frozen=_musicHandle==owner&&_mixer->getSoundElapsedTime(owner)-musicPaused<50&&_mixer->getSoundElapsedTime(_effectHandle)-effectPaused<50;}
   const uint32 began=_system->getMillis();while(_system->getMillis()-began<800){resumeLoopAt(scriptClock());_system->delayMillis(2);}
   const bool advancing=_musicHandle==owner&&_mixer->isSoundHandleActive(owner)&&_mixer->getSoundElapsedTime(owner)>=musicAt+650&&_soundsStarted==before+1;
   const bool selected=_loopSound==c.loop;playSound(911,scriptClock());const bool narration=!_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_soundHandle);
   const bool correct=loaded&&started&&selected&&overlap&&guard&&frozen&&advancing&&narration;passed+=correct;
   debug("Door pause matrix: place%d state%d loop%d clip%d loaded%d started%d overlap%d guard%d frozen%d advancing%d narration%d result%s",c.place,c.state,c.loop,id,int(loaded),int(started),int(overlap),int(guard),int(frozen),int(advancing),int(narration),correct?"PASS":"FAIL");
  }
  debug("Door pause matrix complete: passed%u total10",passed);_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def observe(cpp,header):
    anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")';assert cpp.count(anchor)==1
    return cpp.replace(anchor,PROBE+'\n'+anchor),header
