"""Enable reconstructed gameplay by default,while preserving explicit configuration values."""
import re
KEYS=('astronomica_audio','astronomica_animation','astronomica_sprite_input','astronomica_entry_scripts')
VERIFIER=r'''
 if(ConfMan.hasKey("astronomica_verify_startup_defaults")&&ConfMan.getBool("astronomica_verify_startup_defaults")) {
  const char*keys[]={"astronomica_audio","astronomica_animation","astronomica_sprite_input","astronomica_entry_scripts"};uint observed=0,explicitMask=0;
  for(uint i=0;i<4;++i){if(ConfMan.hasKey(keys[i]))explicitMask|=1U<<i;if(!ConfMan.get(keys[i]).empty()&&ConfMan.getBool(keys[i]))observed|=1U<<i;}
  const uint expected=ConfMan.getInt("astronomica_expected_startup_mask"),expectedExplicit=ConfMan.getInt("astronomica_expected_explicit_mask");
  const uint initialPending=_runner.pendingCount();bool ok=_place==1&&observed==expected&&explicitMask==expectedExplicit;
  if(expected==15)ok=initialPending==1&&ok;else if(!expected)ok=!initialPending&&ok;
  debug("Startup defaults configuration: %s (observed%u,expected%u,explicit%u,expectedExplicit%u,P1pending%u)",ok?"PASS":"FAIL",observed,expected,explicitMask,expectedExplicit,initialPending);
  ok=loadPlace(27,false,true)&&!_scene.sprites.empty()&&ok;
  if(!_scene.sprites.empty()){
   const int selected=_scene.sprites[0].selectedFrame;ok=selected==((expected&2)?0:-1)&&ok;
   debug("Startup defaults animation: %s (P27sprite1frame%d)",selected==((expected&2)?0:-1)?"PASS":"FAIL",selected);
   Common::File file;bool geometry=file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P27/MEGAFILE.HYP")));
   const Frame*frame=geometry?staticSpriteFrame(_scene,0):nullptr;Graphics::Surface*bmp=frame?decodeSpriteBitmap(file,frame->image,_screen.format):nullptr;
   if(bmp){const int x=_scene.sprites[0].renderX+bmp->w/2,y=_scene.sprites[0].renderY+bmp->h/2;bmp->free();delete bmp;
    if(expected==15||!expected){const uint32 now=scriptClock();clickAtTime(x,y,now);runScriptsAt(now);const bool active=_runner.clicksBlocked()&&_runner.pendingCount();ok=active==bool(expected)&&ok;debug("Startup defaults actual input: %s (P27blocked%d,pending%u)",active==bool(expected)?"PASS":"FAIL",int(_runner.clicksBlocked()),_runner.pendingCount());}
   }else ok=false;
  }
  const int oldSound=_lastSound;const bool sound=playSound(1,scriptClock());ok=sound==bool(expected&1)&&ok;if(!sound)ok=_lastSound==oldSound&&ok;_mixer->stopHandle(_soundHandle);
  debug("Startup defaults actual audio: %s (S1played%d)",sound==bool(expected&1)?"PASS":"FAIL",int(sound));
  debug("Startup defaults native result: %s",ok?"PASS":"FAIL");_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def add_verifier(cpp):
 anchor=' if (!loadPlace(startPlace)) { _background.free(); _screen.free(); return Common::Error(Common::kReadingFailed, "Cannot read Astronomica starting scene"); }'
 assert cpp.count(anchor)==1;return cpp.replace(anchor,anchor+'\n'+VERIFIER)
def production(cpp,header):
 for key in KEYS:
  q=re.escape('"'+key+'"')
  cpp,n=re.subn(r'!ConfMan\.hasKey\('+q+r'\)\s*\|\|\s*!ConfMan\.getBool\('+q+r'\)',f'!ConfMan.getBool("{key}")',cpp)
  cpp,p=re.subn(r'ConfMan\.hasKey\('+q+r'\)\s*&&\s*ConfMan\.getBool\('+q+r'\)',f'ConfMan.getBool("{key}")',cpp)
  assert n+p>0 and f'ConfMan.hasKey("{key}")'not in cpp,key
 anchor='Common::Error AstronomicaEngine::run() {';assert cpp.count(anchor)==1
 defaults='\n // Gameplay works when added through the stock launcher with a fresh target.\n // ConfigManager::hasKey intentionally excludes the defaults domain;read the registered values.\n'+''.join(' ConfMan.registerDefault("'+key+'",true);\n'for key in KEYS)
 return add_verifier(cpp.replace(anchor,anchor+defaults)),header
def baseline(cpp,header):return add_verifier(cpp),header
