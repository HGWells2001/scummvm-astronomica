"""Classify the original P504 speed-step sound by its exact locked numeric-control script."""
from pathlib import Path
import hashlib,sys

PROBE=r'''
 if(ConfMan.hasKey("astronomica_verify_p504_control_music")&&ConfMan.getBool("astronomica_verify_p504_control_music")){
  _runner.resetGlobals();ConfMan.setBool("astronomica_audio",true);ConfMan.setBool("astronomica_entry_scripts",false);
  const bool loaded=loadPlace(504);_runner.enqueueStartup(_scene.scripts,scriptClock(),true);
  const uint32 entry=_system->getMillis();while(!_runner.scriptsIdle()&&_system->getMillis()-entry<2000){runScripts();animateSpritesAt(scriptClock());_system->delayMillis(2);}
  _runner.defineValue(1,1,0);_loopSound=0;_loopEnabled=true;
  const bool started=playSound(0,scriptClock(),true);const Audio::SoundHandle originalMusic=_musicHandle;
  const Sprite&button=_scene.sprites[9];const int x=button.renderX+15,y=button.renderY+10;
  const bool hit=spriteAt(x,y)==9;const uint before=_soundsStarted;clickAtTime(x,y,scriptClock());
  const uint32 began=_system->getMillis();bool effect=false,heard=false;
  while(_system->getMillis()-began<350){runScripts();animateSpritesAt(scriptClock());heard=heard||_lastSound==10;effect=effect||_mixer->isSoundHandleActive(_effectHandle);_system->delayMillis(2);}
  int32 setting=-1;_runner.getValue(1,1,setting);
  const bool music=_musicHandle==originalMusic&&_mixer->isSoundHandleActive(_musicHandle);
  debug("P504 speed music observation: loaded%d started%d hit%d sound%d setting%d effect%d music%d starts%u idle%d",int(loaded),int(started),int(hit),int(heard),int(setting),int(effect),int(music),_soundsStarted-before,int(_runner.scriptsIdle()));
  playSound(911,scriptClock());const bool voice=!_mixer->isSoundHandleActive(_musicHandle)&&_mixer->isSoundHandleActive(_soundHandle);
  debug("P504 speed narration foreground: %d",int(voice));_background.free();_screen.free();quitGame();return Common::kNoError;
 }
'''

def observe(cpp,header):
 anchor=' if(ConfMan.hasKey("astronomica_verify_blocking_voice_menu")';assert cpp.count(anchor)==1
 return cpp.replace(anchor,PROBE+'\n'+anchor),header

def production(cpp,header):
 w=Path(__file__).resolve().parent;sys.path.insert(0,str(w.parents[1]/'outputs/astronomica-cleanroom'))
 from astro_reader import parse,FormatError
 root=Path('D:/astro');raw=(root/'PLACES/P504/MEGAFILE.HYP').read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='dde86ef89aa520e16d006b41ddefece537f81901ad3e8db13c5a3bbe5e6009ba'
 try:scene=parse(raw)
 except FormatError as e:
  import re
  m=re.fullmatch(r'trailing (\d+) bytes at 0x([0-9a-f]+)',str(e));assert m and int(m[2],16)+int(m[1])==len(raw);scene=parse(raw[:int(m[2],16)])
 commands=scene['sprites'][9]['click']
 assert [c['opcode']for c in commands]==[28,9,46,31,32,42,23,41,29]
 assert [c['args']for c in commands]==[[-1],[11],[1,1,1],[1,1,16,0,0,0],[1,1,15],[],[8,0,0,0,0,0],[1],[-1]]
 assert [c['delay']for c in commands]==[0,0,0,0,0,-1,0,0,150]
 data=(root/'PLACES/P504/S10.WAV').read_bytes();assert len(data)==2064 and hashlib.sha256(data).hexdigest()=='10913e35074e459685caeda03486bc96c92a9202292b6dfa589b54391df429e3'
 fnv=2166136261
 for byte in data:fnv=((fnv^byte)*16777619)&0xffffffff
 start=cpp.index('bool AstronomicaEngine::isFeedbackEffect(int id) const {');end=cpp.index('void AstronomicaEngine::synchronizeMusicHandle()',start)
 role=cpp[start:end];assert role.count(' return false;')==1 and role.count('if(universeFileIdentity(')==8
 role=role.replace(' return false;',f' if(universeFileIdentity(path,2064U,0x{fnv:08x}U))return true;\n return false;')
 return observe(cpp[:start]+role+cpp[end:],header)
