"""Apply the remaining original shared-music defaults to close-ups and special mode0 scenes."""
HELPER=r'''
static int originalSceneAmbient(int mode,int place,int32 state){
 int loop=place==1?901:place==422?902:0;
 if(mode==3||place==402)loop=900;
 if(mode==1)loop=state==1?908:((place>=219&&place<=251)||place==410||place==1?901:((place>=361&&place<=389)||place==420?903:902));
 return loop;
}
'''
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_scene_music")&&ConfMan.getBool("astronomica_verify_scene_music")){
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",true);_runner.resetGlobals();
  uint matched=0,total=0;
  for(int flag:{0,1})for(int place:{1,94,104,126,402,422,103,219,361}){
   _runner.defineValue(0,60,flag);const int expected=place==1?901:place==422?902:(place==103||place==219||place==361)?(flag?908:place==219?901:place==361?903:902):900;
   const bool loaded=loadPlace(place);resumeLoopAt(scriptClock());
   const bool correct=loaded&&_loopSound==expected&&_musicHandle==_soundHandle&&_mixer->isSoundHandleActive(_musicHandle)&&_mixer->hasActiveChannelOfType(Audio::Mixer::kMusicSoundType);
   debug("Scene music entry: P%d flag%d mode%d expected%d actual%d active%d",place,flag,_scene.mode,expected,_loopSound,int(correct));matched+=correct;++total;
  }
  ConfMan.setBool("astronomica_entry_scripts",true);bool ready=loadPlace(1);resumeLoopAt(scriptClock());
  const bool normal=ready&&loadGameState(32).getCode()==Common::kNoError&&_place==525;
  ready=loadPlace(1);_loopSound=0;_loopEnabled=true;ready=playSound(0,scriptClock(),true)&&ready;
  const bool legacy=ready&&loadGameState(32).getCode()==Common::kNoError&&_place==525;
  ready=loadPlace(1);resumeLoopAt(scriptClock());playSound(911,scriptClock());PauseToken pause=pauseEngine();const uint32 before=p510WholeLiveHash();
  const bool denied=loadGameState(32).getCode()!=Common::kNoError&&_place==1&&p510WholeLiveHash()==before;pause.clear();
  debug("Scene music P1 recipient: current%d legacy%d narrationRefused%d",int(normal),int(legacy),int(denied));
  debug("Scene music observation complete: matched%u total%u",matched,total);_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def observe(cpp,header):
 anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")';assert cpp.count(anchor)==1
 return cpp.replace(anchor,PROBE+'\n'+anchor),header
def production(cpp,header):
 anchor='bool AstronomicaEngine::changePlace(int place) {';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,HELPER+'\n'+anchor)
 old='if(!restoring&&parsed.mode==1&&ConfMan.getBool("astronomica_audio")&&ConfMan.getBool("astronomica_entry_scripts"))'
 assert cpp.count(old)==1;cpp=cpp.replace(old,'if(!restoring&&ConfMan.getBool("astronomica_audio")&&ConfMan.getBool("astronomica_entry_scripts"))')
 old='explorationLoop=explorationState==1?908:((place>=219&&place<=251)||place==410||place==1?901:((place>=361&&place<=389)||place==420?903:902));'
 assert cpp.count(old)==1;cpp=cpp.replace(old,'explorationLoop=originalSceneAmbient(parsed.mode,place,explorationState);')
 old='const bool keepMusic=explorationLoop>=0&&';assert cpp.count(old)==1;cpp=cpp.replace(old,'const bool keepMusic=parsed.mode==1&&place!=402&&explorationLoop>=0&&')
 old='Audio::SeekableAudioStream *music = openSound(0);\n   if (music) { _loopSound = 0; delete music; }'
 new='const int musicId=originalSceneAmbient(_scene.mode,_place,explorationState);\n   Audio::SeekableAudioStream *music = openSound(musicId);\n   if (music) { _loopSound = musicId; delete music; }else _loopSound=-1;'
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 old='(_loopSound!=0||!_loopEnabled||_lastSound!=0||!universeFileIdentity(ConfMan.getPath("path").join("PLACES/P1/S0.WAV"),2282024,2465437726U))'
 new='(!_loopEnabled||!((_loopSound==0&&_lastSound==0&&universeFileIdentity(ConfMan.getPath("path").join("PLACES/P1/S0.WAV"),2282024,2465437726U))||(_loopSound==901&&_lastSound==901&&_soundHandle==_musicHandle&&universeFileIdentity(ConfMan.getPath("path").join("SOUNDS/S1.WAV"),384936,3697759893U))))'
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 old='const bool music=_place==1&&_loopSound==0&&_loopEnabled&&_lastSound==0&&';assert cpp.count(old)==1;cpp=cpp.replace(old,'const bool music=_place==1&&_loopSound==901&&_loopEnabled&&_lastSound==901&&')
 return observe(cpp,header)
