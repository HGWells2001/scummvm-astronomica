from pathlib import Path
import shutil
p=Path('outputs/astronomica-cleanroom/engine/astronomica')
f=p/'script.h';s=f.read_text();s='\n'.join(l for l in s.split('\n') if 'setMissingSoundTarget' not in l and '_missingSoundTarget' not in l);f.write_text(s)
f=p/'script.cpp';s=f.read_text().replace(' _missingSoundTarget = -1;\n','');s=s.replace('  if ((c.opcode == 9 || c.opcode == 27) && !(c.opcode == 9 && c.args[0] == _missingSoundTarget) && (uint(c.args[0]) >= _soundTargets.size() || !_soundTargets[c.args[0]])) return false;', '''  if (c.opcode == 9 || c.opcode == 27) {
   // _read_command_mem 9:30b0-30d8 decrements the serialized sound id.
   const uint fileId = uint(c.args[0] - 1);
   if (fileId >= _soundTargets.size() || !_soundTargets[fileId]) return false;
  }''');s=s.replace('if (c.args.size() != 1 || c.args[0] < 0 || c.args[0] >= 900) return false;', 'if (c.args.size() != 1 || c.args[0] < 1 || c.args[0] > 900) return false;');s=s.replace('   if (c.opcode == 15) action.x', '   if (c.opcode == 9 || c.opcode == 27) --action.value;\n   if (c.opcode == 15) action.x');f.write_text(s)
f=p/'astronomica.cpp';s=f.read_text();a=s.index(' // The supplied P508 scripts request S9');b=s.index(' _runner.setSoundTargets(targets);',a);s=s[:a]+s[b:];a=s.index(' if (!stream) {',s.index('bool AstronomicaEngine::playSound'));b=s.index(' // sndPlaySound',a);s=s[:a]+' if (!stream) return false;\n'+s[b:];s=s.replace('{2,3627,0x1c898683U}, {3,4272,0xeed1c407U}, {6,23808,0x01fbde02U}', '{1,127488,0x6f7731d2U}, {2,3627,0x1c898683U}, {5,19516,0x0ad041f8U}')
# Correct expectations for serialized P510 commands, without altering direct internal calls.
a=s.index('  bool audioOK =');b=s.index('  bool bitOK',a) if '  bool bitOK' in s[a:] else s.index('  bool stopOK',a)
piece=s[a:b]
import re
piece=re.sub(r'_lastSound == ([23456])\b',lambda m:'_lastSound == '+str(int(m[1])-1),piece)
s=s[:a]+piece+s[b:]
a=s.index('  bool loopOK =');b=s.index('  scriptsOK = loopOK && scriptsOK;',a)
piece=s[a:b].replace('openSound(12)', 'openSound(11)').replace('3705','56541').replace('1834','28252').replace('3668','56504').replace('0xad03e6daU','0x0d45829aU').replace('_lastSound == 12','_lastSound == 11').replace('_loopSound == 12','_loopSound == 11').replace('fg.args.push_back(2)', 'fg.args.push_back(3)').replace('S12 PCM wrap', 'serialized 12 -> S11 PCM wrap');s=s[:a]+piece+s[b:]
s=s.replace('   Script missingLoop; Command missingLoopCommand; missingLoopCommand.opcode = 27; missingLoopCommand.args.push_back(9); missingLoop.push_back(missingLoopCommand);\n   answersOK = !_runner.canRun(missingLoop,true) && answersOK;', '''   Script correctSound; Command correctSoundCommand; correctSoundCommand.opcode = 9; correctSoundCommand.args.push_back(9); correctSound.push_back(correctSoundCommand);
   const uint beforeCorrectSound = _soundsStarted;
   answersOK = _runner.start(correctSound,0,true) && answersOK; applyScriptActions(0);
   answersOK = _lastSound == 8 && _soundsStarted == beforeCorrectSound+1 && answersOK;
   _mixer->stopHandle(_soundHandle);''');f.write_text(s)
for f in p.iterdir():
 if f.is_file(): shutil.copy2(f,Path('work/fresh-20260913/scummvm/engines/astronomica')/f.name)
