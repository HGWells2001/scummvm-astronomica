"""Keep original P513 numeric image-selector feedback over the existing Music owner."""
from pathlib import Path
import hashlib,sys
PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_p513_control_music")&&ConfMan.getBool("astronomica_verify_p513_control_music")){
  ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",false);uint matches=0;
  for(int index:{6,7}){
   _runner.resetGlobals();const bool loaded=loadPlace(513);_runner.enqueueStartup(_scene.scripts,scriptClock(),true);
   const uint32 entry=_system->getMillis();while(_system->getMillis()-entry<500){runScripts();animateSpritesAt(scriptClock());_system->delayMillis(2);}
   _runner.defineValue(1,0,5);_loopSound=0;_loopEnabled=true;const bool started=playSound(0,scriptClock(),true);const Audio::SoundHandle musicOwner=_musicHandle;
   const Sprite&button=_scene.sprites[index];const int x=button.renderX+1,y=button.renderY+1;const bool hit=spriteAt(x,y)==index;
   const uint before=_soundsStarted;clickAtTime(x,y,scriptClock());const uint32 began=_system->getMillis();bool effect=false,heard=false;
   while(_system->getMillis()-began<400){runScripts();animateSpritesAt(scriptClock());heard=heard||_lastSound==index+2;effect=effect||_mixer->isSoundHandleActive(_effectHandle);_system->delayMillis(2);}
   int32 setting=-1;_runner.getValue(1,0,setting);const bool music=_musicHandle==musicOwner&&_mixer->isSoundHandleActive(_musicHandle);
   const bool correct=loaded&&started&&hit&&heard&&setting==(index==6?6:4)&&effect&&music&&_soundsStarted==before+1&&!_runner.clicksBlocked();matches+=correct;
   debug("P513 numeric music observation: sprite%d loaded%d started%d hit%d sound%d setting%d effect%d music%d starts%u blocked%d",index+1,int(loaded),int(started),int(hit),int(heard),int(setting),int(effect),int(music),_soundsStarted-before,int(_runner.clicksBlocked()));
  }
  playSound(911,scriptClock());debug("P513 numeric narration foreground: %d",int(!_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_soundHandle)));
  debug("P513 numeric music complete: matches%u total2",matches);_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''
def observe(cpp,header):
 anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")';assert cpp.count(anchor)==1
 return cpp.replace(anchor,PROBE+'\n'+anchor),header
def production(cpp,header):
 w=Path(__file__).resolve().parent;sys.path.insert(0,str(w.parents[1]/'outputs/astronomica-cleanroom'))
 from astro_reader import parse
 root=Path('D:/astro');raw=(root/'PLACES/P513/MEGAFILE.HYP').read_bytes();assert hashlib.sha256(raw).hexdigest()=='ca2219d2a44dbed6f42ff2badccc87613941488c3a2f4ef7e62ff981395dbc87';scene=parse(raw)
 signatures=[]
 for index,clip,step,limit,cap,size,pin in ((6,8,1,10,9,3306,'1cc78cf15ee6af07862b53720fc75dd891d01a08d661cf5ba9d49d7d6405a74f'),(7,9,-1,0,1,3310,'c34e45b86f1a6d5a2b5137b3f95cf2385f51073392fc82e001197c80d414ba53')):
  commands=scene['sprites'][index]['click'];pattern=[28,9,46,31,32,45,31]+[20,49,20,49]+([45,31,20,49,20,49]*7)+[42,29]
  assert len(commands)==55 and [c['opcode']for c in commands]==pattern
  assert [c['args']for c in commands[:5]]==[[-1],[clip+1],[1,0,step],[1,0,limit,0,0,0],[1,0,cap]]
  assert commands[-1]['args']==[-1] and commands[-1]['delay']==200
  assert all(c['delay']==(-1 if c['opcode']in(42,45,49)else 200 if i==54 else 0)for i,c in enumerate(commands))
  data=(root/f'PLACES/P513/S{clip}.WAV').read_bytes();assert len(data)==size and hashlib.sha256(data).hexdigest()==pin;fnv=2166136261
  for byte in data:fnv=((fnv^byte)*16777619)&0xffffffff
  signatures.append((size,fnv))
 start=cpp.index('bool AstronomicaEngine::isFeedbackEffect(int id) const {');end=cpp.index('void AstronomicaEngine::synchronizeMusicHandle()',start);role=cpp[start:end]
 assert role.count('if(universeFileIdentity(')==9 and role.count(' return false;')==1
 role=role.replace(' return false;',''.join(f' if(universeFileIdentity(path,{size}U,0x{fnv:08x}U))return true;\n'for size,fnv in signatures)+' return false;')
 return observe(cpp[:start]+role+cpp[end:],header)
