"""Observe detached frame bounds for the retained clock seen in the failed native log."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_p525_terminal_clock")&&ConfMan.getBool("astronomica_verify_p525_terminal_clock")){
  for(const char*option:{"astronomica_audio","astronomica_animation","astronomica_sprite_input"})ConfMan.setBool(option,true);
  ConfMan.setBool("astronomica_entry_scripts",false);_runner.resetGlobals();
  bool ok=loadPlace(117);_runner.defineValue(0,29,1);ConfMan.setBool("astronomica_entry_scripts",true);ok=loadPlace(525)&&ok;
  auto pump=[&](){pollPlayerInput();runScripts();animateSpritesAt(scriptClock());resumeLoopAt(scriptClock());updateMovie();_system->updateScreen();_system->delayMillis(5);};
  auto settle=[&](){const uint32 began=_system->getMillis();while(_place==525&&!shouldQuit()&&(_runner.pendingCount()||_runner.clicksBlocked()||_moviePlaying||(_mixer->isSoundHandleActive(_soundHandle)&&_lastSound!=_loopSound))&&_system->getMillis()-began<90000)pump();return _place==525&&!_runner.pendingCount()&&!_runner.clicksBlocked()&&!_moviePlaying;};
  ok=settle()&&ok;
  for(uint step=0;step<4&&ok;++step){clickAtTime(110,385,scriptClock());ok=settle()&&ok;}
  int32 choice=0;ok=_runner.getValue(1,1,choice)&&choice==4&&ok;if(ok){clickAtTime(358,422,scriptClock());ok=settle()&&ok;}
  Common::Array<uint32>w;ok=captureP525Stopped(w,scriptClock())&&ok;
  if(ok){
   Common::File*f=new Common::File();P525StoppedQuickTime detached;
   ok=f->open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P525/FSUN.MOV")))&&detached.loadStream(f)&&detached.seekToFrame(w[10]);
   const uint32 lastStart=detached.nextFrameStartForClockObservation();ok=detached.decodeNextFrame()&&ok;
   const uint32 nextStart=detached.nextFrameStartForClockObservation(),end=w[13]*1000/30;
   debug("P525 terminal clock bounds: scene%d frame%u retained%u lastStart%u nextStart%u end%u",_place,w[10],w[9],lastStart,nextStart,end);
   for(uint32 clock:{lastStart-1,lastStart,end-1,end,end+1}){
    Common::Array<uint32>cell=w;cell[9]=clock;cell.back()=p525StoppedHash(cell);const uint32 live=p510WholeLiveHash();P525StoppedPrepared prepared;
    const bool accepted=prepareP525Stopped(cell,prepared),unchanged=p510WholeLiveHash()==live;
    debug("P525 terminal clock cell: clock%u accepted%d unchanged%d exact%d",clock,int(accepted),int(unchanged),int(accepted&&prepared.decoder->getTime()==clock));ok=unchanged&&ok;
   }
  }
  debug("P525 terminal clock observation complete: %d",int(ok));_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''

def observe(cpp,header):
 old='class P525StoppedQuickTime final:public Video::QuickTimeDecoder{public:void retainStoppedClock(uint32 ms){_lastTimeChange=Audio::Timestamp(ms);}};'
 new='class P525StoppedQuickTime final:public Video::QuickTimeDecoder{public:uint32 nextFrameStartForClockObservation()const{return _nextVideoTrack?_nextVideoTrack->getNextFrameStartTime():0xffffffffU;}void retainStoppedClock(uint32 ms){_lastTimeChange=Audio::Timestamp(ms);}};'
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")';assert cpp.count(anchor)==1
 return cpp.replace(anchor,PROBE+'\n'+anchor),header

def production(cpp,header):
 cpp,header=observe(cpp,header)
 old='||uint64(w[9])<uint64(w[13])*1000/30||'
 assert cpp.count(old)==1;cpp=cpp.replace(old,'||')
 old='if(!p.decoder->seekToFrame(w[10])||!p.decoder->decodeNextFrame()||p.decoder->getCurFrame()!=int32(w[10]))return false;'
 new='''if(!p.decoder->seekToFrame(w[10]))return false;
 // A stopped clock is independent of the exhausted range. Validate the
 // decoded final-frame interval rather than requiring clock >= range end.
 P525StoppedQuickTime*stopped=static_cast<P525StoppedQuickTime*>(p.decoder);
 const uint32 frameStart=stopped->nextFrameStartForClockObservation(),rangeEnd=Audio::Timestamp(0,w[13],30).msecs();
 if(frameStart>=rangeEnd||w[9]<frameStart||!p.decoder->decodeNextFrame()||p.decoder->getCurFrame()!=int32(w[10])||stopped->nextFrameStartForClockObservation()<rangeEnd)return false;'''
 assert cpp.count(old)==1;cpp=cpp.replace(old,new)
 # Candidate-only observations include wrong-frame refusal and the existing
 # complete memory-installation/future verifier at the observed low clock.
 anchor='  debug("P525 terminal clock observation complete: %d",int(ok));'
 extra=r'''
  if(ok){
   for(uint32 frame:{w[10]-1,w[10]+1}){
    Common::Array<uint32>bad=w;bad[10]=frame;bad[9]=80066;bad.back()=p525StoppedHash(bad);const uint32 live=p510WholeLiveHash();P525StoppedPrepared p;
    const bool refused=!prepareP525Stopped(bad,p)&&p.empty()&&p510WholeLiveHash()==live;
    debug("P525 terminal wrong frame refusal: frame%u refused%d",frame,int(refused));ok=refused&&ok;
   }
   Common::Array<uint32>low=w;low[9]=low[13]*1000/30-1;low.back()=p525StoppedHash(low);
   ok=installP525StoppedMemory(low)&&ok;
   Common::Array<uint32>again;ok=captureP525Stopped(again,low[2])&&again==low&&ok;
   ok=testP525StoppedMemory(scriptClock())&&ok;
   debug("P525 terminal low-clock memory futures: %s",ok?"PASS":"FAIL");
  }
'''
 assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,extra+'\n'+anchor)
 return cpp,header
