"""Instrument real engine callbacks in an isolated verifier; no header changes."""
def inject(code):
 entry='bool AstronomicaEngine::verifyBuilderPuzzle() {';assert code.count(entry)==1
 probe=r'''
 if (ConfMan.hasKey("astronomica_verify_success_effects") && ConfMan.getBool("astronomica_verify_success_effects")) {
  Common::File reference;
  if (!reference.open(Common::FSNode(ConfMan.getPath("astronomica_success_effects_reference")))) return false;
  char magic[8];if(reference.read(magic,8)!=8 || memcmp(magic,"SCFX0001",8)) return false;
  const uint cases=reference.readUint32LE();if(!cases || cases>1000) return false;
  for(uint row=0;row<cases;++row) {
   const uint scene=reference.readUint32LE(),sourceOffset=reference.readUint32LE(),counter=reference.readUint32LE(),repeats=reference.readUint32LE();
   if(repeats!=2) return false;
   uint32 initial[100];for(uint i=0;i<100;++i) initial[i]=reference.readUint32LE();
   _runner.resetGlobals();if(!loadPlace(scene)) return false;
   for(uint i=0;i<100;++i)if(!_runner.defineValue(0,i,int32(initial[i]))) return false;
   _puzzlesCompleted=counter;
   for(uint repeat=0;repeat<repeats;++repeat) {
    const uint32 expectedCounter=reference.readUint32LE(),expectedVoices=reference.readUint32LE(),voiceCounter=reference.readUint32LE(),voiceHash=reference.readUint32LE();
    uint32 expected[100];for(uint i=0;i<100;++i) expected[i]=reference.readUint32LE();
    if(expectedVoices>1 || reference.err()) return false;
    debug("Custom effects begin: case%u repeat%u scene%u source%u expectedvoices%u voicecounter%u voicehash%08x",row,repeat,scene,sourceOffset,expectedVoices,voiceCounter,voiceHash);
    Script call;Command c;c.opcode=23;c.args.push_back(25);for(uint i=0;i<5;++i)c.args.push_back(0);c.delay=-1;call.push_back(c);
    const uint beforeSounds=_soundsStarted;
    if(!_runner.start(call,scriptClock(),true)) {debug("Custom effects admission: FAIL scene%u",scene);return false;}
    if(_puzzlesCompleted!=expectedCounter || _soundsStarted-beforeSounds!=expectedVoices || (expectedVoices && _lastSound!=912)) {
     debug("Custom effects counts: FAIL scene%u counter%u/%u voices%u/%u",scene,_puzzlesCompleted,expectedCounter,_soundsStarted-beforeSounds,expectedVoices);return false;
    }
    for(uint i=0;i<100;++i) {int32 v=0;if(!_runner.getValue(0,i,v) || uint32(v)!=expected[i]) {debug("Custom effects global: FAIL scene%u id%u",scene,i);return false;}}
    debug("Custom effects result: PASS case%u repeat%u scene%u counter%u voices%u",row,repeat,scene,_puzzlesCompleted,_soundsStarted-beforeSounds);
   }
  }
  if(reference.err() || reference.pos()!=reference.size()) return false;
  debug("Custom effects full native: PASS (%u cases,100 globals each,actual callbacks and voices)",cases);return loadPlace(103);
 }
'''
 code=code.replace(entry,entry+'\n'+probe)
 entry='uint32 AstronomicaEngine::onBlockingSound(int id, uint32 now) {';assert code.count(entry)==1
 hook=r'''
 if(id==912 && ConfMan.hasKey("astronomica_verify_success_effects") && ConfMan.getBool("astronomica_verify_success_effects")) {
  uint32 h=2166136261U;for(uint i=0;i<100;++i){int32 v=0;if(!_runner.getValue(0,i,v))error("Missing completion trace scalar");h=(h^uint32(v))*16777619U;}
  debug("Custom effects voice: counter%u hash%08x sound%d",_puzzlesCompleted,h,id);
 }
'''
 return code.replace(entry,entry+'\n'+hook)
