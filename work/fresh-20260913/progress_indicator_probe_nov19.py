"""Verify actual backend pixels against original-instruction fixtures and old saved flags."""
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_progress_indicator")&&ConfMan.getBool("astronomica_verify_progress_indicator")){
  ConfMan.setBool("astronomica_audio",false);ConfMan.setBool("astronomica_entry_scripts",false);
  Common::File fixture;bool ok=fixture.open(Common::FSNode(ConfMan.getPath("astronomica_progress_fixture")));
  char magic[8];if(ok)ok=fixture.read(magic,8)==8&&!memcmp(magic,"PSCR0001",8);const uint count=ok?fixture.readUint32LE():0;ok=ok&&count==212;
  uint hostPassed=0,rgb565Passed=0,oldPassed=0;bool payload=true;
  auto agrees=[&](const Graphics::Surface&surface,const Common::Array<Common::Rect>&rects,bool overlay,bool absolute){
   const uint32 base=surface.format.RGBToColor(34,68,102),white=surface.format.RGBToColor(255,255,255);
   for(int y=0;y<4;++y)for(int x=0;x<160;++x){bool marked=false;for(const Common::Rect&r:rects)marked=marked||r.contains(x+16,y+327);const uint32 expected=overlay&&marked?white:base;if(surface.getPixel(x+(absolute?16:0),y+(absolute?327:0))!=expected)return false;}return true;
  };
  for(uint row=0;ok&&row<count;++row){
   const uint kind=fixture.readUint32LE(),scene=fixture.readUint32LE(),counter=fixture.readUint32LE();int32 values[100];for(int i=0;i<100;++i)values[i]=fixture.readSint32LE();const uint n=fixture.readUint32LE();ok=n>=26&&n<=27&&(kind==0||kind==1)&&scene==103&&ok;Common::Array<Common::Rect>rects;
   for(uint i=0;ok&&i<n;++i){const int16 l=fixture.readSint16LE(),t=fixture.readSint16LE(),r=fixture.readSint16LE(),b=fixture.readSint16LE();ok=l>=16&&r<=176&&t>=327&&b<=331&&l<r&&t<b;rects.push_back(Common::Rect(l,t,r,b));}
   if(!ok)break;
   _runner.resetGlobals();_puzzlesCompleted=counter;
   if(kind==0){for(int i=0;i<100;++i)_runner.defineValue(0,i,values[i]);ok=loadPlace(103)&&ok;}
   else{ok=loadPlace(103)&&ok;Common::File old;ok=old.open(Common::FSNode(ConfMan.getPath("savepath").join("astro-verify.097")))&&ok;if(ok)ok=loadGameStream(&old).getCode()==Common::kNoError;oldPassed+=ok;}
   for(int i=0;i<100;++i){int32 v=0;ok=_runner.getValue(0,i,v)&&v==values[i]&&ok;}ok=_puzzlesCompleted==counter&&ok;
   _screen.fillRect(Common::Rect(16,327,176,331),_screen.format.RGBToColor(34,68,102));const uint32 before=screenRGBHash(_screen);presentScene();
   Graphics::Surface*host=_system->lockScreen();const bool hostOK=host&&host->format==_screen.format&&agrees(*host,rects,true,true);_system->unlockScreen();ok=hostOK&&screenRGBHash(_screen)==before&&ok;hostPassed+=hostOK;
   Graphics::Surface band;band.create(160,4,Graphics::PixelFormat(2,5,6,5,0,11,5,0,0));band.fillRect(Common::Rect(160,4),band.format.RGBToColor(34,68,102));composePuzzleProgress(band,_runner);const bool rgb565OK=agrees(band,rects,true,false);band.free();rgb565Passed+=rgb565OK;ok=rgb565OK&&ok;
   if(kind==1){Common::MemoryWriteStreamDynamic saved(DisposeAfterUse::YES);payload=saveGameStream(&saved).getCode()==Common::kNoError;Common::MemoryReadStream input(saved.getData(),saved.size());payload=input.readUint32BE()==MKTAG('A','S','V','M')&&input.readUint32LE()==2&&input.readUint32LE()==103&&input.readUint32LE()==counter&&payload;for(int i=0;i<100;++i)payload=input.readSint32LE()==values[i]&&payload;ok=payload&&ok;}
   debug("Progress pixels row: case%u kind%u marks%u host%d rgb565%d buffers%d",row,kind,n,int(hostOK),int(rgb565OK),int(screenRGBHash(_screen)==before));
  }
  bool excluded=true;for(int place:{1,126}){excluded=loadPlace(place)&&excluded;for(int i=20;i<=46;++i)_runner.defineValue(0,i,1);_screen.fillRect(Common::Rect(16,327,176,331),_screen.format.RGBToColor(34,68,102));const uint32 before=screenRGBHash(_screen);presentScene();Graphics::Surface*host=_system->lockScreen();Common::Array<Common::Rect>none;excluded=host&&agrees(*host,none,false,true)&&screenRGBHash(_screen)==before&&excluded;_system->unlockScreen();}
  ok=hostPassed==212&&rgb565Passed==212&&oldPassed==1&&payload&&excluded&&ok;
  debug("Progress pixels complete: %s (host%u,rgb565%u,old%u,payload%d,excluded%d)",ok?"PASS":"FAIL",hostPassed,rgb565Passed,oldPassed,int(payload),int(excluded));_background.free();_screen.free();quitGame();return ok?Common::kNoError:Common::Error(Common::kReadingFailed,"Progress pixels verification failed");
 }
'''
def observe(cpp,header):
    from progress_indicator_source_nov19 import production
    cpp,header=production(cpp,header)
    anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")';assert cpp.count(anchor)==1
    return cpp.replace(anchor,PROBE+'\n'+anchor),header
