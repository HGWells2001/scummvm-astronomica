from pathlib import Path
import shutil
p=Path('outputs/astronomica-cleanroom/engine/astronomica/script.cpp');s=p.read_text();needle=' return !vm.enqueue(loop, 0, true);';assert needle in s;s=s.replace(needle,''' if (vm.enqueue(loop,0,true)) return false;
 Common::Array<bool> sounds; sounds.resize(900);
 for (uint i = 0; i < sounds.size(); ++i) sounds[i] = true;
 vm.setSoundTargets(sounds);
 const int rawIds[] = {1,2,9,900};
 for (uint opcodeIndex = 0; opcodeIndex < 2; ++opcodeIndex) {
  for (uint i = 0; i < ARRAYSIZE(rawIds); ++i) {
   Script soundScript; Command sound; sound.opcode = opcodeIndex ? 27 : 9;
   sound.args.push_back(rawIds[i]); soundScript.push_back(sound);
   if (!vm.start(soundScript,0) || !vm.popAction(action) || action.opcode != sound.opcode || action.value != rawIds[i]-1 || vm.popAction(action)) return false;
   soundScript[0].args[0] = 0; if (vm.start(soundScript,0)) return false;
   soundScript[0].args[0] = 901; if (vm.start(soundScript,0)) return false;
  }
 }
 return true;''');p.write_text(s);shutil.copy2(p,Path('work/fresh-20260913/scummvm/engines/astronomica')/p.name)
for file,old,new in [('verify_audio_reference.py','(2, 3, 6)','(1, 2, 5)'),('verify_loop_reference.py','(12,)','(11,)')]:
 p=Path('outputs/astronomica-cleanroom')/file;s=p.read_text().replace(old,new);p.write_text(s)
