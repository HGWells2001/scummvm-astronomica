"""Observe the actual P512 movie/blocking-voice boundary, without ABI changes."""
def inject(code):
 entry='bool AstronomicaEngine::verifyP512Puzzle() {';assert code.count(entry)==1
 probe=r'''
 if(ConfMan.hasKey("astronomica_verify_weather_order_audio")&&ConfMan.getBool("astronomica_verify_weather_order_audio")) {
  _runner.resetGlobals();if(!loadPlace(512)||!_movie||_scene.scripts.size()!=6)return false;
  _runner.defineValue(1,4,1);_runner.defineValue(1,5,1);
  const uint32 start=scriptClock();
  if(!_runner.enqueue(_scene.scripts[2],start,true))return false;
  const uint32 began=_system->getMillis();
  while(_runner.pendingCount()&&_system->getMillis()-began<3000){runScriptsAt(scriptClock());updateMovie();_system->delayMillis(5);}
  int32 previous=-1;if(_runner.pendingCount()||!_moviePlaying||!_movie->isPlaying()||!_runner.getValue(1,5,previous)||previous!=1)return false;
  if(_scene.sprites.size()!=64||_scene.sprites[13].click.size()<3)return false;
  Script original;original.push_back(_scene.sprites[13].click[2]);
  if(original[0].offset!=335959||original[0].opcode!=23||original[0].args.size()!=6||original[0].args[0]!=24||original[0].args[1]!=0)return false;
  const uint sounds=_soundsStarted;debug("Weather movie audio before: result%d playing%d source%u",previous,int(_moviePlaying),original[0].offset);
  if(!_runner.start(original,scriptClock(),true)||!_runner.getValue(1,5,previous)||previous!=0||_soundsStarted!=sounds+1||_lastSound!=10||!_movie||_movie->isPaused())return false;
  debug("Weather movie audio result: PASS (original mode0 command,active original clip,S10,final0,decoder resumed)");return loadPlace(103);
 }
'''
 code=code.replace(entry,entry+'\n'+probe)
 entry='uint32 AstronomicaEngine::onBlockingSound(int id, uint32 now) {';assert code.count(entry)==1
 hook=r'''
 if((id==10||id==11||id==12)&&ConfMan.hasKey("astronomica_verify_weather_order_audio")&&ConfMan.getBool("astronomica_verify_weather_order_audio")) {
  int32 previous=-1;_runner.getValue(1,5,previous);
  debug("Weather movie audio voice: id%d result%d movie%d decoder%d",id,previous,int(_moviePlaying),int(_movie&&_movie->isPlaying()));
 }
'''
 return code.replace(entry,entry+'\n'+hook)
