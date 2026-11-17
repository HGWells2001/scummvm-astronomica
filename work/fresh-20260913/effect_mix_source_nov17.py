"""Extend feedback mixing to original short numeric-control sounds, with actual-click checks."""
from pathlib import Path
import hashlib,json
from effect_mix_source_nov16d import production as previous

CLICK_PROBE=r'''
  _runner.resetGlobals();ConfMan.setBool("astronomica_entry_scripts",true);
  ok=loadPlace(517)&&ok;
  const uint32 entry=_system->getMillis();
  while(_place==517&&!_mixer->isSoundHandleActive(_musicHandle)&&_system->getMillis()-entry<5000){
   runScripts();animateSpritesAt(scriptClock());resumeLoopAt(scriptClock());_system->delayMillis(5);
  }
  const Audio::SoundHandle controlMusic=_musicHandle;
  for(int action:{0,1}){
   const int x=319,y=action?369:420,wanted=action?5:4;bool seen=false;
   const bool hit=spriteAt(x,y)==wanted;clickAtTime(x,y,scriptClock());const uint32 began=_system->getMillis();
   while(_place==517&&_system->getMillis()-began<350){
    runScripts();animateSpritesAt(scriptClock());
    seen=seen||_mixer->isSoundHandleActive(_effectHandle);resumeLoopAt(scriptClock());_system->delayMillis(5);
   }
   const bool kept=hit&&seen&&_musicHandle==controlMusic&&_mixer->isSoundHandleActive(_musicHandle);
   debug("Effect mix original numeric control: %s (sprite%d,effectObserved%d)",kept?"PASS":"FAIL",wanted,int(seen));ok=kept&&ok;
  }
'''

def production(cpp,header):
 cpp,header=previous(cpp,header)
 w=Path(__file__).resolve().parent;inventory=json.loads((w/'control-effects-inventory-nov17.json').read_text())
 assert inventory['status']=='ORIGINAL_NUMERIC_CONTROL_EFFECT_INVENTORY_COMPLETE'
 signatures=set()
 for row in inventory['controls']:
  data=(Path('D:/astro')/row['audio_path']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['audio_sha256']
  signatures.add((row['bytes'],row['fnv1a']))
 assert len(signatures)==4
 start=cpp.index('bool AstronomicaEngine::isFeedbackEffect(int id) const {');end=cpp.index('void AstronomicaEngine::synchronizeMusicHandle()',start)
 role=cpp[start:end];assert role.count(' return false;')==1
 role=role.replace(' return false;',''.join(' if(universeFileIdentity(path,%uU,0x%08xU))return true;\n'%pair for pair in sorted(signatures))+' return false;')
 cpp=cpp[:start]+role+cpp[end:]
 anchor='  debug("Effect mix native result: %s",ok?"PASS":"FAIL");'
 assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,CLICK_PROBE+'\n'+anchor)
 return cpp,header
