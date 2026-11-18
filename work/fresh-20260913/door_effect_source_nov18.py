"""Keep exact shared door responses over the current Music stream."""
from pathlib import Path
import json
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_door_music")&&ConfMan.getBool("astronomica_verify_door_music")){
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",true);uint passed=0;
  for(int place:{27,85}){
   _runner.resetGlobals();if(place==85)_runner.defineValue(0,53,1);const bool loaded=loadPlace(place);
   const uint32 warm=_system->getMillis();while(_system->getMillis()-warm<250){runScripts();animateSpritesAt(scriptClock());resumeLoopAt(scriptClock());_system->delayMillis(2);}
   const Audio::SoundHandle owner=_musicHandle;const uint32 elapsed=_mixer->getSoundElapsedTime(owner);const bool started=_mixer->isSoundHandleActive(owner);
   int x=587,y=246;bool hit=true;
   if(place==27){Common::File file;hit=file.open(Common::FSNode(ConfMan.getPath("path").join("PLACES/P27/MEGAFILE.HYP")));const Frame*f=hit?staticSpriteFrame(_scene,0):nullptr;Graphics::Surface*bmp=f?decodeSpriteBitmap(file,f->image,_screen.format):nullptr;if(bmp){x=_scene.sprites[0].renderX+bmp->w/2;y=_scene.sprites[0].renderY+bmp->h/2;bmp->free();delete bmp;hit=spriteAt(x,y)==0;}else hit=false;}
   const uint before=_soundsStarted;clickAtTime(x,y,scriptClock());bool heard=false,overlap=false,guard=false;const uint32 began=_system->getMillis();
   while(_system->getMillis()-began<800){runScripts();animateSpritesAt(scriptClock());resumeLoopAt(scriptClock());heard=heard||_lastSound==(place==27?905:907);const bool effect=_mixer->isSoundHandleActive(_effectHandle);overlap=overlap||(effect&&_mixer->isSoundHandleActive(_musicHandle)&&_musicHandle==owner);guard=guard||(effect&&!canSaveGameStateCurrently()&&!canLoadGameStateCurrently());_system->delayMillis(2);}
   int32 state=-1;_runner.getValue(1,0,state);const bool music=_mixer->isSoundHandleActive(_musicHandle)&&_musicHandle==owner;const bool advancing=music&&_mixer->getSoundElapsedTime(_musicHandle)>=elapsed+600;
   const bool correct=loaded&&started&&hit&&heard&&state==1&&overlap&&guard&&music&&advancing&&_soundsStarted==before+1;passed+=correct;
   debug("Door Music observation: place%d loaded%d started%d hit%d heard%d state%d overlap%d guard%d music%d advancing%d starts%u",place,int(loaded),int(started),int(hit),int(heard),int(state),int(overlap),int(guard),int(music),int(advancing),_soundsStarted-before);
   if(place==27){clickAtTime(x,y,scriptClock());runScripts();const bool destination=_place==32;const bool retained=_musicHandle==owner&&_mixer->isSoundHandleActive(_musicHandle);debug("Door Music traversal: destination%d retained%d",int(destination),int(retained));}
  }
  playSound(911,scriptClock());debug("Door Music narration foreground: %d",int(!_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_soundHandle)));
  debug("Door Music complete: passed%u total2",passed);_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def observe(cpp,header):
    anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")';assert cpp.count(anchor)==1
    return cpp.replace(anchor,PROBE+'\n'+anchor),header
def production(cpp,header):
    w=Path(__file__).resolve().parent;proof=json.loads((w/'door-effects-original-nov18.json').read_text());assert proof['status']=='ORIGINAL_SHARED_DOOR_EFFECTS_EVIDENCE_PASS'
    lines=[]
    for clip in proof['clips']:
        lines.append(' if(id==%d&&universeFileIdentity(ConfMan.getPath("path").join("SOUNDS/S%d.WAV"),%dU,0x%08xU))return true;'%(clip['id'],clip['id']-900,clip['bytes'],clip['fnv1a']))
    anchor='bool AstronomicaEngine::isFeedbackEffect(int id) const {\n';assert cpp.count(anchor)==1
    new=' if(id==905||id==907){\n  if(id==_scene.introSoundId||isBlockingSound(id))return false;\n'+'\n'.join(lines)+'\n  return false;\n }\n'
    return observe(cpp.replace(anchor,anchor+new),header)
