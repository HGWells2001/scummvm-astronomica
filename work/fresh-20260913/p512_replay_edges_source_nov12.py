"""Check midrange, stopped-end and active-end classification using original movie tracks."""
PROBE = r'''
 if(ConfMan.hasKey("astronomica_verify_p512_replay_edges")&&ConfMan.getBool("astronomica_verify_p512_replay_edges")){
  for(const char*key:{"astronomica_audio","astronomica_animation","astronomica_sprite_input"})ConfMan.setBool(key,true);
  ConfMan.setBool("astronomica_entry_scripts",false);
  bool ok=loadPlace(512,false,true)&&_movie;uint cells=0;
  auto originalPlay=[&](){if(_scene.sprites.size()<14||_scene.sprites[13].click.size()<6)return false;Script one;one.push_back(_scene.sprites[13].click[5]);const uint32 now=scriptClock();if(!_runner.enqueue(one,now,true))return false;runScriptsAt(now);return true;};
  for(uint range=0;range<6&&ok;++range){
   auto*decoder=static_cast<P512StoppedDecoder*>(_movie);const uint32 start=kP512Starts[range],end=kP512Ends[range],endMs=uint32(Audio::Timestamp(0,end,30).msecs());
   decoder->stop();_moviePlaying=false;decoder->setEndTime(Audio::Timestamp(0,end,30));_movieSegmentStart=start;
   ok=decoder->seek(Audio::Timestamp(0,start,30))&&decoder->decodeNextFrame()&&ok;
   const uint midSeeks=_p512OriginalSeekSerial;
   ok=!decoder->stoppedAtSegmentEnd()&&originalPlay()&&_p512OriginalSeekSerial==midSeeks&&decoder->isPlaying()&&ok;
   decoder->stop();_moviePlaying=false;
   ok=decoder->seek(Audio::Timestamp(0,end-1,30))&&decoder->decodeNextFrame()&&ok;
   decoder->retainStoppedClock(endMs-8);
   const uint endedSeeks=_p512OriginalSeekSerial;
   ok=decoder->stoppedAtSegmentEnd()&&originalPlay()&&_p512OriginalSeekSerial==endedSeeks+1&&decoder->isPlaying()&&decoder->getTime()<endMs&&ok;
   decoder->stop();_moviePlaying=false;
   ok=decoder->seek(Audio::Timestamp(0,end-1,30))&&decoder->decodeNextFrame()&&ok;
   decoder->retainStoppedClock(endMs-500);decoder->start();_moviePlaying=true;
   ok=!decoder->stoppedAtSegmentEnd()&&ok;
   decoder->stop();_moviePlaying=false;
   cells+=3;debug("P512 replay range edges: %s (range%u,start%u,end%u,midrange no seek,stopped end seeks,active end not classified)",ok?"PASS":"FAIL",range,start,end);
  }
  debug("P512 replay edge native: %s (%u cells)",ok&&cells==18?"PASS":"FAIL",cells);_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''


def inject(cpp, script):
    anchor = ' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }'
    assert cpp.count(anchor) == 1
    return cpp.replace(anchor, anchor + '\n' + PROBE), script
