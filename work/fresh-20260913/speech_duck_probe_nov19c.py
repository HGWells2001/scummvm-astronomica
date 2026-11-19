from speech_duck_probe_nov19b import observe as previous

def observe(cpp,header):
 cpp,header=previous(cpp,header);start=cpp.index(' if(ConfMan.hasKey("astronomica_verify_speech_duck")');end=cpp.index(' if(ConfMan.hasKey("astronomica_verify_door_music")',start);block=cpp[start:end]
 block=block.replace('  bool scene=playSound(921,scriptClock())&&loadPlace(101,false,true);','  ConfMan.setBool("astronomica_entry_scripts",true);_runner.defineValue(0,60,0);\n  bool scene=playSound(921,scriptClock())&&loadPlace(101);')
 block=block.replace('loadPlace(219,false,true)','loadPlace(219)')
 block=block.replace('  all=scene&&all;debug("Speech duck scene transitions: %d",int(scene));','  all=scene&&all;debug("Speech duck scene transitions: %d",int(scene));ConfMan.setBool("astronomica_entry_scripts",false);')
 block=block.replace('  loadPlace(103,false,true);_loopSound=902;_loopEnabled=true;resumeLoopAt(scriptClock());Common::MemoryWriteStreamDynamic saved','  ConfMan.setBool("astronomica_entry_scripts",true);_runner.resetGlobals();loadPlace(103);_loopSound=902;_loopEnabled=true;resumeLoopAt(scriptClock());Common::MemoryWriteStreamDynamic saved')
 block=block.replace('  all=payload&&all;debug("Speech duck settled save/load: %d",int(payload));','  all=payload&&all;debug("Speech duck settled save/load: %d",int(payload));ConfMan.setBool("astronomica_entry_scripts",false);')
 return cpp[:start]+block+cpp[end:],header
